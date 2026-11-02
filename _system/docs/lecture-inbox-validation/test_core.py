"""lecture-inbox 코어(`_system/tools/lecture-inbox/config.py` 등)의 검사.

  python test_core.py

시스템 Python으로 돈다(표준 라이브러리만 사용). 임시 폴더에만 쓰고 저장소에는 아무것도 쓰지 않는다.
종료 코드 0이면 문제 없음. FastAPI가 필요한 검사는 test_app.py(uv)에서 한다.
"""
import contextlib
import datetime
import pathlib
import shutil
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOL = ROOT / "_system/tools/lecture-inbox"
sys.path.insert(0, str(TOOL))

results = []  # (그룹, 이름, PASS/FAIL, 메모)


def check(group, name, cond, note=""):
    results.append((group, name, "PASS" if cond else "FAIL", note))
    return bool(cond)


@contextlib.contextmanager
def tmpdir():
    d = tempfile.mkdtemp(prefix="lecture-inbox-test-")
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    except Exception:
        return False
    return False


META = {"course": "자료구조", "term": "2026-2", "ecampus_id": "12345", "code": "CSE2010", "section": "01", "created": "2026-11-02"}
_BASE = {"bundle": "20261102-자료구조", "kind": "transcript", "status": "done", "error": None, "week": 3, "session": 1,
         "date": "2026-10-20", "source": {"type": "ecampus", "lecture_id": "9", "title": "3주차 1차시"},
         "media": "a.mp4", "model": "large-v3", "repetitions": "01:02-01:10", "created": "2026-11-02T10:00:00"}
DONE_PRESENT = {**_BASE, "id": "t1", "filename": "week_03_01.md"}
DONE_MOVED = {**_BASE, "id": "t2", "filename": "week_03_02.md", "session": 2, "created": "2026-11-02T10:01:00"}
WAITING = {**_BASE, "id": "t3", "filename": "week_03_03.md", "session": 3, "status": "queued", "date": None,
           "model": None, "repetitions": None, "created": "2026-11-02T10:02:00"}
FAILED = {**_BASE, "id": "t4", "filename": "week_03_04.md", "session": 4, "status": "failed",
          "error": "영상 다운로드에 실패했습니다.", "created": "2026-11-02T10:03:00"}

# ---------------------------------------------------------------- 그룹

def group_a():
    import config
    with tmpdir() as t:
        p = config.Paths.at(pathlib.Path(t))
        check("A", "하위 폴더 생성", p.models.is_dir() and p.work.is_dir() and p.state_file.parent.is_dir())
        check("A", "settings 기본값", config.load_settings(p.settings_file) == {"model": "large-v3"} and p.settings_file.is_file())
        p.settings_file.write_text('{"model": "nope"}', encoding="utf-8")
        check("A", "모르는 모델 거절", raises(ValueError, config.load_settings, p.settings_file))
    check("A", "LECTURE_INBOX_HOME 우선", config.data_home({"LECTURE_INBOX_HOME": "X:/h", "LOCALAPPDATA": "Y:/"}) == pathlib.Path("X:/h"))
    check("A", "LOCALAPPDATA 기본", config.data_home({"LOCALAPPDATA": "Y:/a"}) == pathlib.Path("Y:/a/lecture-inbox"))
    check("A", "ROOT는 저장소 루트", (config.ROOT / "SECOND-BRAIN.md").is_file())
    check("A", "로컬 전용 바인드", config.HOST == "127.0.0.1")


def group_b():
    import bundle
    date = datetime.date
    check("B", "폴더 이름", bundle.bundle_dir_name("자료/구조", date(2026, 11, 2)) == "20261102-자료_구조")
    check("B", "예약 이름", bundle.safe_name("CON.pdf") == "_CON.pdf" and bundle.safe_name("a<b>.pdf") == "a_b_.pdf")
    check("B", "예약 이름 아님", bundle.safe_name("console.pdf") == "console.pdf" and bundle.safe_name("com10.pdf") == "com10.pdf")
    check("B", "전사 이름", bundle.transcript_name(3, 1) == "week_03_01.md")
    with tmpdir() as t:
        d = pathlib.Path(t)
        bundle.write_new_file(d / "x.pdf", b"one")
        check("B", "덮어쓰기 거절", raises(FileExistsError, bundle.write_new_file, d / "x.pdf", b"two") and (d / "x.pdf").read_bytes() == b"one")
        src = d / "src.bin"
        src.write_bytes(b"from-path")
        bundle.write_new_file(d / "y.bin", src)
        check("B", "Path 원본 복사", (d / "y.bin").read_bytes() == b"from-path")
        check("B", "partial 없음", not [p for p in d.iterdir() if p.name.endswith(".partial")])
        text = bundle.render_guide(META, [DONE_PRESENT, DONE_MOVED, WAITING, FAILED], present={"week_03_01.md"})
        check("B", "첫머리 문구", text.startswith("# 강의 수집 도구 안내\n\n이 파일은 강의 수집 도구"))
        check("B", "옮긴 완료 항목 제외", "### week_03_02.md" not in text and "### week_03_01.md" in text)
        check("B", "대기·실패 표시", "- 상태: 대기" in text and "- 상태: 실패 — 영상 다운로드에 실패했습니다." in text)
        check("B", "id 없으면 줄 없음", "이캠퍼스 과목 id" not in bundle.render_guide({**META, "ecampus_id": None}, [], set()))
        evil = {**WAITING, "source": {"type": "ecampus", "lecture_id": "1", "title": "제목\n### 가짜 항목"}}
        check("B", "줄바꿈 주입 무력화", "\n### 가짜" not in bundle.render_guide(META, [evil], set()))
        check("B", "수업일 미확인", "- 수업일: 미확인" in bundle.render_guide(META, [WAITING], set()))
        bundle.write_guide(d / "20261102-자료구조", META, [WAITING])
        check("B", "지운 묶음 다시 만듦", (d / "20261102-자료구조" / "안내.md").is_file())


GROUPS = [group_a, group_b]

for g in GROUPS:
    try:
        g()
    except Exception:
        tb = traceback.format_exc().strip().splitlines()
        check(g.__name__[-1].upper(), "그룹 실행", False, tb[-1])

print("=" * 68)
print("lecture-inbox core 검사")
print("=" * 68)
shown = None
for g, name, verdict, note in results:
    if g != shown:
        print(f"\n[{g}]")
        shown = g
    print(f"  {verdict}  {name}" + (f"   ({note})" if verdict == "FAIL" and note else ""))
fails = [r for r in results if r[2] == "FAIL"]
print(f"\nPASS {len(results) - len(fails)} / FAIL {len(fails)}")
sys.exit(1 if fails else 0)
