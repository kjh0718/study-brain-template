# 강의 수집 도구(lecture-inbox for Windows) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 이캠퍼스 강의 받기, 녹음 전사, PDF 올리기를 한 화면에서 하고, 결과를 과목별 묶음으로 `inbox/`에 놓는 Windows용 로컬 도구를 만든다. template 문서는 그 묶음을 "사용자 지정"으로 받도록 고친다.

**Architecture:** `_system/tools/lecture-inbox/`에 평평한 Python 모듈들을 두고, FastAPI 서버(127.0.0.1:4319)가 HTML 한 장을 내보낸다. 작업 큐는 워커 스레드 하나가 처리하며 상태를 `%LOCALAPPDATA%\lecture-inbox\state\jobs.json`에 원자적으로 쓴다. 전사는 faster-whisper(CPU int8)로 한다. 음성은 `decode_audio`(PyAV 내장 FFmpeg)로 메모리에 풀고, 끝난 구간은 JSONL 체크포인트에 바로 붙여 쓴다. 다시 켜면 마지막 구간의 끝 시각부터 오디오 배열을 잘라 이어서 디코딩하고, 그 시각만큼 타임스탬프를 더한다. ffmpeg CLI는 HLS 다운로드에만 쓴다. 그래서 따로 "추출한 음성" 파일은 생기지 않는다(spec 7에서 빌더에게 맡긴 이어하기 방식).

**Tech Stack:** Python 3.12(uv 관리), FastAPI 0.142.2, uvicorn 0.54.0, faster-whisper 1.2.1(ctranslate2·onnxruntime·av), 테스트용 httpx 0.28.1, 표준 라이브러리 `urllib`·`html.parser`·`ctypes`, 순수 HTML/JS, ffmpeg(Gyan.FFmpeg, winget).

**Spec:** `_system/docs/specs/2026-11-02-lecture-inbox-design.md`

## Main 결정 필요 (저장소와 spec의 충돌)

1. **[해결됨 2026-11-02: 사용자가 (b) 선택 → Task 11 Step 3]** **ASM에는 `source` 필드가 없다.** spec 6.3은 L5 완료 조건으로 "ASM의 `source`가 그 경로를 가리킨다"를 요구한다. 그런데 `_system/schemas/assignment.md`에는 `sources`(LEC·RES·FAC **ID** 목록)만 있고 경로 필드는 없다. SECOND-BRAIN §0은 스키마에 없는 새 필드를 승인 없이 만들지 못하게 한다. 선택지는 둘이다.
   - (a) 완료 조건을 "과제 원본이 `raw/<term>/<course-slug>/assignments/`에 있고, ASM 본문 `## Sources`에 그 경로가 적혀 있다"로 바꾼다. 스키마는 그대로 둔다.
   - (b) assignment 스키마·템플릿·검증 스크립트에 `source` 필드를 추가한다. 범위가 커진다.

   Task 11 Step 3은 이 결정을 받기 전까지 **보류**다. 나머지 Task는 이 결정과 무관하다.
2. **가정 (영향 작음, 진행하되 확인 요청):** 묶음의 PDF와 같은 내용이 이미 `raw/`에 있으면 L2 1단계에 따라 다시 복사하지 않는다. 이때 inbox 사본은 "처리됨"으로 본다. 로그에 `preserve-source`와 메모 "이미 보존됨: <경로>"를 남기고, 묶음을 지울 때 함께 지운다. 이 가정이 없으면 그런 묶음은 영영 지워지지 않는다.

## 확인한 외부 사실 (2026-11-02, Context7·PyPI)

- faster-whisper 최신은 1.2.1(2025-10-31)이고 `requires_python >=3.9`다. 의존성은 `ctranslate2>=4.0,<5`, `onnxruntime>=1.14,<2`, `av>=11`, `tokenizers`, `huggingface-hub`다.
- `utils._MODELS`에 `large-v3`(Systran/faster-whisper-large-v3)와 `large-v3-turbo`(mobiuslabsgmbh/faster-whisper-large-v3-turbo)가 있다.
- `WhisperModel.transcribe(audio: str|BinaryIO|np.ndarray, ..., condition_on_previous_text=True, vad_filter=False, clip_timestamps="0", temperature=[0.0..1.0], compression_ratio_threshold=2.4)`는 lazy generator인 `segments`와 `info`를 돌려준다.
  - 문서에는 `condition_on_previous_text=False`가 반복 루프를 줄인다고 적혀 있다(원본 whisper.cpp의 `-mc 0`과 같은 역할).
  - `clip_timestamps`와 `vad_filter`를 함께 쓸 때의 동작은 문서에서 확인하지 못했다. 그래서 이어하기는 **배열 슬라이싱 + 오프셋 더하기**로 한다.
- `decode_audio(path, sampling_rate=16000)`는 PyAV 내장 FFmpeg로 float32 mono 배열을 만든다. ffmpeg CLI가 필요 없다.
- `download_model(size_or_id, output_dir=...)`는 `model.bin` 등을 output_dir에 받는다.
- ctranslate2 4.8.4(2026-10-25)는 cp310~cp315 `win_amd64` 휠이 있다. 업로드된 지 2주가 안 됐으므로 `exclude-newer`로 그 전 버전을 고정한다.
- uv의 `UV_PROJECT_ENVIRONMENT`에 절대경로를 주면 그 경로를 그대로 venv로 쓴다. `[tool.uv] package = false`로 패키지가 아닌 프로젝트를 만든다.
- FastAPI `TestClient`는 httpx가 필요하다.
- **확인하지 못한 것:**
  - Gyan.FFmpeg 빌드에서 `-tls_verify 1`이 Windows 인증서 저장소로 동작하는지(Task 13에서 확인)
  - Qwen3-ASR의 Windows CPU 실행 가능성(Task 12에서 시간을 정해 확인)

## Global Constraints

- 도구가 vault에 쓰는 곳은 `inbox/`뿐이다. `raw/`, `study/`, `wiki/`, `_system/log.md`에는 절대 쓰지 않는다.
- 학번, 비밀번호, 서명된 URL, ffmpeg stderr를 로그·디스크·화면·오류 메시지에 남기지 않는다. TLS 검증을 끄지 않는다. 학교 쿠키는 메모리에만 둔다.
- 서버는 `127.0.0.1`에만 바인드하고 포트는 `4319`(`config.PORT`)를 쓴다.
- 과목·학기는 사용자 입력이나 학교 목록에서 온 값만 쓴다. 도구는 course-slug를 정하지 않는다. 이캠퍼스 내부 id는 `code`가 아니라 "이캠퍼스 과목 id"로 적는다.
- term 형식은 `^\d{4}-(1|2|summer|winter)$`다.
- 전사 `.md`는 한 줄에 `[HH:MM:SS] 문장` 하나다. 머리말과 frontmatter를 붙이지 않는다. 끝내 해결하지 못한 반복 구간은 줄 앞에 `[⚠️ 반복 감지 - 확인 필요] `를 붙인다.
- 묶음은 과목 하나당 폴더 하나이고 이름은 `<YYYYMMDD>-<과목명>`(제출한 날짜)이다. 이미 있는 파일은 덮어쓰지 않는다. 파일은 `완료`가 된 뒤에만 묶음에 나타난다.
- PDF만 받는다(자료/족보/과제). PDF가 아니면 거절하고 변환을 안내한다.
- 기본 모델은 `large-v3`, CPU `int8`이다. `%LOCALAPPDATA%\lecture-inbox\settings.json`의 `"model"` 하나로 바꾼다.
- Python은 3.12(`requires-python = ">=3.12,<3.13"`)다. venv·모델·영상·임시 파일·상태는 `%LOCALAPPDATA%\lecture-inbox\` 아래 둔다.
  - **모든 `uv` 명령은 `UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\lecture-inbox\venv`를 설정한 상태로 실행한다.** 그렇지 않으면 `.venv`가 vault에 생긴다.
  - PowerShell에서는 `$env:UV_PROJECT_ENVIRONMENT = "$env:LOCALAPPDATA\lecture-inbox\venv"`로 설정한다.
- `.gitignore`는 고치지 않는다(SECOND-BRAIN 2.12). 새 고정 폴더(`_system/tools/`, `_system/tools/lecture-inbox/`, `_system/docs/lecture-inbox-validation/`)에는 README.md를 만든다.
- ffmpeg는 `winget install --id Gyan.FFmpeg -e`로 설치하되 터미널에서 사용자가 동의한 뒤에만 실행한다.
- 다운로드 제한은 크기 2 GiB(`2 * 1024**3`), 시간 7200초다. HTTPS와 공인 IP만 허용하고, 403이면 `Referer: https://ecampus.sejong.ac.kr/`를 붙여 한 번 재시도한다.
- 절전 방지는 `SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED)` = `0x80000001`, 해제는 `0x80000000`이다. 화면 꺼짐(`ES_DISPLAY_REQUIRED`)은 막지 않는다.
- 다음 모듈은 맨 위에서 `fastapi`·`faster_whisper`·`numpy`를 import하지 않는다(시스템 Python으로 `run_all.py`가 돌아야 함): `config`, `bundle`, `transcript`, `repetition`, `transcriber`, `jobs`, `school`, `hls`, `prereq`.
- 테스트는 기존 `_system/docs/*-validation/` 방식을 따른다. 표준 라이브러리 스크립트, `check(group, name, cond)`, 마지막 줄 `PASS n / FAIL n`, FAIL이 있으면 종료 코드 1이다.
- 원본의 React 화면과 study·exam·notes 기능은 이식하지 않는다.
- 커밋하지 않는다. 각 Task 끝은 "변경 확인(`git status`, `git diff`)이고, 커밋은 사용자가 요청할 때만" 한다. 필요하면 사용자에게 `git switch -c feat/lecture-inbox`를 선택지로 알린다.

## Review Focus

1. **체크포인트 줄을 쓰는 도중 꺼짐(정전·강제 종료)** → 다시 켜면 잘린 마지막 줄을 버리고 그 앞 구간의 끝부터 이어서 한다. 처음부터 다시 하지 않는다. (Task 3 `read_checkpoint` 잘린 줄 테스트, Task 4 이어하기 테스트)
2. **브라우저의 다른 사이트가 `http://127.0.0.1:4319`로 보내는 요청(CSRF, DNS rebinding)** → 거부한다. 학교 세션을 쓰거나 작업을 넣지 못한다. (Task 8 Host·헤더 테스트)
3. **음성이 없는 녹음, 또는 전사 결과가 0줄** → 빈 `.md`를 `완료`로 내지 않고 `실패: 인식된 음성이 없습니다`로 표시한다. (Task 5 테스트)
4. **같은 날 같은 과목에 같은 주차·차시를 다시 넣음** → 409로 거절하고 기존 파일·작업을 보존한다. (Task 5 Store, Task 8 API 테스트)
5. **Claude가 묶음 일부를 `raw/`로 옮겼거나 묶음을 지운 뒤 도구가 `안내.md`를 다시 씀** → 폴더를 다시 만들고, 이미 옮긴 `완료` 항목은 `안내.md`에서 빠진다. 없는 파일을 `완료`로 가리키지 않는다. (Task 2 `render_guide`·`write_guide` 테스트)

