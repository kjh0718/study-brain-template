"""lecture-inbox 코어(`_system/tools/lecture-inbox/config.py` 등)의 검사.

  python test_core.py

시스템 Python으로 돈다(표준 라이브러리만 사용). 임시 폴더에만 쓰고 저장소에는 아무것도 쓰지 않는다.
종료 코드 0이면 문제 없음. FastAPI가 필요한 검사는 test_app.py(uv)에서 한다.
"""
import contextlib
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


GROUPS = [group_a]

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
