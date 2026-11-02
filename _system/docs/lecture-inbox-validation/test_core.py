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
    long_ko = bundle.safe_name("가" * 45 + ".pdf")
    check("B", "긴 한글 이름 확장자 보존", long_ko.endswith(".pdf") and len(long_ko.encode("utf-8")) <= 120)
    tails = [bundle.safe_name(n) for n in ("a" * 119 + " b.pdf", "a" * 119 + ". b", "a" * 118 + " . x", "가" * 40 + " " * 5)]
    check("B", "끝에 공백·점 없음", all(n and not n.endswith((" ", ".")) for n in tails), repr(tails))
    check("B", "자른 뒤 예약 이름", bundle.safe_name("CON" + " " * 130 + ".pdf") == "_CON.pdf")
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


def group_c():
    import repetition
    import transcript
    S = transcript.Segment
    check("C", "hms", transcript.format_hms(3725.9) == "01:02:05")
    check("C", "md 형식", transcript.to_markdown([S(0, 1, "안녕"), S(65.2, 70, "둘")]) == "[00:00:00] 안녕\n[00:01:05] 둘\n")
    with tmpdir() as t:
        d = pathlib.Path(t)
        ck = d / "ck.jsonl"
        check("C", "없는 체크포인트", transcript.read_checkpoint(d / "none.jsonl") == [])
        for s in (S(0, 2, "가"), S(2, 4, "나")):
            transcript.append_checkpoint(ck, s)
        good = ck.read_bytes()
        with open(ck, "ab") as f:
            f.write(b'{"start": 4, "end"')  # 쓰다 끊긴 줄
        check("C", "잘린 줄 버림", transcript.read_checkpoint(ck) == [S(0, 2, "가"), S(2, 4, "나")])
        check("C", "잘린 줄 바이트 단위 truncate", ck.read_bytes() == good)
        transcript.append_checkpoint(ck, S(4, 6, "다"))
        check("C", "truncate 후 이어 쓰기", len(transcript.read_checkpoint(ck)) == 3)
        with open(ck, "ab") as f:
            f.write('{"start": 6, "end": 8, "text": "한'.encode("utf-8")[:-1])  # 한글 중간에서 끊김
        check("C", "멀티바이트 중간에서 끊겨도 버림", len(transcript.read_checkpoint(ck)) == 3)
        bad = d / "bad.jsonl"
        bad.write_bytes(good.replace(b'"end": 2', b'"end"', 1))
        check("C", "중간 줄 깨짐은 ValueError", raises(ValueError, transcript.read_checkpoint, bad))
        nonl = d / "nonl.jsonl"
        nonl.write_bytes(good.rstrip(b"\n"))  # 마지막 줄은 온전하지만 개행만 없음
        check("C", "개행 없는 온전한 줄 유지", transcript.read_checkpoint(nonl) == [S(0, 2, "가"), S(2, 4, "나")])
        transcript.append_checkpoint(nonl, S(4, 6, "다"))
        check("C", "개행 보충 후 이어 쓰기", len(transcript.read_checkpoint(nonl)) == 3)
    rep = [S(i, i + 1, "같은 말을 반복합니다") for i in range(3)]
    check("C", "반복 3회 탐지", repetition.find_repetition_span([S(-1, 0, "시작")] + rep) == (1, 3))
    check("C", "짧은 반복은 정상", repetition.find_repetition_span([S(i, i + 1, "네") for i in range(5)]) is None)
    check("C", "2회는 반복 아님", repetition.find_repetition_span(rep[:2]) is None)