---

## 파일 구조

| 경로 | 책임 |
|---|---|
| `_system/tools/README.md` | 고정 폴더 안내 (2.12) |
| `_system/tools/lecture-inbox/README.md` | 설치·실행·설정·데이터 위치 |
| `_system/tools/lecture-inbox/pyproject.toml`, `.python-version`, `uv.lock` | 의존성 고정 |
| `_system/tools/lecture-inbox/start.cmd` | 저장소 루트에서 한 줄로 실행 |
| `config.py` | 경로·상수·settings |
| `bundle.py` | 묶음 폴더 이름, 덮어쓰지 않는 쓰기, `안내.md` 렌더 |
| `transcript.py` | `Segment`, `[HH:MM:SS]` 형식, JSONL 체크포인트 |
| `repetition.py` | 반복 구간 탐지 (원본 이식) |
| `transcriber.py` | 이어하기 전사, 반복 재디코딩, faster-whisper 어댑터 |
| `jobs.py` | 상태 저장, 다음 작업 선택, 워커, 절전 방지 |
| `school.py` | 세종대 로그인·목록·m3u8 파싱, term·주차 제안 |
| `hls.py` | CDN 주소 검사, ffmpeg HLS 다운로드 |
| `prereq.py` | ffmpeg 찾기·설치 제안, 모델 받기 |
| `app.py` | FastAPI 라우트, 로컬 전용 미들웨어, `main()` |
| `index.html` | 화면 한 장 |
| `compare.py` | 모델 비교 (Task 12) |
| `_system/docs/lecture-inbox-validation/README.md`, `test_core.py`, `test_app.py` | 검사 |
| `_system/docs/run_all.py` | `test_core.py` 등록 |

모듈은 모두 `_system/tools/lecture-inbox/` 바로 아래에 둔다(하위 폴더를 만들면 README 규칙이 붙는다). 테스트는 `sys.path.insert(0, str(ROOT / "_system/tools/lecture-inbox"))` 후 import한다.

---

### Task 1: 도구 골격, 설정, 검사 스위트 등록

**Files:**
- Create: `_system/tools/README.md`, `_system/tools/lecture-inbox/{README.md,pyproject.toml,.python-version,config.py}`
- Create: `_system/docs/lecture-inbox-validation/{README.md,test_core.py}`
- Modify: `_system/docs/run_all.py` (`SUITES` 끝에 추가)
- Generate: `_system/tools/lecture-inbox/uv.lock`

**Interfaces:**
- Produces (`config.py`):
  - 경로 상수: `ROOT: Path`(= `Path(__file__).resolve().parents[3]`), `INBOX = ROOT / "inbox"`
  - 서버·제한 상수: `HOST = "127.0.0.1"`, `PORT = 4319`, `MAX_MEDIA_BYTES = 2 * 1024**3`, `DOWNLOAD_TIMEOUT_S = 7200`
  - 모델 상수: `DEFAULT_MODEL = "large-v3"`, `KNOWN_MODELS = ("large-v3", "large-v3-turbo", "medium", "small")`
  - `@dataclass(frozen=True) class Paths: home, models, work, state_file, settings_file` 와 `Paths.at(home: Path) -> Paths`(하위 폴더 생성, `state_file = home/"state"/"jobs.json"`, `settings_file = home/"settings.json"`)
  - `data_home(env: Mapping[str, str] = os.environ) -> Path`: `LECTURE_INBOX_HOME`이 있으면 그것, 없으면 `LOCALAPPDATA\lecture-inbox`
  - `load_settings(path: Path) -> dict`: 파일이 없으면 `{"model": "large-v3"}`로 만들고, 모르는 모델이면 `ValueError("settings.json의 model은 ... 중 하나여야 합니다")`
- Produces (`test_core.py` 뼈대):
  - `check(group, name, cond, note="")`
  - 그룹 함수 목록 `GROUPS`: 그룹마다 예외를 잡아 FAIL로 기록하고, 마지막 줄에 `PASS n / FAIL n`을 출력한다
  - 임시 폴더 helper `tmpdir()`

- [ ] **Step 1: `pyproject.toml`·`.python-version` 작성 후 lock 생성**

`pyproject.toml`:
```toml
[project]
name = "lecture-inbox"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = ["fastapi==0.142.2", "uvicorn==0.54.0", "faster-whisper==1.2.1"]

[dependency-groups]
dev = ["httpx==0.28.1"]

[tool.uv]
package = false
exclude-newer = "2026-10-19T00:00:00Z"
```
`.python-version`에는 `3.12`를 쓴다.

Run: `$env:UV_PROJECT_ENVIRONMENT="$env:LOCALAPPDATA\lecture-inbox\venv"; uv lock --project _system/tools/lecture-inbox; uv sync --project _system/tools/lecture-inbox`

Expected: `uv.lock`이 생기고 `ctranslate2`·`onnxruntime`·`av`가 `win_amd64` cp312 휠로 설치된다. 저장소 안에 `.venv`가 없다(`Test-Path _system/tools/lecture-inbox/.venv` → False). 고정 버전이 cutoff 이후 버전이라 lock이 실패하면, cutoff 이전의 최신 버전으로 바꾸고 바꾼 내용을 보고한다.

- [ ] **Step 2: 실패하는 테스트 작성 (그룹 A)**

```python
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
```

- [ ] **Step 3: 실패 확인**

Run: `python _system/docs/lecture-inbox-validation/test_core.py`

Expected: 종료 코드 1, `A ... FAIL ... ModuleNotFoundError: config`.

- [ ] **Step 4: `config.py` 구현.** 위 Interfaces 그대로 만든다. 표준 라이브러리만 쓴다.

- [ ] **Step 5: 통과 확인 및 run_all 등록**

`SUITES`에 다음을 추가한다:
```python
{"name": "lecture-inbox 검사", "dir": "lecture-inbox-validation", "script": "test_core.py",
 "needs": ["_system/tools/lecture-inbox/config.py"], "pattern": r"PASS \d+ / FAIL \d+"}
```
Run: `python _system/docs/lecture-inbox-validation/test_core.py` → `PASS 7 / FAIL 0`, 종료 코드 0.

Run: `python _system/docs/run_all.py --list` → 7번째 줄에 `lecture-inbox 검사`가 보인다.

- [ ] **Step 6: README 두 개 작성**
  - `_system/tools/README.md`: 목적, 여기 두는 것(노트가 아닌 보조 실행 도구), 여기 두지 않는 것(모델·영상·venv), 규격 "해당 없음", 관련 문서. 형식은 `inbox/README.md` 절 구성을 따른다.
  - `lecture-inbox-validation/README.md`: hook-validation README 형식으로 실행 명령 2개(`test_core.py`는 시스템 Python, `test_app.py`는 uv)와 그룹 표.
  - 도구 README는 Task 10에서 채운다.

- [ ] **Step 7: 변경 확인** — `git status`에 `_system/tools/`, `_system/docs/lecture-inbox-validation/`, `run_all.py`만 보인다. 커밋은 사용자가 요청할 때만 한다.

---

### Task 2: inbox 묶음 쓰기와 `안내.md`

**Files:** Create `_system/tools/lecture-inbox/bundle.py`. Test: `test_core.py` 그룹 B.

**Interfaces:**
- Consumes: 없음
- Produces:
  - 표시용 상수:
    - `KIND_LABEL = {"transcript": "전사", "resource": "자료", "past-exam": "족보", "assignment": "과제"}`
    - `STATUS_LABEL = {"done": "완료", "failed": "실패"}` (그 밖의 상태는 모두 `"대기"`)
  - `safe_name(value: str) -> str`: 원본 `school.safe_name`을 이식한다. Windows 예약 이름(stem이 `CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]`, 대소문자 무시)이면 앞에 `_`를 붙인다.
  - `bundle_dir_name(course: str, day: date) -> str` → `f"{day:%Y%m%d}-{safe_name(course)}"`
  - `transcript_name(week: int, session: int) -> str` → `f"week_{week:02d}_{session:02d}.md"`
  - `write_new_file(dest: Path, src: bytes | Path) -> None`
    - 같은 폴더에 `.{dest.name}.partial`로 쓴 뒤 `os.rename`한다. Windows에서는 대상이 있으면 `FileExistsError`가 난다.
    - 실패하면 partial을 지우고, 쓰기 전에 대상이 이미 있으면 바로 `FileExistsError`를 낸다.
  - `render_guide(meta: dict, items: list[dict], present: set[str]) -> str`
  - `write_guide(folder: Path, meta: dict, items: list[dict]) -> None`: 폴더를 만들고(`exist_ok`), `present = {p.name for p in folder.iterdir()}`를 구한 뒤 `.안내.md.partial`에 쓰고 `os.replace`한다.
- 데이터 모양 (Task 5와 공유):
  - `meta = {"course", "term", "ecampus_id"|None, "code"|None, "section"|None, "created": "YYYY-MM-DD"}`
  - `item = {"id", "bundle", "kind", "filename", "status", "error", "week", "session", "date", "source": {"type": "ecampus", "lecture_id", "title"} | {"type": "upload", "name"}, "media", "model", "repetitions", "created"}`

`안내.md`의 정확한 문구는 아래와 같다. 값 안의 줄바꿈과 연속 공백은 `" ".join(v.split())`로 한 칸으로 합친다. 값이 없는 줄은 생략한다.
```markdown
# 강의 수집 도구 안내

이 파일은 강의 수집 도구(`_system/tools/lecture-inbox`)가 사용자가 화면에서 지정한 내용을 받아 쓴 것이다. 아래의 과목·학기·종류·주차·차시·수업일은 사용자 지정이다. 도구가 다시 쓰는 파일이므로 고치지 않는다. 처리 규칙은 `inbox/README.md`의 `강의 수집 도구 묶음` 절을 따른다.

## 과목

- 과목명: {course}
- term: {term}
- 이캠퍼스 과목 id: {ecampus_id}
- 학수번호: {code}
- 분반: {section}

## 항목

### {filename}
- 상태: 완료 | 대기 | 실패 — {error}
- 종류: 전사 | 자료 | 족보 | 과제
- 주차·차시: {week}주차 {session}차시          ← 전사만
- 출처: 이캠퍼스 강의 "{title}" | 원래 파일 "{name}"
- 수업일: {date} | 미확인                         ← 전사만
- 모델: {model}                                    ← 전사 완료만
- 반복 감지 구간: {repetitions}                    ← 전사 완료만
```
항목은 `created` 순서로 쓴다. `완료` 항목은 `filename in present`일 때만 쓴다(이미 옮긴 것은 뺀다).

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 B)**

