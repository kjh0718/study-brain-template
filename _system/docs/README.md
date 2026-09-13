# System Docs

Study Brain의 설계 결정, 운영 설명 및 보조 문서를 보관합니다.

## 폴더

| 폴더 | 역할 |
|---|---|
| `plan/` | 구현 전에 확정한 설계 문서 묶음. 목표, 구조, 데이터 모델, 운영 규칙, Git 전략, 구현 순서, 테스트 기준, 결정 기록 |
| `template-validation/` | `_system/templates/` 검사용 임시 스크립트와 가상 노트 |
| [`integration-test/`](integration-test/README.md) | Scenario A~K 워크플로 정합성 검증 |
| [`skill-validation/`](skill-validation/README.md) | Skill 구조와 runtime 결과 검증 |
| [`hook-validation/`](hook-validation/README.md) | SessionStart 공통 core 검증 |

## 한 번에 돌리기

```bash
python _system/docs/run_all.py
```

위 스위트를 정해진 순서로 부르고 종료 코드와 요약을 표로 낸다. 검사 로직을 새로 만들지 않으며, 각 스크립트를 직접 실행하는 방법도 그대로 유효하다. fixture 생성기(`build_fixtures.py`, `build_filled.py`, `seed_workspace.py`)는 부르지 않는다. 추적 중인 fixture를 다시 만들면 검사 대상이 바뀌기 때문이다.

| 옵션 | 뜻 |
|---|---|
| `--list` | 무엇을 도는지만 본다 |
| `--fail-fast` | 첫 FAIL에서 멈춘다 |
| `--strict` | SKIP도 실패로 본다 |

**SKIP과 PASS는 다르다.** SKIP은 사전 조건이 없어 그 스위트를 **돌리지 못했다**는 뜻이며, `PASS 5 / SKIP 1`은 전체 검증을 마친 상태가 아니다. 종료 코드는 기본적으로 FAIL에서만 1이 되고, `--strict`를 주면 SKIP에서도 1이 된다.

새로 clone하면 Skill 런타임 스위트가 SKIP된다. `runtime/workspace/`가 `.gitignore` 대상이기 때문이다. 실제 에이전트 실행까지 검증하려면 [`skill-validation/runtime-test.md`](skill-validation/runtime-test.md)의 절차대로 `seed_workspace.py`로 workspace를 만들고 Skill을 호출한 뒤 검증해야 한다. **`run_all.py`는 이 준비를 대신하지 않는다.** 에이전트 실행 결과가 든 workspace를 실행기가 임의로 초기화하면 안 되기 때문이다.
