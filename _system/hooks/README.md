# Hooks

세션 시작 컨텍스트를 만드는 **공통 core**를 둔다. 플랫폼별 등록 파일(`.claude/settings.json`, `.codex/hooks.json`)은 이 core 하나를 가리키며, 규칙을 다시 정의하지 않는다.

| 파일 | 역할 |
|---|---|
| `session_context.py` | SessionStart 컨텍스트 생성. Claude Code와 Codex가 같은 파일을 쓴다 |

검사는 [`_system/docs/hook-validation/`](../docs/hook-validation/)에 있다.

## 무엇을 읽는가

파일 **두 개**만 읽는다. 그 밖의 경로는 열지 않는다.

| 경로 | 읽는 범위 |
|---|---|
| `wiki/clusters/_topics.md` | `<!-- REGISTRY:start -->`와 `<!-- REGISTRY:end -->` 사이의 등록 항목 |
| `_system/log.md` | 형식이 완전한 마지막 기록 최대 10줄 |

`raw/`, `study/`, `inbox/`, Course 대시보드는 읽지 않는다. 활성 Course를 추론하지 않는다. 읽은 줄을 그대로 옮기며 요약하거나 해석하지 않는다.

표식 밖의 불릿은 registry 항목이 아니다. `_topics.md`의 규칙 설명이 topic으로 새어 들어가지 않게 하는 경계다. 로그는 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)의 `_system/log.md`는 append-only다 절이 정한 한 줄 형식과 작업 코드 목록에 맞는 줄만 통과시킨다. 형식이 깨진 줄, 목록에 없는 작업 코드, 없는 날짜는 버린다.

## 출력

Claude Code와 Codex가 같은 JSON 형식을 받는다.

```json
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}
```

`--format text`를 주면 본문만 낸다. 검사와 사람이 읽을 때 쓴다.

### 문체는 사실 진술이다

컨텍스트는 **지시문이 아니라 상태 데이터**로 쓴다.

- ❌ `SECOND-BRAIN.md를 읽어라.`
- ✅ `판단 규칙의 정본은 SECOND-BRAIN.md다.`

명령형으로 쓴 컨텍스트는 주입된 지시처럼 보여 모델의 방어 동작을 건드릴 수 있고, 실제로는 그저 파일에서 읽은 값이다. 같은 이유로 `_topics.md`나 `log.md` 안에 명령형 문장이 있어도 hook 지시로 승격하지 않는다. 출력 머리말이 이 점을 명시한다.

### 읽기 상태를 구분한다

빈 것과 못 읽은 것은 다르다. 어휘표가 `empty`인 것은 등록된 topic이 없다는 사실이고, `unreadable`인 것은 아무것도 알 수 없다는 뜻이다. 출력의 `### 읽기 상태` 절이 파일별로 다음 중 하나를 적는다.

| 값 | 뜻 |
|---|---|
| `ok` | 끝까지 읽었고 항목이 있다 |
| `empty` | 정상적으로 읽었고 항목이 0개다 |
| `missing` | 파일이 없다 |
| `unreadable` | 열 수 없거나 registry 표식이 없어 판정할 수 없다 |
| `partial` | 읽기 상한에 걸려 일부만 봤다 |

두 파일이 모두 정상이면서 비어 있으면 **아무것도 출력하지 않는다.** 세션 시작 컨텍스트는 최소여야 한다.

## 한계값

| 항목 | 값 | 이유 |
|---|---|---|
| 파일당 읽기 | 64 KiB | 로그는 뒤에서, 어휘표는 앞에서 읽는다 |
| 출력 | 4 KiB UTF-8 | Codex `additionalContext` 기본 상한(약 2,500 토큰)에 여유를 둔다. `additionalContextLimit`을 올려 맞추지 않고 출력을 줄인다 |
| 로그 기록 수 | 10줄 | |
| hard timeout | 5초 | 정상 목표가 아니라 상한이다. Windows Python cold start와 일시적 지연을 위한 여유이며, 넘으면 컨텍스트 없이 진행한다 |
| 정상 성능 목표 | p95 ≤ 300 ms | |

상한을 넘겨 항목을 버린 경우 그 사실을 출력에 적는다. 오래된 로그부터 버린다.

## 하지 않는 것

- **fail-open.** 일반 runtime 오류는 traceback 없이 종료 코드 0으로 끝낸다. 컨텍스트를 만들지 못하면 아무것도 출력하지 않는다. `KeyboardInterrupt`와 `SystemExit`는 삼키지 않고 호출자에게 전달한다.
- 어떤 파일에도 쓰지 않는다. 캐시·상태 파일·로그를 남기지 않는다. `__pycache__`도 만들지 않는다.
- network를 쓰지 않는다. 하위 프로세스를 띄우지 않는다.
- 표준 라이브러리만 쓴다. PyYAML도 쓰지 않는다.
- 같은 입력에 대해 stdout 바이트가 항상 같다. 시각·난수·환경값을 섞지 않는다.
- 사용자 전역 설정이나 다른 저장소의 hook을 건드리지 않는다.

## 플랫폼 등록

| 파일 | 대상 | 상태 |
|---|---|---|
| `.claude/settings.json` | Claude Code | Windows에서 runtime 확인함 |
| `.codex/hooks.json` | Codex | Windows에서 runtime 확인함 |

### Claude Code

exec form(`command` + `args`)으로 `${CLAUDE_PROJECT_DIR}` 아래의 core를 부른다. args가 있으면 shell을 거치지 않고 PATH에서 실행 파일을 직접 찾는다.