```python
check("B", "폴더 이름", bundle.bundle_dir_name("자료/구조", date(2026, 11, 2)) == "20261102-자료_구조")
check("B", "예약 이름", bundle.safe_name("CON.pdf") == "_CON.pdf" and bundle.safe_name("a<b>.pdf") == "a_b_.pdf")
check("B", "전사 이름", bundle.transcript_name(3, 1) == "week_03_01.md")
# write_new_file
bundle.write_new_file(d / "x.pdf", b"one")
check("B", "덮어쓰기 거절", raises(FileExistsError, bundle.write_new_file, d / "x.pdf", b"two") and (d / "x.pdf").read_bytes() == b"one")
check("B", "partial 없음", not [p for p in d.iterdir() if p.name.endswith(".partial")])
# render_guide
text = bundle.render_guide(META, [DONE_PRESENT, DONE_MOVED, WAITING, FAILED], present={"week_03_01.md"})
check("B", "첫머리 문구", text.startswith("# 강의 수집 도구 안내\n\n이 파일은 강의 수집 도구"))
check("B", "옮긴 완료 항목 제외", "### week_03_02.md" not in text and "### week_03_01.md" in text)
check("B", "대기·실패 표시", "- 상태: 대기" in text and "- 상태: 실패 — 영상 다운로드에 실패했습니다." in text)
check("B", "id 없으면 줄 없음", "이캠퍼스 과목 id" not in bundle.render_guide({**META, "ecampus_id": None}, [], set()))
evil = {**WAITING, "source": {"type": "ecampus", "lecture_id": "1", "title": "제목\n### 가짜 항목"}}
check("B", "줄바꿈 주입 무력화", "\n### 가짜" not in bundle.render_guide(META, [evil], set()))
check("B", "수업일 미확인", "- 수업일: 미확인" in bundle.render_guide(META, [WAITING], set()))
# write_guide on deleted folder
bundle.write_guide(d / "20261102-자료구조", META, [WAITING])
check("B", "지운 묶음 다시 만듦", (d / "20261102-자료구조" / "안내.md").is_file())
```
`META`, `DONE_PRESENT`(week_03_01, done), `DONE_MOVED`(week_03_02, done), `WAITING`(week_03_03, `date: None`), `FAILED`(error `"영상 다운로드에 실패했습니다."`)는 테스트 파일 맨 위에 dict로 정의한다.

- [ ] **Step 2: 실패 확인** — `python _system/docs/lecture-inbox-validation/test_core.py` → 그룹 B FAIL(ImportError).
- [ ] **Step 3: `bundle.py` 구현** — Interfaces 그대로 만든다. 표준 라이브러리만 쓴다.
- [ ] **Step 4: 통과 확인** — 같은 명령으로 그룹 A·B가 모두 PASS다.
- [ ] **Step 5: 변경 확인** — `git status`, `git diff`. 커밋은 사용자 요청 시.

---

### Task 3: 전사 형식, 체크포인트, 반복 탐지

**Files:** Create `transcript.py`, `repetition.py` (`_system/tools/lecture-inbox/`). Test: 그룹 C.

**Interfaces:**
- Produces (`transcript.py`):
  - `@dataclass(frozen=True) class Segment: start: float; end: float; text: str`
  - `format_hms(seconds: float) -> str`, `to_markdown(segments: list[Segment]) -> str`: 원본 `server/lecture/transcript.py`를 이식한다.
  - `read_checkpoint(path: Path) -> list[Segment]`
    - 파일이 없으면 `[]`
    - JSON이 아닌 마지막 줄이 있으면 버리고 파일을 마지막 유효 줄 끝까지 truncate한다.
    - 중간 줄이 깨져 있으면 `ValueError`를 낸다.
  - `append_checkpoint(path: Path, seg: Segment) -> None`: `{"start","end","text"}` JSON 한 줄을 쓴 뒤 `flush()`와 `os.fsync()`를 한다.
- Produces (`repetition.py`): `find_repetition_span(segments: list[Segment]) -> tuple[int, int] | None`, 상수 `MIN_REPEAT_RUN = 3`, `SIMILARITY_THRESHOLD = 0.9`, `MIN_REPEAT_TEXT_LENGTH = 5`. 원본 `server/lecture/repetition.py`를 그대로 옮기고 import 경로와 MIT 출처 주석만 맞춘다.

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 C)**

```python
check("C", "hms", transcript.format_hms(3725.9) == "01:02:05")
check("C", "md 형식", transcript.to_markdown([S(0, 1, "안녕"), S(65.2, 70, "둘")]) == "[00:00:00] 안녕\n[00:01:05] 둘\n")
check("C", "없는 체크포인트", transcript.read_checkpoint(d / "none.jsonl") == [])
for s in (S(0, 2, "가"), S(2, 4, "나")): transcript.append_checkpoint(ck, s)
with open(ck, "ab") as f: f.write(b'{"start": 4, "end"')          # 쓰다 끊긴 줄
check("C", "잘린 줄 버림", transcript.read_checkpoint(ck) == [S(0, 2, "가"), S(2, 4, "나")])
transcript.append_checkpoint(ck, S(4, 6, "다"))
check("C", "truncate 후 이어 쓰기", len(transcript.read_checkpoint(ck)) == 3)
rep = [S(i, i + 1, "같은 말을 반복합니다") for i in range(3)]
check("C", "반복 3회 탐지", repetition.find_repetition_span([S(-1, 0, "시작")] + rep) == (1, 3))
check("C", "짧은 반복은 정상", repetition.find_repetition_span([S(i, i + 1, "네") for i in range(5)]) is None)
check("C", "2회는 반복 아님", repetition.find_repetition_span(rep[:2]) is None)
```

- [ ] **Step 2: 실패 확인** — 그룹 C FAIL.
- [ ] **Step 3: 두 모듈 구현.** `read_checkpoint`의 truncate는 바이트 기준으로 한다. 파일을 `rb`로 읽어 마지막 `b"\n"` 뒤의 내용이 유효 JSON이 아니면 `os.truncate(path, 마지막 개행 위치 + 1)`을 한다.
- [ ] **Step 4: 통과 확인** — 그룹 A~C PASS.
- [ ] **Step 5: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 4: 이어하기 전사와 반복 재디코딩

**Files:** Create `transcriber.py`. Test: 그룹 D.

**Interfaces:**
- Consumes: `transcript.Segment`, `read_checkpoint`, `append_checkpoint`, `repetition.find_repetition_span`
- Produces:
  - 상수:
    - `SAMPLE_RATE = 16000`, `MIN_TAIL_SECONDS = 1.0`, `PAD_SECONDS = 0.5`, `MAX_RETRY_SPAN_SECONDS = 180.0`
    - `REPETITION_MARK = "[⚠️ 반복 감지 - 확인 필요] "`
    - `BASE_OPTIONS = {"language": "ko", "vad_filter": True, "condition_on_previous_text": False}`
    - `RETRY_OPTIONS = ({}, {"temperature": 0.5, "compression_ratio_threshold": 2.6})` (원본의 `[]`, `-et 2.6 -tp 0.5`에 대응)
  - 엔진 계약: `engine.segments(audio, offset: float, **options) -> Iterator[Segment]`. 타임스탬프에는 이미 `offset`이 더해져 있고 `text`는 strip된 상태다.
  - `class WhisperEngine`: `__init__(self, model_dir: Path)`에서 지연 import한 `WhisperModel(str(model_dir), device="cpu", compute_type="int8")`을 만든다. `segments()`는 `model.transcribe(audio, **options)`를 감싼다.
  - `load_audio(path: Path)` → `faster_whisper.decode_audio(str(path), sampling_rate=SAMPLE_RATE)` (지연 import)
  - `transcribe(audio: Sequence[float], work: Path, engine, on_progress: Callable[[float], None] = lambda f: None) -> tuple[list[Segment], int]`: (최종 구간, 미해결 반복 수)를 돌려준다.
  - `resolve_repetitions(segments, audio, engine) -> tuple[list[Segment], int]`

`transcribe` 본문(이어하기 오프셋 규칙):
```python
def transcribe(audio, work, engine, on_progress=lambda f: None):
    duration = len(audio) / SAMPLE_RATE
    ckpt, marker = work / "segments.jsonl", work / "decoded"
    segments = read_checkpoint(ckpt)
    if not marker.exists():
        offset = segments[-1].end if segments else 0.0
        if duration - offset >= MIN_TAIL_SECONDS:
            for seg in engine.segments(audio[int(offset * SAMPLE_RATE):], offset, **BASE_OPTIONS):
                if not seg.text or seg.start < offset - 0.05:   # never rewrite checkpointed time
                    continue
                append_checkpoint(ckpt, seg)
                segments.append(seg)
                on_progress(min(seg.end / duration, 1.0))
        marker.touch()
    return resolve_repetitions(segments, audio, engine)
```

`resolve_repetitions`는 원본 `whisper.py`의 `_resolve_repetitions`/`_retry_span`을 이식하되 다음이 다르다.
- WAV 파일 대신 배열을 자른다: `clip_offset = max(0.0, first.start - PAD_SECONDS)`, `clip = audio[int(clip_offset * SR): int(min(duration, last.end + PAD_SECONDS) * SR)]`.
- 옵션마다 `engine.segments(clip, clip_offset, **{**BASE_OPTIONS, **opts})`를 호출한다.
- 재시도 예외는 `log.warning`만 남기고 다음 옵션으로 넘어간다.
- 끝내 실패하면 `Segment(first.start, last.end, REPETITION_MARK + first.text)` 하나로 바꾸고 미해결 수에 1을 더한다.
- 구간 길이가 180초를 넘으면 재시도 없이 placeholder로 바꾼다.
- 다음 탐색 시작 위치는 항상 앞으로만 움직인다(`start + len(fixed)`).

전체 파일을 한 번에 디코딩하므로 큰 파일에서 메모리 상한이 있다. 이 상한은 `# ponytail:` 주석으로 남긴다(1시간에 float32 약 230MB, 4시간 이상의 녹음이 생기면 청크 단위로 바꾼다).

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 D)** — `FakeEngine(script)`는 호출마다 `(len(audio), offset, options)`를 기록한다. `script(call_index, offset)`가 돌려준 상대 구간에 offset을 더해 yield한다. `audio = [0.0] * (SR * 60)`(60초).

```python
# D1 처음부터
segs, n = transcriber.transcribe(audio, w, eng(lambda i, o: [S(0, 5, "하나"), S(5, 9, "둘"), S(9, 12, "셋")]))
check("D", "처음부터 offset 0", eng.calls[0][1] == 0.0 and eng.calls[0][0] == len(audio))
check("D", "체크포인트 3줄·마커", len(read_checkpoint(w / "segments.jsonl")) == 3 and (w / "decoded").exists())
# D2 이어하기: 체크포인트에 끝 20.0까지 + 잘린 줄
segs, _ = transcriber.transcribe(audio, w2, e2 := eng(lambda i, o: [S(0, 4, "넷")]))
check("D", "마지막 끝 시각부터", e2.calls[0][1] == 20.0 and e2.calls[0][0] == len(audio) - 20 * SR)
check("D", "타임스탬프 원본 기준", segs[-1] == S(20.0, 24.0, "넷") and len(segs) == 3)
# D3 decoded 마커가 있으면 디코딩 안 함
check("D", "마커 있으면 재디코딩 없음", e3.calls == [])
# D4 이미 끝까지 됨 (마지막 끝 59.5초, 60초 파일)
check("D", "남은 꼬리 1초 미만이면 호출 없음", e4.calls == [] and (w4 / "decoded").exists())
# D5 반복 해결
check("D", "재시도 offset은 start-0.5", e5.calls[1][1] == 9.5 and n5 == 0 and not any(s.text.startswith(transcriber.REPETITION_MARK) for s in segs5))
# D6 반복 미해결
check("D", "미해결 표시 한 줄", n6 == 1 and sum(s.text.startswith(transcriber.REPETITION_MARK) for s in segs6) == 1 and len(e6.calls) == 1 + len(transcriber.RETRY_OPTIONS))
# D7 180초 넘는 반복
check("D", "긴 구간은 재시도 없음", len(e7.calls) == 1 and n7 == 1)
# D8 재시도 예외는 다음 옵션으로
check("D", "재시도 예외 흡수", n8 == 0 and len(e8.calls) == 3)
# D9 offset 이전 구간은 버림
check("D", "체크포인트 이전 시간 무시", all(s.start >= 19.95 for s in segs9[2:]))
```

