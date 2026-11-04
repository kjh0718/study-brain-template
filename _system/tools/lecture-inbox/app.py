"""lecture-inbox 로컬 API. 요청 본문·학번·비밀번호·서명된 URL은 로그와 오류 응답에 남기지 않는다."""
import contextlib
import datetime as dt
import json
import logging
import secrets
import shutil
import socket
import threading
import urllib.request
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi import Path as ApiPath
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, SecretStr

from bundle import bundle_dir_name, safe_name, transcript_name, write_new_file
from config import DEFAULT_DEVICE, HOST, MAX_MEDIA_BYTES, PORT, ROOT, Paths, data_home, load_settings
from hls import download_hls
from jobs import (DONE, DOWNLOAD_WAIT, FAILED, TRANSCRIBE_WAIT, ConflictError, StateError, Store, Worker, waiting_login)
from school import SchoolExpired, SchoolSession, UserError, split_course_name, suggest_week, to_term
from transcriber import WhisperEngine, load_audio as default_load_audio

log = logging.getLogger(__name__)

FFMPEG_MISSING = "ffmpeg가 없습니다. 터미널 안내대로 설치한 뒤 다시 시도해 주세요."
NOT_LOCAL = "로컬 화면에서만 사용할 수 있습니다."
INVALID = "입력 형식을 확인해 주세요."
NEED_PDF = "PDF만 받습니다. PPT·HWP·이미지는 PDF로 변환해 주세요."
SAVING = "업로드를 저장하는 중입니다."
DELETABLE = (DOWNLOAD_WAIT, TRANSCRIBE_WAIT, FAILED)

TERM = r"^[0-9]{4}-(1|2|summer|winter)$"  # \d는 전각 숫자도 받으므로 [0-9]를 쓴다
LECTURE_ID = r"^[0-9]{1,12}$"


class CourseBody(BaseModel):
    course: str = Field(min_length=1, max_length=100)
    term: str = Field(pattern=TERM)
    ecampusId: str | None = Field(default=None, pattern=LECTURE_ID)
    code: str | None = Field(default=None, max_length=30)
    section: str | None = Field(default=None, max_length=10)

    def meta(self) -> dict:
        return {"course": self.course, "term": self.term, "ecampus_id": self.ecampusId,
                "code": self.code, "section": self.section}


class LectureRow(BaseModel):
    id: str = Field(pattern=LECTURE_ID)
    title: str = Field(min_length=1, max_length=300)
    week: int = Field(ge=1, le=99)
    session: int = Field(ge=1, le=99)
    date: dt.date | None = None


class LecturesBody(BaseModel):
    course: CourseBody
    lectures: list[LectureRow] = Field(min_length=1)


class LoginBody(BaseModel):
    studentId: str = Field(pattern=r"^[0-9]{4,20}$")
    password: SecretStr = Field(min_length=1, max_length=512)


class UploadQuery(CourseBody):
    kind: Literal["recording", "resource", "past-exam", "assignment"]
    week: int | None = Field(default=None, ge=1, le=99)
    session: int | None = Field(default=None, ge=1, le=99)
    date: dt.date | None = None


def _ffmpeg() -> "str | None":
    try:
        import prereq  # Task 10. 아직 없으면 PATH에서 찾는다
    except ModuleNotFoundError:
        return shutil.which("ffmpeg")
    return prereq.ffmpeg_path()


