# lecture-inbox

강의 영상·음성을 로컬에서 전사해 `inbox/`에 넣어 주는 Windows 도구다. 서버는 `127.0.0.1:4319`에서만 열린다.

도구가 vault에 쓰는 곳은 `inbox/`뿐이다. 모델·작업물·상태는 모두 저장소 밖에 둔다.

## 설치

1. [uv](https://docs.astral.sh/uv/)를 설치한다.
2. 저장소 루트에서 처음 실행한다. 가상환경이 `%LOCALAPPDATA%\lecture-inbox\venv`에 만들어진다.
3. ffmpeg가 없으면 터미널이 설치 명령(`winget install --id Gyan.FFmpeg -e`)을 보여 주고 `지금 설치할까요? [y/N]`를 묻는다. `y`일 때만 설치한다. 거절해도 실행되고, 파일 업로드 전사는 ffmpeg 없이 된다. 이캠퍼스 영상 다운로드에는 필요하다.
4. 모델은 첫 전사 때 약 3 GB(`large-v3`)를 자동으로 받는다. 받는 동안 화면에 "모델 준비 중"으로 보인다.

## 실행

```powershell
_system\tools\lecture-inbox\start.cmd
```

브라우저가 `http://127.0.0.1:4319/`를 연다. 이미 실행 중이면 서버를 또 띄우지 않고 브라우저만 연다. 다른 프로그램이 4319 포트를 쓰고 있으면 메시지를 내고 종료한다. 접근 로그는 남기지 않는다.

시작할 때 비정상 종료로 남은 `work\up-*` 임시 폴더와 "업로드를 저장하는 중입니다." 자리표시자를 치운다.

## 데이터 위치

`%LOCALAPPDATA%\lecture-inbox\` 아래에 `venv`, `models`, `work`, `state`, `settings.json`이 있다. `LECTURE_INBOX_HOME`을 설정하면 그 폴더를 대신 쓴다.

## 모델 바꾸기

`settings.json`의 `"model"` 하나로 바꾼다. 값은 `large-v3`(기본), `large-v3-turbo`, `medium`, `small` 중 하나다. 다음 전사부터 적용된다.

## 검사

```powershell
python _system/docs/lecture-inbox-validation/test_core.py

$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA\lecture-inbox\venv"
uv run --project _system/tools/lecture-inbox python _system/docs/lecture-inbox-validation/test_app.py
```

`UV_PROJECT_ENVIRONMENT`를 설정하지 않고 `uv`를 쓰면 저장소 안에 `.venv`가 생긴다.

## 문제 해결

`import ctranslate2`가 DLL 오류로 실패하면 Visual C++ 런타임이 없는 것이다. 설치 동의를 받은 뒤 `winget install Microsoft.VCRedist.2015+.x64`를 실행한다.