- [ ] **Step 2: 실패 확인** — 그룹 D FAIL.
- [ ] **Step 3: `transcriber.py` 구현** — 위 본문과 Interfaces를 따른다. faster-whisper import는 `WhisperEngine.__init__`과 `load_audio` 안에서만 한다.
- [ ] **Step 4: 통과 확인** — 그룹 A~D PASS. 시스템 Python 3.14에서 돈다(numpy를 쓰지 않음).
- [ ] **Step 5: 실제 엔진 smoke 확인** — `uv run --project _system/tools/lecture-inbox python -c "import transcriber, faster_whisper; print(faster_whisper.__version__)"`(작업 디렉터리는 도구 폴더) → `1.2.1`.
- [ ] **Step 6: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 5: 작업 상태, 다음 작업 선택, 워커, 절전 방지

**Files:** Create `jobs.py`. Test: 그룹 E.

**Interfaces:**
- Consumes:
  - `bundle.write_new_file`, `bundle.write_guide`
  - `transcript.to_markdown`
  - `transcriber.transcribe`
  - `school.UserError`, `school.SchoolExpired` (Task 6에서 정의. 이 Task에서는 `school.py`에 두 예외 클래스만 먼저 만든다)
- Produces:
  - 상태 상수: `DOWNLOAD_WAIT = "download-wait"`, `DOWNLOADING = "downloading"`, `TRANSCRIBE_WAIT = "transcribe-wait"`, `TRANSCRIBING = "transcribing"`, `DONE = "done"`, `FAILED = "failed"`
  - 오류 문구: `NO_SPEECH = "인식된 음성이 없습니다. 녹음 파일을 확인해 주세요."`, `NAME_TAKEN = "같은 이름의 파일이 이미 묶음에 있습니다."`
  - 예외: `class StateError(Exception)`, `class ConflictError(Exception)`
  - `class Store`. 모든 메서드는 `threading.Lock`으로 보호하고, 바꾸는 메서드는 모두 저장한다.
    - `Store(path: Path)`
      - 로드할 때 `DOWNLOADING`은 `DOWNLOAD_WAIT`로, `TRANSCRIBING`은 `TRANSCRIBE_WAIT`로 되돌린다.
      - JSON이 깨졌으면 `StateError`를 내고 파일은 건드리지 않는다.
      - 파일 형식은 `{"version": 1, "bundles": {name: meta}, "items": [item]}`이다.
    - `save()`: `jobs.json.tmp`에 쓴 뒤 `os.replace`한다.
    - `add_bundle(name: str, meta: dict) -> None`: 이미 있는데 `(course, term, ecampus_id)`가 다르면 `ConflictError`
    - `add_item(**fields) -> dict`: `id = secrets.token_hex(6)`, `created`는 ISO 시각
    - `find(item_id) -> dict`(없으면 `KeyError`), `update(item_id, **fields) -> dict`, `remove(item_id) -> dict`
    - `items_in(bundle: str) -> list[dict]`
    - `reserved_names(bundle: str, folder: Path) -> set[str]`: DONE이 아닌 항목의 filename과 폴더의 파일 이름의 합집합
  - `next_item(items: list[dict], logged_in: bool) -> dict | None`: 로그인 상태면 `DOWNLOAD_WAIT`를 먼저 고른다. 아니면 `TRANSCRIBE_WAIT`를 고른다. 같은 상태끼리는 `created` 순서다.
  - `waiting_login(items) -> int`
  - `keep_awake(active: bool, set_state: Callable[[int], int] | None = None) -> None`
    - 기본 `set_state`는 `ctypes.windll.kernel32.SetThreadExecutionState`이고, Windows가 아니면 아무것도 하지 않는다.
    - 실행 상태는 스레드별로 적용되므로 반드시 워커 스레드에서 부른다.
  - `class Worker`:
    - 생성자: `Worker(store, inbox: Path, work_root: Path, *, model: Callable[[], str], download: Callable[[str, Path], None], engine_factory: Callable[[str], object], load_audio: Callable[[Path], Sequence[float]], set_state=None)`
    - 공개 속성: `school: SchoolSession | None`, `progress: dict[str, str]`(메모리 전용)
    - 메서드: `wake()`, `start()`(daemon 스레드), `run_once() -> bool`(처리했으면 True, 테스트용)
  - `meta(bundle)` 조회는 `store.bundles[bundle]`로 한다.

`run_once` 규칙:
- **할 일이 없을 때:** `keep_awake(False)` 후 False를 돌려준다. 할 일이 있으면 `keep_awake(True)`부터 한다.
- **다운로드 작업:**
  1. `DOWNLOADING`으로 바꾼다.
  2. `stream, _ = self.school.stream(lecture_id)`
  3. `download(stream, work/id/"video.mp4")`
  4. 성공하면 `media`를 기록하고 `TRANSCRIBE_WAIT`로 바꾼다.
  5. `SchoolExpired`면 `DOWNLOAD_WAIT`로 되돌리고 `self.school = None`.
  6. `UserError`면 `FAILED`와 `str(e)`.
- **전사 작업:**
  1. `item.model`이 없으면 `model()`로 기록한다. 이어서 할 때는 기록된 모델을 쓴다.
  2. `TRANSCRIBING`으로 바꾸고 `progress[id] = "모델 준비 중"`.
  3. `engine_factory(model)`. 같은 모델이면 엔진을 재사용한다.
  4. `transcribe(load_audio(media), work/id, engine, on_progress)`
  5. 결과가 0줄이면 `FAILED NO_SPEECH`(work 폴더는 남김).
  6. `write_new_file(inbox/bundle/filename, to_markdown(segs).encode("utf-8"))`. `FileExistsError`면 `FAILED NAME_TAKEN`(체크포인트 유지).
  7. 성공하면 `DONE`과 `repetitions=n`을 기록하고 `shutil.rmtree(work/id)`로 받은 영상과 업로드 사본을 지운다. 사용자 PC의 원래 파일은 이 도구가 건드릴 수 없다.
- **그 밖의 예외:** `FAILED`, `"작업 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요."`, `log.exception`.
- 상태가 바뀔 때마다 `write_guide(inbox/bundle, meta, store.items_in(bundle))`를 부른다.

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 E)** — fake 엔진, fake 다운로드, `load_audio=lambda p: [0.0] * SR * 30`, `set_state` 기록용 리스트를 쓴다.

```python
check("E", "저장 왕복·tmp 없음", Store(p).items == st.items and not p.with_name("jobs.json.tmp").exists())
p.write_text("{broken", encoding="utf-8")
check("E", "깨진 상태 파일은 거부·보존", raises(StateError, Store, p) and p.read_text(encoding="utf-8") == "{broken")
check("E", "재시작 시 진행 중 상태 복귀", [i["status"] for i in Store(p2).items] == [DOWNLOAD_WAIT, TRANSCRIBE_WAIT])
check("E", "다른 학기 같은 묶음 거절", raises(ConflictError, st.add_bundle, "20261102-자료구조", {**META, "term": "2026-1"}))
check("E", "로그인 시 다운로드 먼저", next_item(ITEMS, True)["status"] == DOWNLOAD_WAIT)
check("E", "비로그인 시 전사만", next_item(ITEMS, False)["status"] == TRANSCRIBE_WAIT and waiting_login(ITEMS) == 1)
keep_awake(True, rec.append); keep_awake(False, rec.append)
check("E", "절전 방지 플래그", rec == [0x80000001, 0x80000000])
# 워커: 업로드 전사 성공
check("E", "전사 파일·안내 완료", (bdir / "week_03_01.md").read_text(encoding="utf-8").startswith("[00:00:00] ") and "- 상태: 완료" in (bdir / "안내.md").read_text(encoding="utf-8"))
check("E", "성공 후 work 삭제", not (work / item_id).exists() and st.find(item_id)["repetitions"] == 0)
check("E", "작업 후 절전 해제", rec[-1] == 0x80000000)
# 0줄
check("E", "무음은 실패", st.find(i2)["error"] == NO_SPEECH and not (bdir / "week_03_02.md").exists() and (work / i2).exists())
# 이름 충돌
check("E", "최종 쓰기 충돌은 실패·기존 보존", st.find(i3)["error"] == NAME_TAKEN and (bdir / "week_03_03.md").read_bytes() == b"user")
# 모델 고정
check("E", "이어하기는 기록된 모델", factory_calls == ["large-v3"])   # settings는 중간에 turbo로 바뀜
# 다운로드
check("E", "비로그인이면 다운로드 안 함", not w.run_once() or st.find(d1)["status"] == DOWNLOAD_WAIT)
check("E", "다운로드 성공 → 전사 대기", st.find(d1)["status"] == TRANSCRIBE_WAIT and st.find(d1)["media"].endswith("video.mp4"))
check("E", "세션 만료면 대기로", st.find(d2)["status"] == DOWNLOAD_WAIT and w.school is None)
check("E", "실패 메시지에 URL 없음", "https://" not in st.find(d3)["error"])
check("E", "같은 이름 예약", "week_03_04.md" in st.reserved_names(B, bdir))
```

- [ ] **Step 2: 실패 확인** — 그룹 E FAIL.
- [ ] **Step 3: `jobs.py` 구현** (+ `school.py`에 `UserError`, `SchoolExpired`만 먼저 만든다).
- [ ] **Step 4: 통과 확인** — 그룹 A~E PASS.
- [ ] **Step 5: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 6: 세종대 연동 (`school.py`)

**Files:** Modify/complete `_system/tools/lecture-inbox/school.py`. Test: 그룹 F.

