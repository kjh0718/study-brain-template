"""작업 상태 저장, 다음 작업 선택, 백그라운드 워커, 절전 방지. fastapi·numpy를 import하지 않는다."""
import json
import logging
import os
import secrets
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence

from bundle import GUIDE_LOCK, write_guide, write_new_file
from school import SchoolExpired, UserError
from transcript import to_markdown
from transcriber import transcribe

log = logging.getLogger(__name__)

DOWNLOAD_WAIT = "download-wait"
DOWNLOADING = "downloading"
TRANSCRIBE_WAIT = "transcribe-wait"
TRANSCRIBING = "transcribing"
DONE = "done"
FAILED = "failed"

NO_SPEECH = "인식된 음성이 없습니다. 녹음 파일을 확인해 주세요."
NAME_TAKEN = "같은 이름의 파일이 이미 묶음에 있습니다."
GENERIC_ERROR = "작업 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요."

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001  # 화면 꺼짐(ES_DISPLAY_REQUIRED)은 막지 않는다


class StateError(Exception):
    pass


class ConflictError(Exception):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.bundles: dict[str, dict] = {}
        self.items: list[dict] = []
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.bundles, self.items = dict(data["bundles"]), list(data["items"])
        except (ValueError, KeyError, TypeError) as e:  # 깨진 파일은 덮어쓰지 않고 거부한다
            raise StateError(f"상태 파일을 읽을 수 없습니다: {path}") from e
        back = {DOWNLOADING: DOWNLOAD_WAIT, TRANSCRIBING: TRANSCRIBE_WAIT}
        for item in self.items:
            item["status"] = back.get(item["status"], item["status"])

    def _write(self) -> None:
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            tmp.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"version": 1, "bundles": self.bundles, "items": self.items}, f, ensure_ascii=False, indent=1)
                f.flush()
                os.fsync(f.fileno())  # 정전으로 빈 jobs.json이 남지 않게 디스크에 내린 뒤 바꾼다
            os.replace(tmp, self.path)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise

    def save(self) -> None:
        with self.lock:
            self._write()

    def add_bundle(self, name: str, meta: dict) -> None:
        with self.lock:
            old = self.bundles.get(name)
            if old is not None:
                if any(old.get(k) != meta.get(k) for k in ("course", "term", "ecampus_id")):
                    raise ConflictError(f"같은 이름의 묶음이 다른 과목·학기로 이미 있습니다: {name}")
                return
            self.bundles[name] = meta
            self._write()

    def add_item(self, **fields) -> dict:
        item = {**fields, "id": secrets.token_hex(6), "created": datetime.now().isoformat()}
        with self.lock:
            self.items.append(item)
            self._write()
            return dict(item)

    def _get(self, item_id: str) -> dict:
        for item in self.items:
            if item["id"] == item_id:
                return item
        raise KeyError(item_id)

    def find(self, item_id: str) -> dict:
        with self.lock:
            return dict(self._get(item_id))

    def update(self, item_id: str, **fields) -> dict:
        with self.lock:
            item = self._get(item_id)
            item.update(fields)
            self._write()
            return dict(item)

    def claim(self, item_id: str, from_statuses: "set[str] | tuple[str, ...]", **fields) -> "dict | None":
        """현재 상태가 from_statuses일 때만 바꾼다. 항목이 없거나 상태가 달라졌으면 None."""
        with self.lock:
            for item in self.items:
                if item["id"] == item_id:
                    if item["status"] not in from_statuses:
                        return None
                    item.update(fields)
                    self._write()
                    return dict(item)
            return None

    def remove(self, item_id: str) -> dict:
        with self.lock:
            item = self._get(item_id)
            self.items.remove(item)
            self._write()
            return dict(item)

    def all_items(self) -> list[dict]:
        with self.lock:
            return [dict(i) for i in self.items]

    def items_in(self, bundle: str) -> list[dict]:
        with self.lock:
            return [dict(i) for i in self.items if i["bundle"] == bundle]

    def reserved_names(self, bundle: str, folder: Path) -> set[str]:
        with self.lock:
            names = {i["filename"] for i in self.items if i["bundle"] == bundle and i["status"] != DONE}
        if folder.is_dir():
            names |= {p.name for p in folder.iterdir()}
        return names


