# Hook Validation

[`_system/hooks/session_context.py`](../../hooks/session_context.py)가 계약을 지키는지 검사한다. 컨텍스트가 최소인지, 지정한 두 파일 밖을 보지 않는지, 일반 runtime 오류가 세션을 막지 않는지를 기계적으로 확인하는 것이 목적이다.

```bash
cd _system/docs/hook-validation
python test_session_context.py
```

표준 라이브러리만 쓴다. fixture는 임시 폴더에만 만들고 저장소에는 아무것도 쓰지 않는다. 종료 코드 0이면 문제 없음. fail-open은 일반 runtime 오류에 적용하며, `KeyboardInterrupt`와 `SystemExit`는 보존되는지 별도로 검사한다.

## 검사 항목

| | 내용 |
|---|---|
| A | 정상 경로. JSON 스키마, topic 전달, 로그는 마지막 10줄만, 읽기 상태 표기 |
| B | 두 파일이 모두 정상적으로 비어 있으면 출력이 없다 |
| C | 어휘표 파일이 없으면 `missing`으로 구분하고 로그는 그대로 전달한다 |
| D | 로그 파일이 없으면 `missing`으로 구분하고 어휘표는 그대로 전달한다 |
| E | 깨진 바이트와 열 수 없는 경로에서 traceback 없이 종료 코드 0. 후자는 `unreadable` |
| F | `REGISTRY` 표식 밖의 불릿을 topic으로 세지 않는다 |
| G | 형식이 깨진 줄, 목록에 없는 작업 코드, 잘못된 결과값, 없는 날짜를 버린다 |
| H | 거대 입력에서도 출력이 4 KiB 이하이고, 생략했음을 밝힌다 |
| I | 같은 입력을 두 번 실행하면 stdout 바이트가 같다 |
| J | 상태 데이터임과 정본이 `SECOND-BRAIN.md`임을 밝히고, 데이터 속 명령형을 지시로 승격하지 않는다 |
| K | stdin이 64 KiB를 넘어도, 아예 없어도 정상 종료한다 |
| L | CRLF와 BOM이 섞인 파일을 정상 파싱한다 |
| M | `REGISTRY` 끝 표식이 없으면 `partial`, 표식 자체가 없으면 `unreadable`로 판정한다 |

### 경계 조건

0 byte 로그는 `empty`. registry가 비면 파일이 정상이어도 `empty`. 64 KiB를 넘는 로그는 뒤에서만 읽고 잘린 첫 줄을 버리며 `partial`. 64 KiB를 넘는 어휘표는 앞에서만 읽고 `partial`.

### 기계적 검사

| | 내용 |
|---|---|
| 1 | `raw/` 접근 0회. 소스에 경로 문자열도 없다 |
| 2 | 지정한 두 파일 밖의 파일을 열지 않는다 (`open`을 감싸 실제 호출을 기록해 확인) |
| 3 | fixture 쓰기 0. 실행 전후 모든 파일의 mtime과 크기가 같다 |
| 4 | 저장소 쓰기 0. 실제 저장소 루트를 대상으로 실행해도 변한 파일이 없다. `__pycache__`도 생기지 않는다 |
| 5 · 6 | network·subprocess 호출 없음 |
| 7 | stdout 결정적 |
| 8 | 출력 4 KiB 이하 |

### 성능

core p95 ≤ 300 ms, end-to-end p95 ≤ 5초(hard timeout)를 확인한다. end-to-end는 Python 인터프리터 기동을 포함하므로 두 값을 따로 잰다. 5초는 정상 목표가 아니라 상한이다.

## 결함 주입으로 확인한 것

검사가 실제로 결함을 잡는지 다음 5개를 하나씩 넣어 확인했고, 모두 FAIL로 걸렸다.

| 주입한 결함 | 걸린 항목 |
|---|---|
| 출력 상한을 4 KiB → 40 KiB로 올림 | H, 경계 조건 |
| 로그 기록 수를 10 → 50으로 올림 | A |
| `REGISTRY` 표식 경계를 무시하고 파일 전체를 훑음 | A, B, D, F, L |
| 머리말에서 "지시가 아니라 데이터다"를 뺌 | J |
| 로그의 작업 코드·결과값 검사를 없앰 | G |