def create_app(*, root: Path = ROOT, paths: "Paths | None" = None, school_factory=SchoolSession,
               engine_factory=None, load_audio=None, start_worker: bool = True,
               allowed_hosts: frozenset = frozenset({f"127.0.0.1:{PORT}", f"localhost:{PORT}"})) -> FastAPI:
    if not (root / "SECOND-BRAIN.md").is_file():
        raise RuntimeError(f"Study Brain 저장소 루트가 아닙니다: {root}")
    paths = paths or Paths.at(data_home())
    inbox = root / "inbox"

    def model() -> str:
        return load_settings(paths.settings_file)["model"]

    def device() -> str:
        return load_settings(paths.settings_file).get("device", DEFAULT_DEVICE)

    def default_engine(name: str):
        import prereq  # Task 10

        return WhisperEngine(prereq.ensure_model(name, paths.models), device())

    def download(stream: str, dest: Path) -> None:
        ffmpeg = _ffmpeg()
        if ffmpeg is None:
            raise UserError(FFMPEG_MISSING)
        download_hls(stream, dest, ffmpeg=ffmpeg)

    store = Store(paths.state_file)
    worker = Worker(store, inbox, paths.work, model=model, download=download,
                    engine_factory=engine_factory or default_engine, load_audio=load_audio or default_load_audio)
    register = threading.Lock()  # "이름이 비었는지 확인 → 항목 추가"를 한 덩어리로 묶는다

    @asynccontextmanager
    async def lifespan(_app):
        if start_worker:
            worker.start()
        yield

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store, app.state.worker = store, worker

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        # CORS 미들웨어가 없고 사용자 정의 헤더가 필요해서 다른 출처의 페이지는 /api를 부를 수 없다.
        if request.headers.get("host") not in allowed_hosts or (
                request.url.path.startswith("/api/") and request.headers.get("x-lecture-inbox") != "1"):
            response = JSONResponse({"detail": NOT_LOCAL}, status_code=403)
        else:
            response = await call_next(request)
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                 "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
                                 "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                                                            "style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'"})
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_input(_request, _error):
        return JSONResponse({"detail": INVALID}, status_code=422)  # 기본 오류는 입력(비밀번호)을 되풀이한다

    def guide(bundle: str) -> None:
        try:
            worker.refresh_guide(bundle)
        except Exception as e:
            log.error("안내.md를 쓰지 못했습니다: %s", type(e).__name__)

    def public(item: dict) -> dict:
        return {**{k: v for k, v in item.items() if k != "media"}, "progress": worker.progress.get(item["id"])}

    def need_school():
        school = worker.school
        if school is None:
            raise HTTPException(401, "학교에 로그인해 주세요.")
        return school

    def school_call(fn):
        school = need_school()
        try:
            return fn(school)
        except SchoolExpired as e:
            if worker.school is school:
                worker.school = None
            raise HTTPException(409, str(e)) from None
        except UserError as e:
            raise HTTPException(502, str(e)) from None

    @app.get("/")
    def index():
        return FileResponse(Path(__file__).with_name("index.html"))

    @app.get("/api/health")
    def health():
        return {"app": "lecture-inbox"}

    @app.get("/api/status")
    def status():
        try:
            model_name = model()
        except (ValueError, OSError):
            model_name = ""
        # 이미 올라간 엔진이 실제로 쓰는 장치가 우선이다. 없으면 설정값("auto"일 수 있다)
        loaded = getattr(worker._engine, "device", None)
        try:
            device_name = loaded or device()
        except (ValueError, OSError):
            device_name = ""
        items = store.all_items()
        return {"ffmpeg": _ffmpeg() is not None, "model": model_name, "device": device_name,
                "loggedIn": worker.school is not None,
                "waitingLogin": waiting_login(items), "items": [public(i) for i in items]}

    @app.post("/api/login")
    def login(body: LoginBody):
        school = school_factory()
        try:
            school.login(body.studentId, body.password.get_secret_value())
        except UserError as e:
            raise HTTPException(401, str(e)) from None
        worker.school = school
        worker.wake()
        return {"loggedIn": True}

    @app.post("/api/logout")
    def logout():
        worker.school = None
        return {"loggedIn": False}

    @app.get("/api/courses")
    def courses():
        found = school_call(lambda s: s.courses())
        out = []
        for c in found:
            name, code, section = split_course_name(c["name"])
            out.append({**c, "name": name, "code": code, "section": section, "term": to_term(c["year"], c["semester"])})
        return {"courses": out}

    @app.get("/api/courses/{course_id}/lectures")
    def lectures(course_id: Annotated[str, ApiPath(pattern=LECTURE_ID)]):
        found = school_call(lambda s: s.lectures(course_id))
        out = []
        for lecture in found:
            week, session = suggest_week(lecture["title"])
            out.append({**lecture, "week": week, "session": session})
        return {"lectures": out}

    @app.post("/api/lectures", status_code=202)
    def add_lectures(body: LecturesBody):
        bundle = bundle_dir_name(body.course.course, dt.date.today())
        names = [transcript_name(r.week, r.session) for r in body.lectures]
        if len(set(names)) != len(names):
            raise HTTPException(409, "같은 주차·차시가 요청 안에 중복되어 있습니다.")
        with register:
            try:
                store.add_bundle(bundle, body.course.meta())
            except ConflictError as e:
                raise HTTPException(409, str(e)) from None
            if set(names) & store.reserved_names(bundle, inbox / bundle):
                raise HTTPException(409, "같은 주차·차시의 파일이 이미 묶음에 있거나 대기 중입니다.")
            for r, name in zip(body.lectures, names):
                store.add_item(
                    kind="transcript", bundle=bundle, filename=name, status=DOWNLOAD_WAIT, error=None,
                    week=r.week, session=r.session, date=r.date.isoformat() if r.date else None,
                    source={"type": "ecampus", "lecture_id": r.id, "title": r.title})
        guide(bundle)
        worker.wake()
        return {"bundle": bundle, "count": len(names)}

    @app.post("/api/uploads", status_code=202)
    async def upload(request: Request, q: Annotated[UploadQuery, Query()]):
        recording = q.kind == "recording"
        if recording and (q.week is None or q.session is None):
            raise HTTPException(422, INVALID)
        raw_name = request.headers.get("x-filename")
        if not raw_name:
            raise HTTPException(400, "파일 이름이 없습니다.")
        name = safe_name(unquote(raw_name))
        if not recording and not name.lower().endswith(".pdf"):
            raise HTTPException(400, NEED_PDF)
        length = request.headers.get("content-length")
        if length is None:
            raise HTTPException(411, "파일 크기를 알 수 없습니다.")
        if not (length.isascii() and length.isdigit()):
            raise HTTPException(400, "잘못된 요청입니다.")
        if int(length) > MAX_MEDIA_BYTES:
            raise HTTPException(413, "파일이 너무 큽니다.")
        bundle = bundle_dir_name(q.course, dt.date.today())
        filename = transcript_name(q.week, q.session) if recording else name
        if filename in store.reserved_names(bundle, inbox / bundle):  # 본문을 받기 전에 걸러낸다
            raise HTTPException(409, "같은 이름의 파일이 이미 묶음에 있거나 대기 중입니다.")

        tmp = paths.work / f"up-{secrets.token_hex(6)}"
        try:
            tmp.mkdir(parents=True)
            size = 0
            with open(tmp / "upload.part", "wb") as f:
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > MAX_MEDIA_BYTES:
                        raise HTTPException(413, "파일이 너무 큽니다.")
                    f.write(chunk)
            await run_in_threadpool(finish_upload, q, bundle, filename, name, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)  # 녹음은 이미 work/<id>로 옮겨져 여기엔 남지 않는다
        guide(bundle)
        worker.wake()
        return {"bundle": bundle, "filename": filename}

    def finish_upload(q: UploadQuery, bundle: str, filename: str, name: str, tmp: Path) -> None:
        part, recording = tmp / "upload.part", q.kind == "recording"
        if not recording:
            with open(part, "rb") as f:
                if f.read(5) != b"%PDF-":
                    raise HTTPException(400, NEED_PDF)
        folder = inbox / bundle
        with register:
            try:
                store.add_bundle(bundle, q.meta())
            except ConflictError as e:
                raise HTTPException(409, str(e)) from None
            if filename in store.reserved_names(bundle, folder):
                raise HTTPException(409, "같은 이름의 파일이 이미 묶음에 있거나 대기 중입니다.")
            common = dict(bundle=bundle, filename=filename, source={"type": "upload", "name": name})
            if not recording:
                folder.mkdir(parents=True, exist_ok=True)
                try:
                    write_new_file(folder / filename, part)
                except FileExistsError:
                    raise HTTPException(409, "같은 이름의 파일이 이미 묶음에 있습니다.") from None
                store.add_item(kind=q.kind, status=DONE, error=None, **common)
                return
            # 작업 폴더 이름이 항목 id라서 항목을 먼저 만든다. 옮기는 동안은 워커가 집지 못하게 FAILED로 둔다.
            item = store.add_item(
                kind="transcript", status=FAILED, error=SAVING, week=q.week, session=q.session,
                date=q.date.isoformat() if q.date else None, **common)
            work = paths.work / item["id"]
            try:
                tmp.rename(work)
                (work / "upload.part").rename(work / name)
                if store.claim(item["id"], (FAILED,), status=TRANSCRIBE_WAIT, error=None, media=str(work / name)) is None:
                    raise HTTPException(409, "업로드 항목이 그 사이에 바뀌었습니다. 다시 올려 주세요.")
            except BaseException:
                with contextlib.suppress(KeyError):  # 그 사이 항목이 지워졌어도 폴더는 치워야 한다
                    store.remove(item["id"])
                shutil.rmtree(work, ignore_errors=True)
                raise

    def is_upload_placeholder(item: dict) -> bool:
        """옮기는 중인 업로드(FAILED, media 없음). 되살릴 파일이 없고 업로드 쪽이 정리를 맡는다."""
        return item["status"] == FAILED and item["source"]["type"] == "upload" and not item.get("media")

    def sweep_leftovers() -> None:
        """비정상 종료로 남은 업로드 임시 폴더와 자리표시자를 치운다. API로는 지울 수 없게 막아 둔 항목이다.
        워커가 시작되기 전, 서버가 하나뿐일 때만 부른다(main이 두 번째 서버를 막는다)."""
        for tmp in paths.work.glob("up-*"):
            shutil.rmtree(tmp, ignore_errors=True)
        touched = set()
        for item in store.all_items():
            if is_upload_placeholder(item):
                with contextlib.suppress(KeyError):
                    store.remove(item["id"])
                shutil.rmtree(paths.work / item["id"], ignore_errors=True)
                touched.add(item["bundle"])
        for bundle in touched:
            guide(bundle)

    @app.post("/api/items/{item_id}/retry")
    def retry(item_id: str):
        try:
            item = store.find(item_id)
        except KeyError:
            raise HTTPException(404, "항목을 찾을 수 없습니다.") from None
        if is_upload_placeholder(item):
            raise HTTPException(409, "올리던 도중 멈춘 항목입니다. 지우고 다시 올려 주세요.")  # 되살릴 파일이 없다
        target = TRANSCRIBE_WAIT if item.get("media") else DOWNLOAD_WAIT
        item = store.claim(item_id, (FAILED,), status=target, error=None)
        if item is None:
            raise HTTPException(409, "실패한 항목만 다시 시도할 수 있습니다.")
        guide(item["bundle"])
        worker.wake()
        return public(item)

    @app.delete("/api/items/{item_id}")
    def delete(item_id: str):
        try:
            item = store.find(item_id)
        except KeyError:
            raise HTTPException(404, "항목을 찾을 수 없습니다.") from None
        if item["status"] not in DELETABLE or is_upload_placeholder(item):
            raise HTTPException(409, "진행 중이거나 끝난 항목은 지울 수 없습니다.")
        try:
            removed = store.remove(item_id, DELETABLE)  # 확인과 삭제를 한 번에 해야 워커가 집은 항목을 지우지 않는다
        except KeyError:
            raise HTTPException(404, "항목을 찾을 수 없습니다.") from None
        if removed is None:
            raise HTTPException(409, "진행 중이거나 끝난 항목은 지울 수 없습니다.")
        shutil.rmtree(paths.work / item_id, ignore_errors=True)  # 파일이 잠겨 있으면 워커가 _Gone에서 다시 지운다
        guide(item["bundle"])
        return {"deleted": item_id}

    sweep_leftovers()
    return app


