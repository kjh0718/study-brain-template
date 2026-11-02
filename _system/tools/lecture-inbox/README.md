# lecture-inbox

강의 영상·음성을 로컬에서 전사해 `inbox/`에 넣어 주는 Windows 도구다. 서버는 `127.0.0.1:4319`에서만 열린다.

사용법과 구조 설명은 아직 없다. 구현이 끝나면 채운다.

## 설치

```powershell
$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA\lecture-inbox\venv"
uv sync --project _system/tools/lecture-inbox
```

가상환경은 저장소 밖에 만든다. 모델·작업물·상태도 `%LOCALAPPDATA%\lecture-inbox\`에 둔다.
