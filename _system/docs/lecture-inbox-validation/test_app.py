"""lecture-inbox API(`_system/tools/lecture-inbox/app.py`)의 검사.

  uv run --project _system/tools/lecture-inbox python _system/docs/lecture-inbox-validation/test_app.py

FastAPI가 필요해서 uv 환경에서 돈다. 임시 폴더에만 쓰고 저장소에는 아무것도 쓰지 않는다.
종료 코드 0이면 문제 없음.
"""
import datetime
import pathlib
import shutil
import sys
import tempfile
import traceback
from urllib.parse import quote

sys.dont_write_bytecode = True
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE.parents[2] / "_system/tools/lecture-inbox"
sys.path.insert(0, str(TOOL))

results = []


def check(group, name, cond, note=""):
    results.append((group, name, "PASS" if cond else "FAIL", note))
    return bool(cond)


def group_h():
    import app as app_mod
    import jobs
    from bundle import bundle_dir_name
    from config import Paths
    from fastapi.testclient import TestClient
    from school import SchoolExpired, UserError

    class FakeSchool:
        fail = True
        expired = False

        def login(self, student_id, password):
            if FakeSchool.fail:
                raise UserError("학교 로그인이 확인되지 않았습니다.")

        def courses(self):
            if FakeSchool.expired:
                raise SchoolExpired("학교 로그인이 만료되었습니다.")
            return [{"id": "123", "name": "자료구조 (002639-002)", "year": "2026", "semester": "2학기"}]

        def lectures(self, identifier):
            return [{"id": "9001", "title": "3주차 1차시 트리", "url": "https://x/9001"}]

    H = {"X-Lecture-Inbox": "1"}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="lecture-inbox-app-"))
    try:
        root = tmp / "vault"
        (root / "inbox").mkdir(parents=True)
        (root / "SECOND-BRAIN.md").write_text("x", encoding="utf-8")
        try:
            app_mod.create_app(root=tmp / "none", paths=Paths.at(tmp / "h0"), start_worker=False)
            check("H", "루트 표지 없으면 RuntimeError", False)
        except RuntimeError:
            check("H", "루트 표지 없으면 RuntimeError", True)

        paths = Paths.at(tmp / "h")
        app = app_mod.create_app(root=root, paths=paths, school_factory=FakeSchool, start_worker=False,
                                 allowed_hosts=frozenset({"testserver"}))
        c = TestClient(app)
        store, worker = app.state.store, app.state.worker
        COURSE = "자료구조"
        bdir = root / "inbox" / bundle_dir_name(COURSE, datetime.date.today())
        guide = lambda: (bdir / "안내.md").read_text(encoding="utf-8")

        def upload(kind, name, data, term="2026-2", **extra):
            params = {"kind": kind, "course": COURSE, "term": term, "ecampusId": "123", **extra}
            return c.post("/api/uploads", params=params, content=data, headers={**H, "X-Filename": quote(name)})

        def row(week, session):
            return {"id": "9001", "title": f"{week}주차 {session}차시", "week": week, "session": session}

        def post_lectures(term="2026-2", rows=None):
            body = {"course": {"course": COURSE, "term": term, "ecampusId": "123"},
                    "lectures": rows or [row(3, 2)]}
            return c.post("/api/lectures", json=body, headers=H)

        check("H", "외부 Host 거절", c.get("/api/status", headers={**H, "host": "evil.example"}).status_code == 403)
        check("H", "헤더 없는 API 거절", c.get("/api/status").status_code == 403)
        r = c.get("/api/status", headers=H)
        check("H", "보안 헤더", r.headers.get("cache-control") == "no-store"
              and r.headers.get("x-content-type-options") == "nosniff"
              and r.headers.get("referrer-policy") == "no-referrer")
        check("H", "프레임 차단 헤더", r.headers.get("x-frame-options") == "DENY"
              and "frame-ancestors 'none'" in r.headers.get("content-security-policy", ""))
        check("H", "health", c.get("/api/health", headers=H).json() == {"app": "lecture-inbox"})

        r = c.post("/api/login", json={"studentId": "20261234", "password": "pw-secret-123"}, headers=H)
        check("H", "로그인 실패 401·비번 비노출", r.status_code == 401 and "pw-secret-123" not in r.text)
        r = c.post("/api/login", json={"studentId": "abc", "password": "pw-secret-123"}, headers=H)
        check("H", "422 문구 고정", r.status_code == 422 and r.json() == {"detail": "입력 형식을 확인해 주세요."})
        r = c.post("/api/login", json={"studentId": "２０２６１２３４", "password": "pw-secret-123"}, headers=H)
        check("H", "전각 숫자 학번 422", r.status_code == 422)
        check("H", "비로그인 목록 401", c.get("/api/courses", headers=H).status_code == 401)

        FakeSchool.fail = False
        r = c.post("/api/login", json={"studentId": "20261234", "password": "pw-secret-123"}, headers=H)
        check("H", "로그인 성공", r.status_code == 200 and worker.school is not None)
        check("H", "term 변환", c.get("/api/courses", headers=H).json()["courses"][0]["term"] == "2026-2")
        got = c.get("/api/courses", headers=H).json()["courses"][0]
        check("H", "과목명·학수번호·분반 분리", (got["id"], got["name"], got["code"], got["section"]) == ("123", "자료구조", "002639", "002"))
        lec = c.get("/api/courses/123/lectures", headers=H).json()["lectures"][0]
        check("H", "주차 제안", (lec["week"], lec["session"]) == (3, 1))
        check("H", "상태에 학번 없음", "20261234" not in c.get("/api/status", headers=H).text)
        FakeSchool.expired = True
        s = worker.school
        check("H", "만료 409", c.get("/api/courses", headers=H).status_code == 409 and worker.school is None)
        FakeSchool.expired = False
        worker.school = s

        r = upload("resource", "3주차 강의자료.pdf", b"%PDF-1.7 body")
        check("H", "PDF 묶음 저장", r.status_code == 202 and (bdir / "3주차 강의자료.pdf").read_bytes() == b"%PDF-1.7 body")
        check("H", "안내에 자료 완료", "- 종류: 자료" in guide() and "- 상태: 완료" in guide())
        check("H", "같은 PDF 409·보존", upload("resource", "3주차 강의자료.pdf", b"%PDF-other").status_code == 409
              and (bdir / "3주차 강의자료.pdf").read_bytes() == b"%PDF-1.7 body")
        r = upload("resource", "slides.pptx", b"PK\x03\x04")
        check("H", "비PDF 거절", r.status_code == 400 and "PDF" in r.json()["detail"])
        r = upload("resource", "fake.pdf", b"PK\x03\x04 not pdf")
        check("H", "확장자만 PDF면 거절", r.status_code == 400 and not (bdir / "fake.pdf").exists())

        r = upload("recording", "새 녹음 12.m4a", b"\x00" * 10, week=3, session=1)
        check("H", "녹음은 대기·묶음엔 없음", r.status_code == 202 and not (bdir / "week_03_01.md").exists()
              and "- 상태: 대기" in guide())
        rec = next(i for i in store.all_items() if i["filename"] == "week_03_01.md")
        check("H", "녹음 media 설정", rec["status"] == jobs.TRANSCRIBE_WAIT
              and pathlib.Path(rec["media"]).read_bytes() == b"\x00" * 10
              and pathlib.Path(rec["media"]).parent == paths.work / rec["id"])
        check("H", "상태에 media 비노출", "media" not in c.get("/api/status", headers=H).json()["items"][0])
        check("H", "같은 주차·차시 409", upload("recording", "b.m4a", b"\x00", week=3, session=1).status_code == 409)
        check("H", "녹음 주차 누락 422", upload("recording", "b.m4a", b"\x00").status_code == 422)
        check("H", "업로드 임시 폴더 정리", sorted(p.name for p in paths.work.iterdir()) == [rec["id"]])

        orig = app_mod.MAX_MEDIA_BYTES
        app_mod.MAX_MEDIA_BYTES = 5
        try:
            check("H", "크기 초과 413", upload("recording", "c.m4a", b"\x00" * 10, week=4, session=1).status_code == 413)
            r = c.post("/api/uploads", params={"kind": "recording", "course": COURSE, "term": "2026-2", "ecampusId": "123",
                                               "week": 4, "session": 1},
                       content=b"\x00" * 10, headers={**H, "X-Filename": "d.m4a", "Content-Length": "3"})
            check("H", "받는 도중 초과 413", r.status_code == 413)
        finally:
            app_mod.MAX_MEDIA_BYTES = orig
        r = c.post("/api/uploads", params={"kind": "resource", "course": COURSE, "term": "2026-2"},
                   content=iter([b"%PDF-1"]), headers={**H, "X-Filename": "n.pdf"})
        check("H", "Content-Length 없으면 411", r.status_code == 411)
        check("H", "실패한 업로드 흔적 없음", sorted(p.name for p in paths.work.iterdir()) == [rec["id"]])

        check("H", "학기 형식 422", post_lectures(term="2026-3").status_code == 422)
        check("H", "전각 숫자 학기 422", post_lectures(term="２０２６-1").status_code == 422)
        check("H", "요청 내 중복 409", post_lectures(rows=[row(3, 2), row(3, 2)]).status_code == 409)
        check("H", "다른 학기 같은 묶음 409", post_lectures(term="2026-1").status_code == 409)
        r = post_lectures()
        check("H", "묶음 등록 202", r.status_code == 202)
        rid = next(i["id"] for i in store.all_items() if i["filename"] == "week_03_02.md")
        check("H", "안내에 이캠퍼스 출처", "이캠퍼스 강의" in guide())
        check("H", "예약된 이름과 겹치면 409", post_lectures().status_code == 409)

        (paths.work / rid).mkdir()
        (paths.work / rid / "video.mp4").write_bytes(b"v")
        check("H", "대기 항목은 재시도 불가", c.post(f"/api/items/{rid}/retry", headers=H).status_code == 409)
        store.update(rid, status=jobs.FAILED, error="x")
        r = c.post(f"/api/items/{rid}/retry", headers=H)
        check("H", "미디어 없는 실패는 다운로드 재시도", r.status_code == 200
              and store.find(rid)["status"] == jobs.DOWNLOAD_WAIT)
        store.update(rid, status=jobs.FAILED, media=str(paths.work / rid / "video.mp4"))
        c.post(f"/api/items/{rid}/retry", headers=H)
        check("H", "미디어 있는 실패는 전사 재시도", store.find(rid)["status"] == jobs.TRANSCRIBE_WAIT)
        store.update(rid, status=jobs.TRANSCRIBING)
        check("H", "진행 중 삭제 409", c.delete(f"/api/items/{rid}", headers=H).status_code == 409)
        store.update(rid, status=jobs.DOWNLOAD_WAIT)
        check("H", "대기 항목 삭제", c.delete(f"/api/items/{rid}", headers=H).status_code == 200
              and not (paths.work / rid).exists())
        check("H", "없는 항목 404", c.delete(f"/api/items/{rid}", headers=H).status_code == 404)

        # 경합 보강: 저장소 호출 결과가 중간에 달라진 경우를 흉내 낸다.
        real_claim = store.claim

        def claim_after_delete(item_id, *a, **k):  # 옮기는 사이 항목이 지워진 실제 경합
            store.remove(item_id)
            return None
        store.claim = claim_after_delete
        try:
            r = upload("recording", "race.m4a", b"\x00", week=7, session=1)
        finally:
            store.claim = real_claim
        check("H", "업로드 claim 실패 409·되돌림", r.status_code == 409
              and not any(i["filename"] == "week_07_01.md" for i in store.all_items())
              and sorted(p.name for p in paths.work.iterdir()) == [rec["id"]])
        hole = store.add_item(kind="transcript", bundle=rec["bundle"], filename="week_08_01.md", status=jobs.FAILED,
                              error="x", source={"type": "upload", "name": "x.m4a"})
        check("H", "업로드 자리표시자 재시도 409", c.post(f"/api/items/{hole['id']}/retry", headers=H).status_code == 409
              and store.find(hole["id"])["status"] == jobs.FAILED)
        check("H", "업로드 자리표시자 삭제 409", c.delete(f"/api/items/{hole['id']}", headers=H).status_code == 409
              and store.find(hole["id"])["status"] == jobs.FAILED)
        check("H", "조건부 remove는 상태가 다르면 None", store.remove(hole["id"], from_statuses=(jobs.DONE,)) is None
              and store.remove(hole["id"], from_statuses=(jobs.FAILED,))["id"] == hole["id"])
        busy = store.add_item(kind="transcript", bundle=rec["bundle"], filename="week_09_01.md",
                              status=jobs.TRANSCRIBING, error=None, source={"type": "ecampus", "lecture_id": "1", "title": "t"})
        real_find = store.find
        store.find = lambda i: {**real_find(i), "status": jobs.FAILED}  # 확인 뒤에 워커가 집은 상황
        try:
            r = c.delete(f"/api/items/{busy['id']}", headers=H)
        finally:
            store.find = real_find
        check("H", "삭제 확인 뒤 상태 바뀌면 409·보존", r.status_code == 409 and store.find(busy["id"])["status"] == jobs.TRANSCRIBING)
        store.remove(busy["id"])

        # 시작 정리: 비정상 종료로 남은 up-* 임시 폴더와 업로드 자리표시자를 치운다
        paths3 = Paths.at(tmp / "h3")
        pre = jobs.Store(paths3.state_file)
        sweep_bundle = bundle_dir_name(COURSE, datetime.date.today())
        pre.add_bundle(sweep_bundle, {"course": COURSE, "term": "2026-2", "ecampus_id": "123", "code": None, "section": None})
        up_src = {"type": "upload", "name": "x.m4a"}
        hole2 = pre.add_item(kind="transcript", bundle=sweep_bundle, filename="week_01_01.md", status=jobs.FAILED,
                             week=1, session=1, error=app_mod.SAVING, source=up_src)
        keep_media = pre.add_item(kind="transcript", bundle=sweep_bundle, filename="week_01_02.md", status=jobs.FAILED,
                                  week=1, session=2, error="x", source=up_src, media=str(paths3.work / "m" / "x.m4a"))
        keep_dl = pre.add_item(kind="transcript", bundle=sweep_bundle, filename="week_01_03.md", status=jobs.FAILED,
                               week=1, session=3, error="x", source={"type": "ecampus", "lecture_id": "1", "title": "t"})
        for d in ("up-aaaaaa", hole2["id"], keep_media["id"]):
            (paths3.work / d).mkdir()
            (paths3.work / d / "f").write_bytes(b"1")
        (paths3.work / "other").mkdir()
        app3 = app_mod.create_app(root=root, paths=paths3, start_worker=False, allowed_hosts=frozenset({"testserver"}))
        left = {i["id"] for i in app3.state.store.all_items()}
        check("H", "시작 정리: 자리표시자만 제거", left == {keep_media["id"], keep_dl["id"]})
        check("H", "시작 정리: up-*와 자리표시자 작업 폴더 제거",
              sorted(p.name for p in paths3.work.iterdir()) == sorted([keep_media["id"], "other"]))
        text3 = (root / "inbox" / sweep_bundle / "안내.md").read_text(encoding="utf-8")
        check("H", "시작 정리: 안내.md 갱신", "week_01_01.md" not in text3 and "week_01_02.md" in text3)

        # 단일 실행: 포트를 먼저 잡고, 못 잡았을 때만 상대가 우리 서버인지 본다
        import http.server
        import socket as _socket
        import threading

        def free_port():
            with _socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                return probe.getsockname()[1]

        class Health(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{"app": "lecture-inbox"}'
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        port = free_port()
        first, why = app_mod._claim_port("127.0.0.1", port)
        second, ours = app_mod._claim_port("127.0.0.1", port)
        check("H", "빈 포트는 잡고 두 번째는 못 잡음", first is not None and why is None and second is None and ours is None)
        first.close()
        plain = _socket.socket()
        plain.bind(("127.0.0.1", 0))
        plain.listen(16)
        sock, ours = app_mod._claim_port("127.0.0.1", plain.getsockname()[1])
        check("H", "다른 프로그램이 쓰는 포트는 우리 것이 아님", sock is None and ours is False)
        srv = http.server.HTTPServer(("127.0.0.1", 0), Health)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        sock, ours = app_mod._claim_port("127.0.0.1", srv.server_address[1])
        check("H", "health가 우리 앱이면 ours", sock is None and ours is True)
        opened, real_open, real_port = [], app_mod.webbrowser.open, app_mod.PORT
        app_mod.webbrowser.open = opened.append
        try:
            app_mod.PORT = srv.server_address[1]
            rc_ours = app_mod.main()
            app_mod.PORT = plain.getsockname()[1]
            rc_other = app_mod.main()
        finally:
            app_mod.webbrowser.open, app_mod.PORT = real_open, real_port
            srv.shutdown()
            srv.server_close()
            plain.close()
        check("H", "main: 우리 서버면 0·브라우저만, 다른 프로그램이면 1·브라우저 없음",
              rc_ours == 0 and rc_other == 1 and len(opened) == 1)

        page = c.get("/")
        check("H", "화면 제공", "강의 수집 도구" in page.text and "frame-ancestors 'none'" in page.headers["content-security-policy"])
        # 브라우저 없이 확인할 수 있는 최소한: 화면 코드에 해당 규칙이 들어 있다(동작은 수동 확인)
        check("H", "화면: 대기 삭제·로그인 배너 조건·수업일 자동 입력 없음",
              '["failed", "download-wait", "transcribe-wait"].includes(it.status)' in page.text
              and "!s.loggedIn && s.waitingLogin > 0" in page.text
              and 'date: localDate(file.lastModified)' not in page.text and "파일 날짜 사용" in page.text)
        check("H", "화면은 외부 리소스·innerHTML 없음", "innerHTML" not in page.text and "http://" not in page.text
              and "https://" not in page.text and 'src="' not in page.text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def group_r():
    # Real faster-whisper + PyAV decode, no model needed. Catches library version
    # mismatches the fake engines in test_core can't see (av 19 broke decode_audio).
    import wave
    import transcriber
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        wav = tmp / "tone.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(b"\x00\x00" * 16000)
        audio = transcriber.load_audio(wav)
        check("R", "실제 라이브러리로 소리 추출", abs(len(audio) - 16000) < 200)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


try:
    group_r()
except Exception:
    check("R", "그룹 실행", False, traceback.format_exc().strip().splitlines()[-1])

try:
    group_h()
except Exception:
    check("H", "그룹 실행", False, traceback.format_exc().strip().splitlines()[-1])

shown = None
for g, name, verdict, note in results:
    if g != shown:
        print(f"\n[{g}]")
        shown = g
    print(f"  {verdict}  {name}" + (f"   ({note})" if verdict == "FAIL" and note else ""))
fails = [r for r in results if r[2] == "FAIL"]
print(f"\nPASS {len(results) - len(fails)} / FAIL {len(fails)}")
sys.exit(1 if fails else 0)