def _is_ours(host: str, port: int) -> "bool | None":
    """True면 이미 떠 있는 lecture-inbox, False면 다른 프로그램이 쓰는 포트, None이면 비어 있음."""
    try:
        req = urllib.request.Request(f"http://{host}:{port}/api/health", headers={"X-Lecture-Inbox": "1"})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=2) as r:  # 프록시를 거치지 않는다
            return json.load(r) == {"app": "lecture-inbox"}
    except (OSError, ValueError):  # HTTPError·URLError·소켓 오류는 OSError, 깨진 JSON은 ValueError
        pass
    try:
        socket.create_connection((host, port), timeout=1).close()
    except OSError:
        return None
    return False


def _claim_port(host: str, port: int) -> "tuple[socket.socket | None, bool | None]":
    """포트를 먼저 독점해서 잡는다. 확인과 실행 사이에 다른 실행이 끼어들 틈이 없게 하려는 것이다.
    잡았으면 (소켓, None). 못 잡았으면 (None, 이미 떠 있는 lecture-inbox인지)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):  # Windows: 다른 프로세스가 같은 포트에 겹쳐 바인드하지 못하게 한다
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    try:
        sock.bind((host, port))
    except OSError:
        sock.close()
        return None, _is_ours(host, port)
    return sock, None


def main(argv: "list[str] | None" = None) -> int:
    url = f"http://{HOST}:{PORT}/"
    sock, ours = _claim_port(HOST, PORT)
    if sock is None:
        if ours:  # 같은 상태 파일을 쓰는 두 번째 워커를 만들지 않는다
            webbrowser.open(url)
            return 0
        print(f"포트 {PORT}를 쓸 수 없습니다. 다른 프로그램이 쓰고 있거나 다른 창이 아직 시작하는 중입니다. "
              "잠시 뒤 다시 실행하거나 그 프로그램을 끄고 다시 실행해 주세요.")
        return 1
    import prereq
    import uvicorn

    try:
        if prereq.ffmpeg_path() is None:
            prereq.offer_ffmpeg_install()  # 거절해도 계속한다. 업로드 전사는 ffmpeg 없이 된다
        try:
            paths = Paths.at(data_home())
            load_settings(paths.settings_file)
            app = create_app(paths=paths)
        except (ValueError, OSError, StateError) as e:
            print(f"시작하지 못했습니다: {e}")
            return 1
        threading.Timer(1.5, webbrowser.open, [url]).start()
        # access_log=False: 요청 경로·쿼리에 과목명이 들어가므로 접근 로그를 남기지 않는다
        uvicorn.Server(uvicorn.Config(app, log_level="info", access_log=False)).run(sockets=[sock])
        return 0
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