**Interfaces:**
- Produces:
  - 원본 `server/school.py` 전체를 그대로 이식한다: `SCHOOL`, `UserError`, `SchoolExpired`, `CourseParser`, `LectureParser`, `PlayerParser`, `extract_stream`, `SchoolRedirects`, `SchoolSession`(`page`, `login`, `authenticated_page`, `courses(year="all", semester="all")`, `lectures(id)`, `stream(id) -> tuple[str, str]`). 원본의 `lecture_id`와 `safe_name`은 이식하지 않는다(`safe_name`은 bundle에 있다).
  - 추가: `to_term(year: str, semester: str) -> str | None`
    - 연도는 `^\d{4}$`
    - 학기 매핑: `"1학기"|"10" → "1"`, `"2학기"|"20" → "2"`, `"여름"`을 포함하거나 `"11"` → `"summer"`, `"겨울"`을 포함하거나 `"21"` → `"winter"`
    - 그 밖은 None (추측하지 않는다)
  - 추가: `suggest_week(title: str) -> tuple[int | None, int | None]`
    - 주차: `(\d{1,2})\s*주차`
    - 차시: `(\d{1,2})\s*(?:차시|교시)`
    - 값 범위 1~99

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 F)** — 원본 `server/test_app.py`의 `COURSES_HTML`, `LECTURES_HTML`을 그대로 가져온다.

```python
check("F", "과목 파싱·외부·중복 제외", parse_courses(COURSES_HTML) == [{"id": "42", "name": "자료 & 구조", "year": "2026", "semester": "2학기"}])
check("F", "강의 파싱·accesshide 제외", [(l["id"], l["title"]) for l in parse_lectures(LECTURES_HTML)] == [("123", "1주차 소개")])
check("F", "m3u8 추출", school.extract_stream(player('{"sources": {"src": "https://cdn.example/v/index.m3u8"}}'))[0] == "https://cdn.example/v/index.m3u8")
check("F", "http 거절", raises(school.UserError, school.extract_stream, player('{"sources": {"src": "http://cdn.example/index.m3u8"}}')))
check("F", "자격증명 URL 거절", raises(school.UserError, school.extract_stream, player('{"sources": {"src": "https://u:p@cdn.example/index.m3u8"}}')))
check("F", "외부 리다이렉트 차단", raises(school.UserError, school.SchoolRedirects().redirect_request, req, None, 302, "", {}, "https://evil.example/login"))
check("F", "로그인 실패 메시지에 비밀번호 없음", "pw-secret-123" not in login_error_text)  # page를 patch해 /login/index.php 반환
check("F", "목록 경로", calls == ["/local/ubion/user/index.php?year=all&semester=all"])
for (y, s), want in {("2026", "2학기"): "2026-2", ("2026", "1학기"): "2026-1", ("2026", "여름계절수업"): "2026-summer",
                     ("2026", "겨울계절수업"): "2026-winter", ("2026", "20"): "2026-2", ("26", "2학기"): None, ("2026", "특별학기"): None}.items():
    check("F", f"term {y}/{s}", school.to_term(y, s) == want)
check("F", "주차 제안", school.suggest_week("3주차 1차시 자료구조 개요") == (3, 1) and school.suggest_week("1주차 소개") == (1, None) and school.suggest_week("오리엔테이션") == (None, None))
```

- [ ] **Step 2: 실패 확인** — 그룹 F FAIL.
- [ ] **Step 3: 이식과 두 함수 구현** — 파일 첫머리에 출처 주석(EM-H20/lecture-inbox, 작성자 허락)을 단다.
- [ ] **Step 4: 통과 확인** — 그룹 A~F PASS.
- [ ] **Step 5: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 7: HLS 다운로더 (`hls.py`)

**Files:** Create `hls.py`. Test: 그룹 G.

**Interfaces:**
- Consumes: `school.UserError`, `config.MAX_MEDIA_BYTES`, `config.DOWNLOAD_TIMEOUT_S`
- Produces:
  - `validate_cdn(url: str, resolve=socket.getaddrinfo) -> None`: 원본 `app.validate_cdn`을 이식한다. resolver를 주입할 수 있게 한다.
  - `ffmpeg_args(ffmpeg: str, stream: str, dest: Path, referer: bool) -> list[str]`: 원본 `run_ffmpeg`의 인자를 그대로 쓴다.
  - `download_hls(stream: str, dest: Path, *, ffmpeg: str, popen=subprocess.Popen, max_bytes=MAX_MEDIA_BYTES, timeout=DOWNLOAD_TIMEOUT_S) -> None`
    1. 먼저 `validate_cdn(stream)`을 부른다.
    2. `dest.name + ".part"`에 받는다.
    3. stderr는 `tempfile.TemporaryFile`로 받고 최대 16 KiB만 읽어 `"403"`이 있는지만 본다. **로그·예외에 넣지 않는다.**
    4. 403이면 `referer=True`로 한 번 재시도한다.
    5. 크기가 `0 < size < max_bytes`일 때만 `rename`하고, 아니면 partial을 지우고 `UserError`.
    6. 시간을 넘기면 `kill`하고 `UserError("영상 받기가 2시간을 넘었습니다. 다시 시도해 주세요.")`.
  - `validate_cdn`은 DNS를 확인하는 시점과 ffmpeg가 실제로 접속하는 시점 사이에 틈이 있다. 이 상한은 `# ponytail:` 주석으로 남긴다(원본과 같은 수준이고, 필요하면 IP 고정 프록시로 바꾼다).

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 G)** — `FakePopen(rc, stderr_bytes, write=bytes|None)`은 생성될 때 `stderr` 파일 객체에 쓰고, 마지막 인자 경로에 `write`를 쓰며, 호출 인자를 기록한다.

```python
pub = lambda host, port, type=None: [(0, 0, 0, "", ("8.8.8.8", 443))]
priv = lambda host, port, type=None: [(0, 0, 0, "", ("10.0.0.5", 443))]
for bad in ("http://cdn.example/a.m3u8", "https://u:p@cdn.example/a.m3u8", "https://cdn.example:8443/a.m3u8"):
    check("G", f"거절 {bad[:20]}", raises(UserError, hls.validate_cdn, bad, pub))
check("G", "사설 IP 거절", raises(UserError, hls.validate_cdn, "https://cdn.example/a.m3u8", priv))
check("G", "공인 IP 허용", hls.validate_cdn("https://cdn.example/a.m3u8", pub) is None)
a = hls.ffmpeg_args("ffmpeg", URL, d / "v.mp4.part", False)
check("G", "필수 인자", all(x in a for x in ("-tls_verify", "1", "-c", "copy", "-fs", str(2 * 1024**3), "https,tls,tcp,crypto")))
check("G", "Referer 인자", "Referer: https://ecampus.sejong.ac.kr/\r\n" in hls.ffmpeg_args("ffmpeg", URL, d / "x", True))
# 403 → referer 재시도 성공
check("G", "403 재시도", len(calls) == 2 and "-headers" in calls[1] and (d / "v.mp4").read_bytes() == b"video" and not (d / "v.mp4.part").exists())
# 실패: stderr에 서명 URL
check("G", "오류에 URL·stderr 없음", "sig=" not in err_text and "https://" not in err_text and not (d / "f.mp4").exists())
check("G", "빈 파일은 실패", raises(UserError, ...) and not (d / "e.mp4").exists())
```
`download_hls` 안에서 `validate_cdn`을 테스트할 때는 `hls.socket.getaddrinfo`를 `unittest.mock.patch`로 공인 IP를 돌려주게 바꾼다.

- [ ] **Step 2: 실패 확인** — 그룹 G FAIL.
- [ ] **Step 3: 구현.**
- [ ] **Step 4: 통과 확인** — 그룹 A~G PASS.
- [ ] **Step 5: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 8: FastAPI 서버 (`app.py`)

**Files:** Create `app.py`. Test: `_system/docs/lecture-inbox-validation/test_app.py` (check 방식, uv로 실행, run_all 미등록).

**Interfaces:**
- Consumes:
  - `config.*`, `bundle.*`, `jobs.Store/Worker/ConflictError/상태 상수`
  - `school.SchoolSession/UserError/SchoolExpired/to_term/suggest_week`
  - `hls.download_hls`
  - `transcriber.WhisperEngine/load_audio`
  - `prereq.ffmpeg_path/ensure_model` (Task 10. 이 Task에서는 주입 기본값으로만 참조한다)
- Produces:
  - `create_app(*, root: Path = ROOT, paths: Paths | None = None, school_factory=SchoolSession, engine_factory=None, load_audio=None, start_worker: bool = True, allowed_hosts: frozenset[str] = frozenset({f"127.0.0.1:{PORT}", f"localhost:{PORT}"})) -> FastAPI`
    - `root/"SECOND-BRAIN.md"`가 없으면 `RuntimeError`
    - `app.state.store`, `app.state.worker`
  - `main(argv: list[str] | None = None) -> int` (Task 10에서 완성)
  - 미들웨어 `local_only`:
    - `Host` 헤더가 `allowed_hosts`에 없으면 403 `{"detail": "로컬 화면에서만 사용할 수 있습니다."}`
    - `/api/`로 시작하는 요청은 `X-Lecture-Inbox: 1` 헤더가 없으면 403. 사용자 정의 헤더라서 다른 출처의 요청은 preflight가 필요하고, CORS 미들웨어가 없으므로 실패한다.
    - 응답 헤더: `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`
  - `RequestValidationError` 핸들러 → 422 `{"detail": "입력 형식을 확인해 주세요."}` (원본과 같이 입력을 되풀이하지 않는다)
  - 모델:
    - `CourseBody`: `course: str(1..100)`, `term: str(pattern ^\d{4}-(1|2|summer|winter)$)`, `ecampusId: str|None(pattern ^[0-9]{1,12}$)`, `code: str|None(≤30)`, `section: str|None(≤10)`
    - `LectureRow`: `id(pattern ^[0-9]{1,12}$)`, `title(1..300)`, `week: int(1..99)`, `session: int(1..99)`, `date: date|None`
    - `LecturesBody`: `course: CourseBody`, `lectures: list[LectureRow](min 1)`
    - `LoginBody`: 원본과 같다(`studentId ^[0-9]{4,20}$`, `password: SecretStr(1..512)`)
- 라우트:

| 메서드·경로 | 동작 |
|---|---|
| `GET /` | `index.html` (FileResponse) |
| `GET /api/health` | `{"app": "lecture-inbox"}` |
| `GET /api/status` | `{"ffmpeg": bool, "model": str, "loggedIn": bool, "waitingLogin": int, "items": [public]}`. public은 item에서 `media`를 빼고 `progress`를 더한 것 |
| `POST /api/login` | `school_factory().login(...)`. 성공하면 `worker.school = s; worker.wake()`, 실패하면 401 `str(UserError)` |
| `POST /api/logout` | `worker.school = None` |
| `GET /api/courses` | 비로그인 401, `SchoolExpired`는 409, 그 밖 `UserError`는 502. 각 과목에 `term: to_term(...)`을 붙인다 |
| `GET /api/courses/{id}/lectures` | 각 강의에 `week, session = suggest_week(title)`을 붙인다 |
| `POST /api/lectures` | 묶음 등록(`ConflictError`는 409) → 요청 안 중복 또는 `reserved_names`와 겹치면 409 → `DOWNLOAD_WAIT` 항목 추가 → `write_guide` → 202 |
| `POST /api/uploads` | 아래 별도 설명 |
| `POST /api/items/{id}/retry` | `FAILED`일 때만. media가 있으면 `TRANSCRIBE_WAIT`, 없으면 `DOWNLOAD_WAIT`. 아니면 409 |
| `DELETE /api/items/{id}` | `DOWNLOAD_WAIT`, `TRANSCRIBE_WAIT`, `FAILED`만 지운다. 그 밖은 409. `work/id`를 지우고 `write_guide` |

