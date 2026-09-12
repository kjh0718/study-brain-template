# Agent Skills

Study Brain Skill의 **정본**이다. 도구에 중립적이며 여기 있는 문서가 규격이다.

## Skill의 역할

Skill은 얇은 호출 인터페이스다. 사용자의 의도를 알맞은 워크플로에 연결하고, 무엇을 어떤 순서로 읽어야 하는지 알려준다.

**Skill은 규칙을 만들지 않는다.** 새 스키마, authority 정책, 충돌 규칙, ID 규칙을 정의하지 않고 워크플로의 판단 로직을 복사하지도 않는다.

| 계층 | 정본 |
|---|---|
| 데이터 계약 | [`_system/schemas/`](../../_system/schemas/README.md) |
| 운영 판단 | [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md) |
| 실행 절차 | [`_system/workflows/`](../../_system/workflows/README.md) |
| 호출 인터페이스 | 이 폴더 |

## Skill 목록

| Skill | 레이어 | 워크플로 |
|---|---|---|
| [`capture`](capture/SKILL.md) | 라우팅 | 입력을 분류해 아래 셋 중 하나로 |
| [`ingest-lecture`](ingest-lecture/SKILL.md) | L1 | [`l1-lecture-ingestion.md`](../../_system/workflows/l1-lecture-ingestion.md) |
| [`ingest-resource`](ingest-resource/SKILL.md) | L2 | [`l2-resource-ingestion.md`](../../_system/workflows/l2-resource-ingestion.md) |
| [`ingest-past-exam`](ingest-past-exam/SKILL.md) | L3 | [`l3-past-exam-ingestion.md`](../../_system/workflows/l3-past-exam-ingestion.md) |
| [`check-conflict`](check-conflict/SKILL.md) | L5 | [`l5-fact-conflict-reconciliation.md`](../../_system/workflows/l5-fact-conflict-reconciliation.md) |
| [`recall`](recall/SKILL.md) | L6 | [`l6-recall.md`](../../_system/workflows/l6-recall.md) |
| [`review`](review/SKILL.md) | L7 | [`l7-review.md`](../../_system/workflows/l7-review.md) |
| [`maintain`](maintain/SKILL.md) | L8 | [`l8-maintenance.md`](../../_system/workflows/l8-maintenance.md) |

**L4와 L9에는 전용 Skill이 없다.** L4는 L1·L2·L3이 호출하고, L9는 사용자가 명시적으로 요청할 때만 시작한다. 필요하면 워크플로 문서를 직접 읽어 수행한다.

## 문서 구성

각 `SKILL.md`는 다음만 가진다. 워크플로를 다시 길게 복사하지 않는다.

```text
frontmatter (name, description)
Purpose / When to use / Required reading / Inputs
Execution / Completion / Do not / Example
```

`Execution`은 `SECOND-BRAIN.md` → 해당 워크플로 → 관련 스키마·템플릿 순으로 읽도록 연결하는 정도로 끝낸다.

## Claude Code와의 관계

[`.claude/skills/`](../../.claude/skills/README.md)에는 같은 이름의 스텁이 있다. Claude Code가 Skill을 찾으려면 그 경로에 파일이 있어야 하기 때문이며, 스텁은 여기 있는 정본을 가리키기만 한다. 긴 내용을 양쪽에 복제하지 않고 symlink도 쓰지 않는다.

`description`만 양쪽에 있다. Claude Code의 Skill 탐색이 그 값을 쓰기 때문이다. 두 값이 어긋나지 않는지는 [`check_skills.py`](../../_system/docs/skill-validation/check_skills.py)가 검사한다.

## Skill을 추가할 때

- 폴더 이름과 `name`을 같게 한다. lowercase-kebab-case를 쓴다.
- 대응하는 워크플로가 없으면 만들지 않는다. 먼저 워크플로를 정의한다.
- 판단 기준을 여기 쓰고 싶어지면 그건 `SECOND-BRAIN.md` 또는 스키마에 들어갈 내용이다.
- 추가 후 `check_skills.py`를 실행한다.