def group_d():
    import transcriber
    from transcript import Segment as S, append_checkpoint, read_checkpoint
    SR = transcriber.SAMPLE_RATE

    class Fake:
        """script(call_index, offset) -> 상대 구간 목록. 호출마다 (len(audio), offset, options)를 기록한다."""
        def __init__(self, script):
            self.script, self.calls = script, []

        def segments(self, audio, offset, **options):
            i = len(self.calls)
            self.calls.append((len(audio), offset, options))
            return iter([S(offset + s.start, offset + s.end, s.text) for s in self.script(i, offset)])

    audio = [0.0] * (SR * 60)
    REP = "같은 말을 반복합니다"
    rep3 = lambda a: [S(a + k, a + k + 1, REP) for k in range(3)]

    def seeded(d, name, segs, marker=False):
        w = d / name
        w.mkdir()
        for s in segs:
            append_checkpoint(w / "segments.jsonl", s)
        if marker:
            (w / "decoded").touch()
        return w

    with tmpdir() as t:
        d = pathlib.Path(t)
        # D1 처음부터
        w = d / "w1"
        w.mkdir()
        e = Fake(lambda i, o: [S(0, 5, "하나"), S(5, 9, "둘"), S(9, 12, "셋")])
        progress = []
        segs, n = transcriber.transcribe(audio, w, e, progress.append)
        check("D", "처음부터 offset 0", e.calls[0][1] == 0.0 and e.calls[0][0] == len(audio))
        check("D", "체크포인트 3줄·마커", len(read_checkpoint(w / "segments.jsonl")) == 3 and (w / "decoded").exists())
        check("D", "기본 옵션 전달·진행률", e.calls[0][2] == transcriber.BASE_OPTIONS and progress[-1] == 12 / 60)
        # D2 이어하기: 끝 20.0까지 + 잘린 줄
        w2 = seeded(d, "w2", [S(0, 10, "하나"), S(10, 20, "둘")])
        with open(w2 / "segments.jsonl", "ab") as f:
            f.write(b'{"start": 20, "end"')
        e2 = Fake(lambda i, o: [S(0, 4, "넷")])
        segs, _ = transcriber.transcribe(audio, w2, e2)
        check("D", "마지막 끝 시각부터", e2.calls[0][1] == 20.0 and e2.calls[0][0] == len(audio) - 20 * SR)
        check("D", "타임스탬프 원본 기준", segs[-1] == S(20.0, 24.0, "넷") and len(segs) == 3)
        # D3 decoded 마커가 있으면 디코딩 안 함
        w3 = seeded(d, "w3", [S(0, 10, "하나"), S(10, 20, "둘")], marker=True)
        e3 = Fake(lambda i, o: [S(0, 4, "넷")])
        segs3, _ = transcriber.transcribe(audio, w3, e3)
        check("D", "마커 있으면 재디코딩 없음", e3.calls == [] and len(segs3) == 2)
        # D4 이미 끝까지 됨
        w4 = seeded(d, "w4", [S(0, 59.5, "끝까지")])
        e4 = Fake(lambda i, o: [S(0, 1, "x")])
        transcriber.transcribe(audio, w4, e4)
        check("D", "남은 꼬리 1초 미만이면 호출 없음", e4.calls == [] and (w4 / "decoded").exists())
        # D5 반복 해결
        w5 = d / "w5"
        w5.mkdir()
        e5 = Fake(lambda i, o: [S(0, 9, "앞 문장입니다 여기")] + rep3(10) + [S(13, 14, "뒤 문장입니다 저기")] if i == 0
                  else [S(0.5, 2, "정상 하나입니다"), S(2, 4, "정상 둘입니다")])
        segs5, n5 = transcriber.transcribe(audio, w5, e5)
        check("D", "재시도 offset은 start-0.5", e5.calls[1][1] == 9.5 and e5.calls[1][0] == 4 * SR
              and n5 == 0 and not any(s.text.startswith(transcriber.REPETITION_MARK) for s in segs5))
        check("D", "재시도 옵션 병합", e5.calls[1][2] == {**transcriber.BASE_OPTIONS})
        check("D", "해결된 구간 교체", [s.text for s in segs5] == ["앞 문장입니다 여기", "정상 하나입니다", "정상 둘입니다", "뒤 문장입니다 저기"])
        # D6 반복 미해결 (재시도해도 계속 반복)
        w6 = d / "w6"
        w6.mkdir()
        e6 = Fake(lambda i, o: [S(0, 9, "앞 문장입니다 여기")] + rep3(10) if i == 0 else rep3(0.5))
        segs6, n6 = transcriber.transcribe(audio, w6, e6)
        check("D", "미해결 표시 한 줄", n6 == 1 and sum(s.text.startswith(transcriber.REPETITION_MARK) for s in segs6) == 1
              and len(e6.calls) == 1 + len(transcriber.RETRY_OPTIONS) and len(segs6) == 2)
        check("D", "재시도마다 옵션 병합", e6.calls[2][2] == {**transcriber.BASE_OPTIONS, **transcriber.RETRY_OPTIONS[1]})
        # D7 180초 넘는 반복
        long_audio = [0.0] * (SR * 400)
        w7 = d / "w7"
        w7.mkdir()
        e7 = Fake(lambda i, o: [S(10, 100, REP), S(100, 200, REP), S(200, 300, REP)])
        segs7, n7 = transcriber.transcribe(long_audio, w7, e7)
        check("D", "긴 구간은 재시도 없음", len(e7.calls) == 1 and n7 == 1 and len(segs7) == 1)

        # D8 재시도 예외는 다음 옵션으로
        def script8(i, o):
            if i == 1:
                raise RuntimeError("boom")
            return [S(0, 9, "앞 문장입니다 여기")] + rep3(10) if i == 0 else [S(0.5, 3, "정상으로 돌아왔습니다")]
        w8 = d / "w8"
        w8.mkdir()
        e8 = Fake(script8)
        segs8, n8 = transcriber.transcribe(audio, w8, e8)
        check("D", "재시도 예외 흡수", n8 == 0 and len(e8.calls) == 3 and segs8[-1].text == "정상으로 돌아왔습니다")
        # D9 offset 이전 구간은 버림
        w9 = seeded(d, "w9", [S(0, 10, "하나"), S(10, 20, "둘")])
        e9 = Fake(lambda i, o: [S(-1, 2, "과거"), S(-0.03, 2, "허용 오차"), S(2, 5, "정상")])
        segs9, _ = transcriber.transcribe(audio, w9, e9)
        check("D", "체크포인트 이전 시간 무시", len(segs9) == 4 and all(s.start >= 19.95 for s in segs9[2:]) and "과거" not in [s.text for s in segs9])
        # D10 빈 텍스트 무시
        w10 = d / "w10"
        w10.mkdir()
        segs10, _ = transcriber.transcribe(audio, w10, Fake(lambda i, o: [S(0, 1, ""), S(1, 2, "내용")]))
        check("D", "빈 텍스트 무시", [s.text for s in segs10] == ["내용"] and len(read_checkpoint(w10 / "segments.jsonl")) == 1)


GROUPS = [group_a, group_b, group_c, group_d]

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