`POST /api/uploads` 상세:
- 쿼리: `kind ∈ {recording, resource, past-exam, assignment}` 와 CourseBody 필드, recording이면 `week, session, date?` 추가
- 헤더 `X-Filename`은 퍼센트 인코딩된 UTF-8이다
- `Content-Length`가 없거나 `MAX_MEDIA_BYTES`를 넘으면 411/413. 받는 도중 넘어도 413이고 쓰던 파일을 지운다
- 본문은 `request.stream()`으로 `work/<id>/upload.part`에 받는다. python-multipart는 추가하지 않는다
- recording: `work/<id>/<safe_name(원래 이름)>`으로 옮기고 `TRANSCRIBE_WAIT`, `filename = transcript_name(week, session)`
- PDF 종류: 확장자 `.pdf`와 첫 5바이트 `b"%PDF-"`를 확인한다. 아니면 400 `"PDF만 받습니다. PPT·HWP·이미지는 PDF로 변환해 주세요."`. 맞으면 `write_new_file(inbox/bundle/safe_name(name), tmp)`(`FileExistsError`는 409), item을 `DONE`으로 하고 work 폴더를 지운다

- [ ] **Step 1: 실패하는 테스트 작성 (`test_app.py`)**
  - 가짜 루트: tmp 아래 `SECOND-BRAIN.md`와 `inbox/`
  - 설정: `create_app(root=..., paths=Paths.at(tmp/"h"), school_factory=FakeSchool, start_worker=False, allowed_hosts=frozenset({"testserver"}))`
  - `H = {"X-Lecture-Inbox": "1"}`

```python
check("H", "외부 Host 거절", c.get("/api/status", headers={**H, "host": "evil.example"}).status_code == 403)
check("H", "헤더 없는 API 거절", c.get("/api/status").status_code == 403)
r = c.post("/api/login", json={"studentId": "20261234", "password": "pw-secret-123"}, headers=H)   # FakeSchool.login이 UserError
check("H", "로그인 실패 401·비번 비노출", r.status_code == 401 and "pw-secret-123" not in r.text)
r = c.post("/api/login", json={"studentId": "abc", "password": "pw-secret-123"}, headers=H)
check("H", "422 문구 고정", r.status_code == 422 and r.json() == {"detail": "입력 형식을 확인해 주세요."})
check("H", "비로그인 목록 401", c.get("/api/courses", headers=H).status_code == 401)
# 로그인 성공 FakeSchool
check("H", "term 변환", c.get("/api/courses", headers=H).json()["courses"][0]["term"] == "2026-2")
check("H", "상태에 학번 없음", "20261234" not in c.get("/api/status", headers=H).text)
r = upload("resource", "3주차 강의자료.pdf", b"%PDF-1.7 body")
check("H", "PDF 묶음 저장", r.status_code == 202 and (bdir / "3주차 강의자료.pdf").read_bytes() == b"%PDF-1.7 body")
check("H", "안내에 자료 완료", "- 종류: 자료" in guide() and "- 상태: 완료" in guide())
check("H", "같은 PDF 409·보존", upload("resource", "3주차 강의자료.pdf", b"%PDF-other").status_code == 409 and (bdir / "3주차 강의자료.pdf").read_bytes() == b"%PDF-1.7 body")
r = upload("resource", "slides.pptx", b"PK\x03\x04")
check("H", "비PDF 거절", r.status_code == 400 and "PDF" in r.json()["detail"])
r = upload("recording", "새 녹음 12.m4a", b"\x00" * 10, week=3, session=1)
check("H", "녹음은 대기·묶음엔 없음", r.status_code == 202 and not (bdir / "week_03_01.md").exists() and "- 상태: 대기" in guide())
check("H", "같은 주차·차시 409", upload("recording", "b.m4a", b"\x00", week=3, session=1).status_code == 409)
check("H", "학기 형식 422", post_lectures(term="2026-3").status_code == 422)
check("H", "요청 내 중복 409", post_lectures(rows=[ROW(3, 2), ROW(3, 2)]).status_code == 409)
check("H", "다른 학기 같은 묶음 409", post_lectures(term="2026-1").status_code == 409)
check("H", "대기 항목 삭제", c.delete(f"/api/items/{rid}", headers=H).status_code == 200 and not (work / rid).exists())
check("H", "화면 제공", "강의 수집 도구" in c.get("/").text)
```
결과는 `PASS n / FAIL n`으로 출력한다.

- [ ] **Step 2: 실패 확인** — `uv run --project _system/tools/lecture-inbox python _system/docs/lecture-inbox-validation/test_app.py`(환경 변수 설정 상태) → FAIL. `GET /`은 Task 9 전까지 `index.html` 자리표시자 한 줄(`<title>강의 수집 도구</title>`)로 통과시킨다.
- [ ] **Step 3: `app.py` 구현.** 기본 `engine_factory`는 `lambda m: WhisperEngine(ensure_model(m, paths.models))`, 기본 `download`는 `functools.partial(download_hls, ffmpeg=ffmpeg_path() or "ffmpeg")`다. ffmpeg가 없으면 다운로드 항목을 `FAILED "ffmpeg가 없습니다. 터미널 안내대로 설치한 뒤 다시 시도해 주세요."`로 바꾼다.
- [ ] **Step 4: 통과 확인** — 같은 명령 → `FAIL 0`. `python _system/docs/lecture-inbox-validation/test_core.py`도 계속 PASS.
- [ ] **Step 5: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 9: 화면 (`index.html`)

**Files:** Create `_system/tools/lecture-inbox/index.html` (CSS·JS 인라인, 외부 리소스 없음). Test: `test_app.py`의 "화면 제공" 확인과 수동 확인.

**Interfaces:** Consumes Task 8의 라우트와 응답 키(`ffmpeg, model, loggedIn, waitingLogin, items[].{id,filename,kind,status,error,progress,bundle}`).

화면 요구사항은 한 화면에 위에서 아래 순서로 놓는다.
1. **과목**
   - 세종대 로그인 폼. 요청을 보낸 직후 비밀번호 칸을 비운다.
   - 과목 목록. 각 과목에 term을 표시하고, `term == null`이면 학기 선택 칸을 띄운다.
   - 또는 직접 입력: 과목명, term 선택(올해·작년 × `1, 2, summer, winter`), 학수번호·분반(선택).
2. **넣을 것**
   - 강의 목록 체크박스. 체크하면 주차·차시·수업일 칸이 열린다. `suggest_week` 값은 미리 채우되 "확인" 체크를 해야 그 행이 유효하다.
   - 녹음·영상 드롭존. 파일마다 주차·차시를 받고, 수업일은 `File.lastModified` 날짜를 제안한다(비울 수 있음).
   - PDF 드롭존. 파일마다 종류(자료/족보/과제)를 고른다. `.pdf`가 아니면 즉시 "PDF로 변환해 주세요"를 표시하고 목록에 넣지 않는다.
3. **실행** 버튼. 미확인 행이나 빈 주차·차시가 있으면 비활성이다. 누르면 `/api/lectures` 한 번, 그다음 파일을 하나씩 `/api/uploads`로 보낸다.
4. **진행**
   - 2초마다 `/api/status`를 폴링한다.
   - 항목별 상태를 대기 / 받는 중(N MB) / 전사 중(N%) / 완료 / 실패: 이유로 표시하고, 실패 항목에는 다시 시도·삭제 버튼을 둔다.
   - `waitingLogin > 0`이면 "다시 로그인하면 남은 N개를 받습니다"를 띄운다.
   - `ffmpeg == false`면 "이캠퍼스 받기에는 ffmpeg가 필요합니다: `winget install Gyan.FFmpeg`"를 띄운다.
5. **결과** — 남은 항목이 없으면 "Claude Code에서 '넣어줘' 하세요"를 표시한다.

모든 `fetch`에 `X-Lecture-Inbox: 1`을 붙이고, 업로드에는 `X-Filename: encodeURIComponent(name)`도 붙인다. 서버 문자열은 **`textContent`로만** 넣는다. 강의 제목에 의한 XSS를 막기 위해 서버 값으로 `innerHTML`을 쓰지 않는다. 브라우저 저장소는 쓰지 않는다.

- [ ] **Step 1: 자리표시자를 실제 화면으로 교체.**
- [ ] **Step 2: 자동 확인** — `test_app.py` 재실행 → `FAIL 0`.
- [ ] **Step 3: 수동 확인 (로그인 없이)** — Task 10 이후 `start.cmd`로 띄워 확인한다: 직접 입력 과목 + PDF 1개 + 짧은 녹음 1개 → PDF는 바로 완료, 녹음은 대기에서 전사 중 %를 거쳐 완료. 브라우저 개발자 도구 콘솔에 오류가 없다.
- [ ] **Step 4: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 10: ffmpeg·모델 준비, 실행 스크립트, 도구 README

**Files:** Create `prereq.py`, `start.cmd`; complete `app.main`, `_system/tools/lecture-inbox/README.md`. Test: 그룹 P(`test_core.py`).

**Interfaces:**
- Produces:
  - `WINGET_COMMAND = ["winget", "install", "--id", "Gyan.FFmpeg", "-e"]`
  - `ffmpeg_path(env=os.environ, which=shutil.which) -> str | None`: `which("ffmpeg")`가 있으면 그것, 없으면 `LOCALAPPDATA\Microsoft\WinGet\Links\ffmpeg.exe`가 있으면 그 경로. winget 설치 직후에는 현재 프로세스의 PATH가 갱신되지 않기 때문이다.
  - `offer_ffmpeg_install(ask=input, run=subprocess.run) -> bool`: 명령을 그대로 출력하고 "지금 설치할까요? [y/N]"를 묻는다. `y`/`Y`일 때만 `run(WINGET_COMMAND)`.
  - `ensure_model(name: str, models_dir: Path, download=None) -> Path`: `models_dir/name/"model.bin"`이 있으면 그 폴더를 돌려준다. 없으면 `faster_whisper.download_model(name, output_dir=str(models_dir/name))`(지연 import).
  - `app.main()`:
    1. `GET http://127.0.0.1:4319/api/health`(헤더 포함)가 `{"app": "lecture-inbox"}`를 돌려주면 브라우저만 열고 `0`을 돌려준다. 같은 상태 파일을 쓰는 두 번째 워커를 막기 위해서다.
    2. 포트를 다른 프로그램이 쓰고 있으면 오류 메시지를 내고 `1`을 돌려준다.
    3. `ffmpeg_path()`가 None이면 `offer_ffmpeg_install()`을 부른다. 거절해도 계속한다(업로드 전사는 ffmpeg 없이 된다).
    4. `load_settings`
    5. `threading.Timer(1.5, webbrowser.open, ["http://127.0.0.1:4319/"])`
    6. `uvicorn.run(app, host=HOST, port=PORT, log_level="info")`
  - `start.cmd` (정확한 내용):
    ```bat
    @echo off
    setlocal
    set "UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\lecture-inbox\venv"
    uv run --locked --project "%~dp0." python "%~dp0app.py" %*
    ```