launcher 이름은 `python`으로 뒀다. **이 Windows 개발 환경에서 PATH의 `python`이 Python 3임을 확인한 값이다.** macOS와 Linux에서 `python`이라는 실행 파일이 있는지는 확인하지 않았다. launcher를 자동으로 찾는 wrapper는 두지 않는다. 크로스 플랫폼 launcher 구성은 템플릿 배포(P10) 단계에서 다룬다.

2026-09-13 Windows 확인: `SessionStart:startup`에서 hook이 실행되고 `additionalContext`가 전달됐다. script 경로를 없는 파일로 바꾼 실패 fixture에서는 hook만 오류로 끝나고 세션 초기화는 정상 종료했다.

### Codex

`SessionStart`의 source 네 가지(`startup`, `resume`, `clear`, `compact`)에 걸고, POSIX는 `python3`, Windows는 `commandWindows`를 쓴다. 두 경로 모두 Git root에서 script를 찾는다.

Codex는 hook command를 **세션 환경의 shell로 실행한다.** 그 shell이 PowerShell일 수도, cmd일 수도 있다. `commandWindows`는 shell에 argv 원소 하나로 전달되며 Windows의 argv 조립 규칙이 문자열 안의 `"`를 `\"`로 바꾼다. cmd는 `\"`를 이해하지 못하므로, 따옴표가 들어간 표현은 cmd 쪽에서 **오류 없이 조용히** 명령 텍스트를 그대로 출력한다. 반대로 따옴표를 빼면 바깥 PowerShell이 `( )`를 먼저 평가해 공백이 든 경로에서 토큰이 쪼개진다.

그래서 Windows는 `-EncodedCommand`를 쓴다. Base64는 두 shell 모두에서 **평범한 토큰 하나**라 dialect 차이를 타지 않고, 모든 평가가 안쪽 PowerShell에서만 일어난다.

```
powershell.exe -NoProfile -EncodedCommand <BASE64>
```

**정본은 Base64가 아니라 아래 payload다.** Base64는 이것을 UTF-16LE로 인코딩한 파생물이며, 고칠 때는 payload를 고치고 다시 생성한다.

```powershell
$ProgressPreference = 'SilentlyContinue'
$r = git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0 -or -not $r) { exit 0 }
& py -3 -B (Join-Path $r '_system/hooks/session_context.py')
exit $LASTEXITCODE
```

생성 규칙은 PowerShell `-EncodedCommand` 규격 그대로다. **UTF-16LE로 인코딩한 뒤 Base64.** 손으로 옮기지 않는다.

```bash
python -c "import base64,io;print(base64.b64encode(io.open('payload.ps1',encoding='utf-8').read().encode('utf-16-le')).decode())"
```

payload 각 줄의 이유.

| 줄 | 이유 |
|---|---|
| `$ProgressPreference = 'SilentlyContinue'` | Windows PowerShell 5.1에서 `-EncodedCommand`로 네이티브 명령을 부르고 stderr가 파이프면 progress 레코드가 CLIXML로 stderr에 섞인다. 오류가 아니지만 hook 출력은 깨끗해야 하므로 끈다 |
| `git rev-parse --show-toplevel` | Codex는 하위 디렉터리에서 시작될 수 있다. cwd가 아니라 Git root에서 core를 찾는다. `2>$null`로 git의 오류 메시지를 흘리지 않는다 |
| `if (…) { exit 0 }` | Git 저장소가 아니거나 git이 실패하면 stdout·stderr 없이 종료 코드 0으로 끝난다. 세션을 막지 않는다 |
| `& py -3 -B` | Windows Python Launcher로 Python 3을 고른다. 이 환경의 `python`은 3.11, `py -3`은 3.13을 가리켰다. `-B`로 `__pycache__`를 만들지 않는다 |
| `Join-Path $r '…'` | 경로 결합을 안쪽 PowerShell에서 처리한다. repo 경로에 공백이 있어도 인자 하나로 유지된다 |
| `exit $LASTEXITCODE` | core의 종료 코드를 그대로 올린다 |

개인 절대경로나 개인 Python 설치 경로는 넣지 않는다. `.cmd`·`.ps1` wrapper도 두지 않는다. wrapper를 두면 그 wrapper를 찾는 문제가 그대로 남고(`CreateProcess`는 `.cmd`를 직접 실행하지 못한다), 파일만 하나 늘 뿐 Git root 문제를 해결하지 못한다.

전제는 hook 환경 PATH에 `git`과 `py`가 있는 것이다. 둘 다 실제 Codex hook 환경에서 확인했다.

2026-09-13 Windows 확인(`codex-cli 0.153.4`): repo root와 **하위 디렉터리(`wiki/clusters`)** 양쪽에서 세션을 시작해 `SessionStart` hook이 실행되고 `additionalContext`가 모델까지 전달됐다. 직접 실행 검사에서는 PowerShell·cmd × root·하위 디렉터리 × 공백 있는 repo 경로 조합이 모두 통과했고, Git 저장소가 아닌 cwd에서는 stdout·stderr 없이 종료 코드 0이었다.

## 아직 없는 것

Antigravity 어댑터는 보류했다.

`raw/` 원본을 만든 뒤 바뀌지 않게 지키는 PreToolUse guard는 V1 다음 후보다. ingest가 원본을 새로 만드는 것은 정상이므로 `raw/` 전체 쓰기를 막는 방식은 쓰지 않는다.
