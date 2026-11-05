# lecture-inbox

강의 영상·음성을 로컬에서 전사해 `inbox/`에 넣어 주는 Windows 도구다. 서버는 `127.0.0.1:4319`에서만 열린다.

도구가 vault에 쓰는 곳은 `inbox/`뿐이다. 모델·작업물·상태는 모두 저장소 밖에 둔다.

## 설치

1. [uv](https://docs.astral.sh/uv/)를 설치한다.
2. 저장소 루트에서 처음 실행한다. 가상환경이 `%LOCALAPPDATA%\lecture-inbox\venv`에 만들어진다.
3. ffmpeg가 없으면 터미널이 설치 명령(`winget install --id Gyan.FFmpeg -e`)을 보여 주고 `지금 설치할까요? [y/N]`를 묻는다. `y`일 때만 설치한다. 거절해도 실행되고, 파일 업로드 전사는 ffmpeg 없이 된다. 이캠퍼스 영상 다운로드에는 필요하다. 설치 직후 `ffmpeg`가 없다고 나오면 PATH가 갱신되지 않은 것이다. 도구는 WinGet `Links`와 `Packages` 폴더도 찾아보므로 대부분 그대로 인식하고, 그래도 안 되면 새 창에서 다시 실행한다.
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

## GPU로 빠르게 전사하기 (NVIDIA)

기본값(`"device": "auto"`)은 NVIDIA GPU가 보이면 GPU(float16), 없으면 CPU(int8)로 전사한다. GPU는 CPU보다 훨씬 빠르지만 이 저장소에서는 속도를 재 보지 못했다.

필요한 것(faster-whisper 문서 기준):

- NVIDIA GPU와 드라이버
- cuBLAS(CUDA 12)와 cuDNN 9. 둘 중 하나로 맞춘다.
  - CUDA 12 툴킷과 cuDNN 9를 설치한다.
  - 또는 [Purfview whisper-standalone-win](https://github.com/Purfview/whisper-standalone-win)의 `libs` 압축 파일 DLL을 한 폴더에 풀고 그 폴더를 `PATH`에 추가한다.

`settings.json`의 `"device"`로 고른다. 값은 `auto`(기본), `cuda`(GPU 고정), `cpu`(CPU 고정)다. 엔진을 새로 만들 때 적용되므로, 바꾼 뒤에는 서버를 다시 켜는 것이 확실하다.

확인: 전사가 시작되면 화면 위쪽에 "GPU로 전사해요" 또는 "CPU로 전사해요"가 보인다. 엔진이 뜨기 전에 `auto`이면 아무것도 보이지 않는다.

전사를 시작할 때 서버가 cudnn·cublas DLL을 찾지 못한다는 메시지와 함께 죽으면 위 라이브러리를 설치하거나 `"device": "cpu"`로 바꾼다.

## 화면

- 진행 칸은 실패, 진행 중, 대기, 끝남 순으로 보인다.
- 남은 시간은 전사가 진행되는 속도로 추정한다. 속도를 알기 전에는 "N개 남았어요 · 총 X 분량", 알고 나면 "N개 남았어요 · 약 X 남았어요"가 보이고 전사 중인 항목에는 "약 N분 남았어요"가 붙는다. 30분이 넘으면 5분 단위로 맞춘다. 이캠퍼스 영상을 받는 중이거나 소리 길이를 읽지 못한 항목이 있으면 시간은 빼고 개수만 보인다. 길이는 업로드가 끝났을 때와 영상을 다 받았을 때 파일 메타데이터에서 읽어 항목의 `duration`(초)으로 저장한다.
- 진행 중인 항목의 "멈추기"와 대기·실패 항목의 "삭제"는 확인창을 거친다. Esc나 바깥을 누르면 닫힌다. 처리가 끝나면 아래에 알림이 4초 보인다.
- 브라우저 탭 제목에 남은 개수 `(N개 남음)`, 실패 수 `(실패 N)`, 모두 끝났을 때 `✓ 다 했어요`가 나온다.
- 드롭 영역 아래에 받는 파일 종류와 크기 한도(`config.MAX_MEDIA_BYTES`, 지금은 파일당 2GB)가 보인다. 녹음·영상은 확장자를 따로 막지 않고 ffmpeg가 읽을 수 있으면 받으며, 자료·족보·과제는 PDF만 받는다.

## 검사

```powershell
python _system/docs/lecture-inbox-validation/test_core.py

$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA\lecture-inbox\venv"
uv run --project _system/tools/lecture-inbox python _system/docs/lecture-inbox-validation/test_app.py
```

`UV_PROJECT_ENVIRONMENT`를 설정하지 않고 `uv`를 쓰면 저장소 안에 `.venv`가 생긴다.

## 문제 해결

`import ctranslate2`가 DLL 오류로 실패하면 Visual C++ 런타임이 없는 것이다. 설치 동의를 받은 뒤 `winget install Microsoft.VCRedist.2015+.x64`를 실행한다.
