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

## 아직 없는 것

플랫폼 등록 파일(`.claude/settings.json`, `.codex/hooks.json`)은 아직 만들지 않았다. core와 검사가 먼저다. Antigravity 어댑터는 보류했다.

`raw/` 원본을 만든 뒤 바뀌지 않게 지키는 PreToolUse guard는 V1 다음 후보다. ingest가 원본을 새로 만드는 것은 정상이므로 `raw/` 전체 쓰기를 막는 방식은 쓰지 않는다.