- [ ] **Step 1: 실패하는 테스트 작성 (그룹 P)**

```python
check("P", "PATH 우선", prereq.ffmpeg_path({"LOCALAPPDATA": t}, which=lambda n: "C:/x/ffmpeg.exe") == "C:/x/ffmpeg.exe")
(links := pathlib.Path(t, "Microsoft/WinGet/Links")).mkdir(parents=True); (links / "ffmpeg.exe").write_bytes(b"")
check("P", "WinGet Links 대체", prereq.ffmpeg_path({"LOCALAPPDATA": t}, which=lambda n: None) == str(links / "ffmpeg.exe"))
check("P", "없으면 None", prereq.ffmpeg_path({"LOCALAPPDATA": t2}, which=lambda n: None) is None)
ran = []; prereq.offer_ffmpeg_install(ask=lambda q: "n", run=ran.append)
check("P", "거절하면 실행 안 함", ran == [])
prereq.offer_ffmpeg_install(ask=lambda q: "y", run=ran.append)
check("P", "동의하면 winget", ran == [prereq.WINGET_COMMAND])
check("P", "모델 있으면 안 받음", prereq.ensure_model("large-v3", m, download=boom) == m / "large-v3")   # model.bin 미리 생성
got = []; prereq.ensure_model("large-v3-turbo", m, download=lambda n, output_dir: got.append((n, output_dir)) or output_dir)
check("P", "없으면 받음", got == [("large-v3-turbo", str(m / "large-v3-turbo"))])
```

- [ ] **Step 2: 실패 확인 → Step 3: 구현 → Step 4: 통과 확인** — `python _system/docs/lecture-inbox-validation/test_core.py` → `FAIL 0`.
- [ ] **Step 5: 도구 README 작성**
  - 설치 순서: uv → 첫 실행 → ffmpeg 동의 → 모델은 첫 전사 때 약 3GB를 자동으로 받으며 화면에 "모델 준비 중"으로 보인다.
  - 실행 명령: 저장소 루트에서 `_system\tools\lecture-inbox\start.cmd`
  - 데이터 위치: `%LOCALAPPDATA%\lecture-inbox\{venv,models,work,state,settings.json}`
  - 모델 바꾸기: `settings.json`의 `"model"`
  - 도구는 `inbox/`에만 쓴다는 점
  - 검사 명령 2개
  - 문제 해결: `import ctranslate2`가 DLL 오류로 실패하면 사용자 동의 후 `winget install Microsoft.VCRedist.2015+.x64`
- [ ] **Step 6: 수동 실행 확인**
  - `_system\tools\lecture-inbox\start.cmd`를 실행하면 브라우저가 `http://127.0.0.1:4319/`를 연다.
  - 같은 명령을 다시 실행하면 서버가 하나만 뜨고 브라우저만 열린다.
  - `netstat -ano | findstr 4319` 결과가 `127.0.0.1:4319`만 보인다.
  - 저장소 안에 `.venv`가 없다.
- [ ] **Step 7: 변경 확인** — `git status`에 도구·검사 파일만 보인다. 커밋은 사용자 요청 시.

---

### Task 11: template 문서 변경 (spec 6.3, 6.7)

**Files:**
- Modify: `SECOND-BRAIN.md` (§1 `### inbox/` 26-33행, `공통 준비 절차` 1단계 352행, `## L5` 582·588·612행 부근)
- Modify: `inbox/README.md`, `_system/workflows/l5-fact-conflict-reconciliation.md`, `.agents/skills/check-conflict/SKILL.md`, `.agents/skills/capture/SKILL.md`
- Modify: `_system/docs/README.md`(폴더 표), `README.md`(Repository Structure 또는 Usage에 짧은 절), `PROJECT-STATUS.md`(3절에 한 항목)
- 바꾸지 않음: `.claude/skills/*/SKILL.md` 스텁. 정본만 가리키며, `description`을 바꾸지 않으므로 `check_skills.py`의 정본·스텁 비교가 유지된다.

**Interfaces:** Consumes `bundle.py`의 `안내.md` 문구와 상태 이름(`완료`/`대기`/`실패`).

- [ ] **Step 1: `inbox/README.md`에 `## 강의 수집 도구 묶음` 절 추가** (규격 "해당 없음" 대신 이 절을 가리킨다). 담을 내용:
  - 형식: `<YYYYMMDD>-<과목명>/`, `안내.md`, `week_NN_MM.md`(전사), 원래 이름의 PDF. 과목 하나당 폴더 하나다.
  - `안내.md`는 도구가 사용자 지정을 받아 쓴 파일이다. 과목명·term·종류·주차·차시·수업일은 공통 준비 절차의 "사용자 지정" 근거다.
  - Claude는 `완료` 항목만 처리하고, `대기`·`실패` 항목은 건너뛰었다고 보고한다.
  - Claude는 `안내.md`를 고치지 않는다. `.`으로 시작하는 `.partial` 파일은 쓰는 중인 파일이므로 무시한다.
  - `완료`인데 묶음에 파일이 없으면 이미 옮긴 것이다. 로그로 확인하고 다시 처리하지 않는다.
  - 종류별 레이어: 전사 → L1, 자료 → L2, 족보 → L3, 과제 → L5 0단계.
  - `안내.md`에 `대기` 항목이 없고 `안내.md` 말고는 파일이 남지 않으면(모두 `raw/`로 옮겼거나, 같은 내용이 이미 `raw/`에 있어 로그에 남겼으면) Claude가 묶음 폴더를 지운다. 로그는 `finalize-run`에 메모 "inbox 묶음 <폴더> 정리"로 남긴다. 새 작업 코드는 만들지 않는다. ※ 같은 내용 처리는 "Main 결정 필요" 2번의 가정이다.
- [ ] **Step 2: `SECOND-BRAIN.md` 수정**
  - §1 `### inbox/`에 한 줄을 추가한다: "강의 수집 도구가 만든 묶음(`안내.md`가 있는 폴더)의 처리 규칙은 [`inbox/README.md`](inbox/README.md)의 `강의 수집 도구 묶음` 절을 따른다."
  - 공통 준비 절차 1단계 끝에 한 문장을 추가한다: "`inbox/`의 강의 수집 도구 묶음에 있는 `안내.md`는 사용자 지정이다. 그 과목·학기가 기존 CRS와 다를 때만 사용자에게 묻는다." 2단계는 "같은 근거"이므로 그대로 둔다.
  - L5 **입력**에 "`inbox/`의 과제 원본(PDF)"을 추가한다.
  - L5 **처리 순서** 맨 앞에 0단계를 넣는다: "0. **원본 보존.** 입력이 `inbox/`의 과제 PDF면 공통 준비 절차로 CRS를 확보한 뒤 원본을 `raw/<term>/<course-slug>/assignments/`로 옮긴다. 같은 내용이 `raw/`에 이미 있으면 다시 복사하지 않는다. 로그에 `preserve-source`를 남긴다. 이후 단계가 실패해도 이 결과는 유지한다." 기존 1~8 번호는 그대로 둔다.
  - L5 **재실행 시 처리**에 "원본이 이미 보존돼 있으면 다시 복사하지 않는다"를 추가한다.
- [ ] **Step 3: assignment 스키마에 선택 필드 `source` 추가 (사용자 결정 (b), 2026-11-02)**
  - 호환성 원칙:
    - `source`는 **선택 필드**다. 기본값은 `null`이다. 과제 PDF 없이 수업·공지에서만 나온 과제는 `null`로 둔다.
    - 기존 ASM 노트와 fixture는 고치지 않아도 유효하다.
    - 필수 필드 집합(`{"submission_method"}`)은 바꾸지 않는다.
  - `_system/schemas/assignment.md`:
    - frontmatter 예시의 `sources: []` 다음 줄에 `source: null`을 넣는다.
    - Fields 표에 한 행을 넣는다: `| source | 아니오 | 과제 원본 PDF의 저장소 루트 기준 경로(raw/<term>/<course-slug>/assignments/…) 또는 접근 가능한 외부 참조. 원본 파일이 없으면 null. sources(노트 ID 목록)와 혼용하지 않는다. |`
  - `_system/templates/assignment.md`: frontmatter에 `source: null`을 넣는다. `sources` 다음 줄이다.
  - `_system/docs/template-validation/build_filled.py`의 assignment 샘플에 `source="raw/2026-2/general-physics-1/assignments/hw03.pdf"`를 넣는다. 샘플이 가리키는 파일이 fixture에 없어 검사가 깨지면, 이 단계를 `source=None`으로 바꾼다.
    - 그다음 `build_filled.py`를 다시 돌려 `filled/` 샘플을 재생성한다. 이 스크립트는 `run_all.py`가 부르지 않는 생성기이므로 여기서 명시적으로 실행한다.
  - `_system/workflows/l8-maintenance.md` 6번의 로컬 `source` 존재 검사 명령을 고친다. `source: null`이 "null"이라는 경로로 잡히지 않도록 `null` 값을 제외한다(예: `^source: \K(?!http|null$).+`). 검사 설명에 "assignment의 `source: null`은 원본 파일이 없다는 뜻이므로 누락으로 보고하지 않는다"를 한 줄 덧붙인다.
  - `SECOND-BRAIN.md` L5:
    - 0단계 끝에 "옮긴 경로를 해당 ASM의 `source`에 적는다"를 덧붙인다.
    - **완료 조건**에 "입력이 과제 PDF면 원본이 `raw/<term>/<course-slug>/assignments/`에 있고 ASM `source`가 그 경로를 가리킨다. 원본 파일이 없는 과제는 `source: null`이다."를 추가한다.
  - `_system/docs/plan/03-DATA-MODEL.md`에 assignment 필드 표가 있으면 같은 행을 추가한다.
  - Run: `python _system/docs/template-validation/check_templates.py`, `python _system/docs/template-validation/check_filled_notes.py`, `python _system/docs/integration-test/check_scenarios.py`
  - Expected: 셋 모두 FAIL 0이다.
- [ ] **Step 4: L5 워크플로 문서와 스킬 정렬**
  - `l5-fact-conflict-reconciliation.md`: "한눈에 보기" 입력 행에 inbox 과제 PDF를 추가한다. `## 2. 실행 체크리스트` 맨 앞에 `- [ ] **0. 원본 보존.** inbox 과제 PDF면 SECOND-BRAIN.md L5 0단계를 따른다.`를 넣는다. `## 7. 로그 기록` 예시에 `- 2026-09-08 18:43 | L5 | preserve-source | raw/2026-2/general-physics-2/assignments/hw3.pdf | done | inbox 과제 원본 보존` 한 줄을 넣는다. 완료 조건에는 Step 3의 결정 문구를 넣는다.
  - `.agents/skills/check-conflict/SKILL.md`: `## When to use`에 "`inbox/`의 과제 PDF가 들어왔을 때(워크플로 0단계)"를 한 줄 추가한다. `description`과 `SAFETY` 문구("자동 덮어쓰기 금지", "superseded_by")는 그대로 둔다.
  - `.agents/skills/capture/SKILL.md`:
    - 라우팅 표의 L5 행을 "과제·시험·운영 공지, 과제 원본 PDF"로 바꾼다.
    - Execution 2단계 앞에 한 줄을 넣는다: "`inbox/`의 강의 수집 도구 묶음이면 `안내.md`의 항목마다 종류대로 보낸다. 규칙은 [`inbox/README.md`](../../../inbox/README.md)를 따른다."
    - 5단계("확정할 수 없으면 멈춘다")에 "`안내.md`는 사용자 지정이다"를 덧붙인다.
    - `데이터` 안전 문구는 그대로 둔다.
