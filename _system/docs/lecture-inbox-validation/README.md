# lecture-inbox Validation

[`_system/tools/lecture-inbox/`](../../tools/lecture-inbox/README.md)의 코어 로직과 API가 계약을 지키는지 검사한다.

```bash
# 코어: 시스템 Python, 표준 라이브러리만 쓴다
python _system/docs/lecture-inbox-validation/test_core.py

# 앱: FastAPI가 필요하므로 uv 환경에서 돈다
$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA\lecture-inbox\venv"
uv run --project _system/tools/lecture-inbox python _system/docs/lecture-inbox-validation/test_app.py
```

fixture는 임시 폴더에만 만들고 저장소에는 아무것도 쓰지 않는다. 종료 코드 0이면 문제 없음. 마지막 줄은 `PASS n / FAIL n`이다. `test_core.py`만 [`run_all.py`](../run_all.py)에 등록돼 있다.

## 검사 항목

| | 내용 |
|---|---|
| A | 설정과 경로. 데이터 폴더 생성, `settings.json` 기본값과 잘못된 모델 거절, `LECTURE_INBOX_HOME` 우선순위, 저장소 루트, 로컬 전용 바인드 |
| P | 사전 준비(`prereq.py`). ffmpeg 경로 탐색(PATH → WinGet Links → WinGet Packages), 설치 동의 없이는 실행 안 함, 모델이 있으면 다시 받지 않음 |
| H | API(`test_app.py`). Host·헤더 검사, 로그인·422 문구, 학기·학번 전각 숫자 거절, 업로드(PDF·녹음·크기 제한), 묶음 등록 충돌, 재시도·삭제·진행 중 취소, 시작 시 임시 폴더·자리표시자 정리, 소리 길이(`duration`) 기록과 `/api/status` 노출, 화면 규칙(멈추기·확인창·알림·탭 제목·목록 순서·드롭 영역 한도) |
| R | 실제 faster-whisper·PyAV로 짧은 WAV에서 소리 추출(`test_app.py`, 모델 불필요). 라이브러리 버전이 맞지 않으면 실패한다. 같은 WAV로 `media_seconds`(메타데이터에서 길이 읽기)도 확인한다 |