def next_item(items: list[dict], logged_in: bool) -> "dict | None":
    order = (DOWNLOAD_WAIT, TRANSCRIBE_WAIT) if logged_in else (TRANSCRIBE_WAIT,)
    for status in order:
        waiting = [i for i in items if i["status"] == status]
        if waiting:
            return min(waiting, key=lambda i: i["created"])  # min은 동률이면 앞쪽을 돌려준다
    return None


def waiting_login(items: list[dict]) -> int:
    return sum(1 for i in items if i["status"] == DOWNLOAD_WAIT)


def keep_awake(active: bool, set_state: "Callable[[int], int] | None" = None) -> None:
    """실행 상태는 스레드별로 적용되므로 반드시 워커 스레드에서 부른다."""
    if set_state is None:
        if sys.platform != "win32":
            return
        import ctypes

        def set_state(flags):
            return ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint32(flags))
    set_state(ES_CONTINUOUS | ES_SYSTEM_REQUIRED if active else ES_CONTINUOUS)


class _Gone(Exception):
    """작업 도중 항목이 지워졌거나 상태가 바뀌어 더 진행하면 안 된다."""


class Worker:
    def __init__(self, store: Store, inbox: Path, work_root: Path, *, model: Callable[[], str],
                 download: Callable[[str, Path], None], engine_factory: Callable[[str], object],
                 load_audio: Callable[[Path], Sequence[float]], set_state=None):
        self.store, self.inbox, self.work_root = store, inbox, work_root
        self.model, self.download = model, download
        self.engine_factory, self.load_audio, self.set_state = engine_factory, load_audio, set_state
        self.school = None  # school.SchoolSession | None. 로그인하면 app이 채운다
        self.progress: dict[str, str] = {}
        self._engine, self._engine_model = None, None
        self._wake = threading.Event()

    def wake(self) -> None:
        self._wake.set()

    def start(self) -> None:
        threading.Thread(target=self._loop, name="lecture-inbox-worker", daemon=True).start()

    def _loop(self) -> None:
        while True:
            self._wake.clear()  # run_once 전에 지워야 그 사이의 wake()를 놓치지 않는다
            try:
                busy = self.run_once()
            except Exception as e:
                # 서명된 URL이 예외 문구에 섞일 수 있어 메시지·트레이스백은 남기지 않는다
                log.error("워커 루프 오류: %s", type(e).__name__)
                self._wake.wait(5)
                continue
            if not busy:
                self._wake.wait()

    def refresh_guide(self, bundle: str) -> None:
        """안내.md를 현재 상태로 다시 쓴다. 요청 스레드도 이 메서드를 써야 오래된 스냅샷이 나중에 덮어쓰지 않는다."""
        with GUIDE_LOCK:
            write_guide(self.inbox / bundle, self.store.bundles[bundle], self.store.items_in(bundle))

    def _guide(self, bundle: str) -> None:
        try:
            self.refresh_guide(bundle)
        except Exception:
            log.exception("안내.md를 쓰지 못했습니다")

    def _set(self, item_id: str, **fields) -> None:
        try:
            item = self.store.update(item_id, **fields)
        except KeyError:  # 작업 도중 사용자가 항목을 지웠다. 더 진행하지 않는다
            raise _Gone from None
        self._guide(item["bundle"])

    def _claim(self, item_id: str, from_status: str, **fields) -> None:
        """다음 작업으로 고른 뒤 다른 스레드가 항목을 지우거나 바꿨는지 원자적으로 확인하며 상태를 바꾼다."""
        item = self.store.claim(item_id, (from_status,), **fields)
        if item is None:
            raise _Gone
        self._guide(item["bundle"])

    def _forget(self, item: dict) -> None:
        # 항목이 정말 사라졌을 때만 작업 폴더를 지운다. 상태만 바뀐 경우는 다른 쪽이 쓰고 있을 수 있다.
        try:
            self.store.find(item["id"])
        except KeyError:
            shutil.rmtree(self.work_root / item["id"], ignore_errors=True)

    def run_once(self) -> bool:
        item = next_item(self.store.all_items(), self.school is not None)
        if item is None:
            keep_awake(False, self.set_state)
            return False
        keep_awake(True, self.set_state)
        try:
            if item["status"] == DOWNLOAD_WAIT:
                self._download(item)
            else:
                self._transcribe(item)
        except _Gone:
            self._forget(item)
        except Exception as e:
            # 서명된 URL이 예외 문구에 섞일 수 있어 종류만 남긴다(메시지·트레이스백 없음)
            log.error("작업 실패: %s (항목 %s)", type(e).__name__, item["id"][:4])
            try:
                self._set(item["id"], status=FAILED, error=GENERIC_ERROR)
            except _Gone:
                self._forget(item)
        finally:
            self.progress.pop(item["id"], None)
            keep_awake(False, self.set_state)
        return True

    def _download(self, item: dict) -> None:
        school = self.school  # 한 번만 읽는다: 도중에 로그아웃·재로그인이 일어날 수 있다
        if school is None:
            return  # 로그인 대기 상태 그대로 둔다
        self._claim(item["id"], DOWNLOAD_WAIT, status=DOWNLOADING, error=None)
        work = self.work_root / item["id"]
        try:
            stream, _ = school.stream(item["source"]["lecture_id"])
            work.mkdir(parents=True, exist_ok=True)
            self.download(stream, work / "video.mp4")
        except SchoolExpired:
            if self.school is school:  # 그 사이 새로 로그인했다면 그 세션은 지우지 않는다
                self.school = None
            self._set(item["id"], status=DOWNLOAD_WAIT)
        except UserError as e:
            self._set(item["id"], status=FAILED, error=str(e))
        else:
            self._set(item["id"], status=TRANSCRIBE_WAIT, media=str(work / "video.mp4"))

    def _transcribe(self, item: dict) -> None:
        item_id, work = item["id"], self.work_root / item["id"]
        model = item.get("model") or self.model()  # 이어서 할 때는 기록된 모델을 쓴다
        self._claim(item_id, TRANSCRIBE_WAIT, status=TRANSCRIBING, error=None, model=model)
        self.progress[item_id] = "모델 준비 중"
        if self._engine is None or self._engine_model != model:
            self._engine, self._engine_model = self.engine_factory(model), model
        audio = self.load_audio(Path(item["media"]))
        work.mkdir(parents=True, exist_ok=True)
        segments, unresolved = transcribe(
            audio, work, self._engine, lambda f: self.progress.__setitem__(item_id, f"전사 중 {int(f * 100)}%"))
        if not segments:
            self._set(item_id, status=FAILED, error=NO_SPEECH)  # work는 남긴다
            return
        try:
            self.store.find(item_id)  # 지워진 항목의 전사를 묶음에 만들지 않는다
        except KeyError:
            raise _Gone from None
        folder, data = self.inbox / item["bundle"], to_markdown(segments).encode("utf-8")
        dest, created = folder / item["filename"], True
        try:
            folder.mkdir(parents=True, exist_ok=True)
            write_new_file(dest, data)
        except FileExistsError:
            # 파일은 썼는데 DONE 기록 전에 멈췄다면 다시 시도했을 때 내용이 같다. 그 경우는 완료로 본다.
            if dest.read_bytes() != data:
                self._set(item_id, status=FAILED, error=NAME_TAKEN)  # 체크포인트는 남긴다
                return
            created = False
        try:
            self._set(item_id, status=DONE, error=None, repetitions=unresolved)
        except _Gone:
            if created:
                dest.unlink(missing_ok=True)
            raise
        shutil.rmtree(work, ignore_errors=True)  # 받은 영상·업로드 사본. 사용자 PC의 원본은 건드릴 수 없다