- [ ] **Step 5: 사용자 문서**
  - `_system/docs/README.md` 표에 `specs/`(설계 문서), `plans/`(구현 계획), `lecture-inbox-validation/`(링크) 세 행을 추가한다. 기존 `plan/`·`template-validation/`처럼 하위 README 없이 표로 설명하는 관례를 따른다.
  - `README.md`에 "강의 수집 도구" 짧은 절을 넣는다(실행 명령 한 줄, 도구 README 링크).
  - `PROJECT-STATUS.md` 3절에 한 항목을 넣는다(구현됨, 실제 계정 검증은 Task 13 결과로 갱신).
- [ ] **Step 6: 검증** — `python _system/docs/run_all.py`
  - Expected: 기존 스위트와 `lecture-inbox 검사`가 모두 PASS다. Skill 런타임만 workspace가 없으면 SKIP(기존과 같음).
  - `python _system/docs/skill-validation/check_skills.py`의 `===== PROBLEMS =====` 아래가 `none`이다.
- [ ] **Step 7: 변경 확인** — `git diff SECOND-BRAIN.md inbox/README.md _system/workflows .agents/skills` 범위 밖 변경이 없다. 커밋은 사용자 요청 시.

---

### Task 12: 모델 비교 (사용자와 함께, spec 6.6)

**Files:** Create `_system/tools/lecture-inbox/compare.py`. 출력은 `%LOCALAPPDATA%\lecture-inbox\compare\`에만 쓴다.

**Interfaces:**
- Consumes: `prereq.ensure_model`, `transcriber.WhisperEngine/load_audio/transcribe`, `transcript.to_markdown`
- Produces: `python compare.py <media> [--seconds 300] [--models large-v3 large-v3-turbo]`
  - 모델마다 다음을 한다:
    1. 타이머 전에 `ensure_model`(다운로드 시간은 측정에서 뺀다)
    2. `audio[:seconds*SR]`
    3. 임시 work 폴더로 `transcribe`
    4. `compare/<model>.md`를 쓴다
    5. 엔진을 `del`하고 `gc.collect()`
  - 마지막에 표 `모델 | 소요 초 | 배속(소요/길이) | 줄 수 | 반복 감지`를 출력한다.

- [ ] **Step 1: `compare.py` 작성** (테스트 없음. 측정용 일회성 스크립트이고 로직은 Task 4에서 검증됐다).
- [ ] **Step 2: 사용자의 실제 강의 파일 5분으로 실행** — `uv run --locked --project _system/tools/lecture-inbox python _system/tools/lecture-inbox/compare.py "<사용자 파일>"`(환경 변수 설정 상태).
- [ ] **Step 3: Qwen3-ASR 확인 (최대 30분)**
  - vault 밖 임시 uv 환경(`%LOCALAPPDATA%\lecture-inbox\qwen-try`)에서 공식 패키지가 Windows CPU에 CUDA·vLLM 없이 설치되는지 본다.
  - 설치되고 같은 5분 클립이 large-v3 소요의 3배 안에 끝나면 표에 넣는다.
  - 아니면 막힌 지점(예: CUDA 전용 의존성, CPU 경로 없음, 시간 초과)을 그대로 보고한다. 도구 의존성에는 넣지 않는다.
- [ ] **Step 4: 두 결과 파일을 나란히 사용자에게 보여 주고 기본 모델을 받는다.** 바꾸기로 하면 `settings.json`만 바꾼다. 코드 기본값 `DEFAULT_MODEL`은 사용자가 원할 때만 바꾸고, 바꾸면 README와 Global Constraints도 함께 바꾼다.
- [ ] **Step 5: 변경 확인.** 커밋은 사용자 요청 시.

---

### Task 13: 실제 계정 수동 E2E (사용자와 함께, spec 8)

**Files:** 없음. 결과로 `PROJECT-STATUS.md`의 해당 항목만 갱신한다.

- [ ] **Step 1 (기준 1):** 새 터미널에서 저장소 루트의 `_system\tools\lecture-inbox\start.cmd`를 실행한다. ffmpeg 설치를 묻고, 동의하면 winget이 실행되고, 화면이 열린다.
- [ ] **Step 2 (기준 2):**
  - 사용자가 직접 학번·비밀번호를 입력해 로그인한다. 과목 목록과 term이 표시되고, 강의 목록이 나오고, 강의 1개를 받는다.
  - **TLS 확인:** `-tls_verify 1`에서 실패하면 검증을 끄지 않고, 오류 원인(인증서 저장소 등)만 Main에 보고한다.
  - 터미널 로그와 `jobs.json`에서 학번·`.m3u8`·`sig=`를 검색했을 때 없다: `Select-String -Path "$env:LOCALAPPDATA\lecture-inbox\state\jobs.json" -Pattern 'm3u8|sig='` 결과가 비어 있다.
- [ ] **Step 3 (기준 3):** 폰 녹음 1개를 `large-v3`로 전사한다. `inbox/<묶음>/week_NN_MM.md`의 모든 줄이 `^\[\d{2}:\d{2}:\d{2}\] `로 시작한다.
- [ ] **Step 4 (기준 4):**
  - 긴 녹음을 전사하는 도중 터미널 창을 닫았다가 다시 실행한다. `segments.jsonl` 줄 수가 유지되고, 이어서 끝난다. 결과의 첫 구간이 0초부터 다시 나오지 않는다.
  - 작업 중 `powercfg /requests`의 SYSTEM에 python이 보이고, 끝나면 사라진다.
- [ ] **Step 5 (기준 5):** PDF 자료·족보·과제를 하나씩 올린다. 묶음에 원래 이름으로 들어가고, `안내.md`에 종류와 `완료`가 적힌다.
- [ ] **Step 6 (기준 6):**
  - Claude Code에서 "넣어줘"라고 한다. Claude가 과목·학기를 되묻지 않고 L1/L2/L3(과제는 L5 0단계)를 진행한다.
  - `대기` 항목은 건너뛰었다고 보고한다.
  - 모두 옮긴 뒤 묶음 폴더가 지워지고 로그에 `finalize-run`이 남는다.
- [ ] **Step 7 (기준 7):** 도구 실행 전후의 `git status`를 비교한다. `inbox/` 밖의 변경이 없다(도구 코드 자체 제외). 결과를 `PROJECT-STATUS.md`에 반영하고 변경을 확인한다. 커밋은 사용자 요청 시.

---

## 자기 검토

- **spec 대응:**

| spec 항목 | 담당 Task |
|---|---|
| 2.1 (로그인·목록·영상 받기) | 6, 7, 13 |
| 2.2 (파일 끌어다 전사) | 8, 9 |
| 2.3 (PDF 종류) | 8, 9 |
| 2.4 (large-v3) | 4, 10, 12 |
| 2.5 (이어하기) | 3, 4, 5 |
| 2.6 (inbox 형식) | 2 |
| 4 (anti-goals) | 2, 5, 7, 8, 13 |
| 6.2 (묶음 형식) | 2 |
| 6.3 (문서 변경) | 11 (Step 3은 결정 대기) |
| 6.4 (위치) | 1, 10 |
| 6.5 (기술 선택) | 1, 4, 7, 8, 10 |
| 6.6 (모델 비교) | 12 |
| 6.7 (주차·차시) | 6, 9 |
| 6.7 (`안내.md` 규칙) | 2, 11 |
| 6.7 (다운로드 먼저) | 5 |
| 6.7 (과목 id) | 2, 8 |
| 6.7 (절전) | 5, 13 |
| 8 (완료 기준) | 13 |

- **빠진 것 없음, 의도적으로 뺀 것:**
  - 원본의 다중 사용자 격리, 로그인 시도 제한, 1회용 다운로드 티켓은 뺐다. spec 6.5에 따라 1인 로컬 도구이고, 받은 영상을 브라우저로 돌려주지 않는다.
  - 실행 중인 작업 취소는 뺐다. spec에 없다. 대기·실패 항목 삭제만 둔다.
- **이름 일관성:** `Store`·`Worker`·`next_item`·상태 상수(Task 5)를 Task 8에서 그대로 쓴다. `transcribe(audio, work, engine, on_progress)`(Task 4)를 Task 5와 12에서 같은 시그니처로 쓴다. `write_new_file`·`write_guide`·`transcript_name`(Task 2)을 Task 5와 8에서 같은 이름으로 쓴다. `UserError`·`SchoolExpired`는 `school.py` 하나에만 있다.
- **실행 방식 제안:** 테스트 파일 하나(`test_core.py`)를 Task 1~7·10이 차례로 늘리므로 Task를 병렬로 돌리지 않는다. Task 11은 Main의 결정 1이 필요하다.

---

**Main에게 따로 전달 (계획 본문과 별개):**
1. **충돌:** spec 6.3의 "ASM `source`"는 `_system/schemas/assignment.md`에 없는 필드다(`sources`는 ID 목록). 위 (a)/(b) 중 사용자 결정이 필요하고, Task 11 Step 3만 막힌다.
2. **가정:** 묶음의 파일과 같은 내용이 이미 `raw/`에 있으면 그 파일을 처리됨으로 보고 묶음 삭제를 허용한다. 확인을 요청한다.
3. **확인 범위:** 확인한 것은 faster-whisper 1.2.1 API·모델 이름, ctranslate2 4.8.4 cp312 Windows 휠, uv의 `UV_PROJECT_ENVIRONMENT`다. 확인하지 못한 것은 `clip_timestamps`와 VAD를 함께 쓸 때의 동작(배열 슬라이싱으로 우회), Gyan ffmpeg의 TLS 검증, Qwen3-ASR이다.
4. **참고 파일:**
   - spec: `C:\Users\ranbo\Projects\study-brain-template\_system\docs\specs\2026-11-02-lecture-inbox-design.md`
   - 이식 원본: `C:\Users\ranbo\AppData\Local\Temp\claude\C--Users-ranbo-Projects-study-brain-template\123d4679-9d8f-4957-adbe-694db15f484e\scratchpad\li\server\{school.py,app.py,lecture\repetition.py,lecture\whisper.py,lecture\transcript.py,test_app.py}`
   - 수정 대상: `C:\Users\ranbo\Projects\study-brain-template\{SECOND-BRAIN.md,inbox\README.md,_system\workflows\l5-fact-conflict-reconciliation.md,.agents\skills\check-conflict\SKILL.md,.agents\skills\capture\SKILL.md,_system\docs\run_all.py,_system\docs\README.md}`, `C:\Users\ranbo\Projects\study-brain-template\_system\schemas\assignment.md`(충돌 근거)