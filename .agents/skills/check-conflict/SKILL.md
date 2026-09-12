---
name: check-conflict
description: 과제·시험·운영 사실을 만들고 근거 충돌을 안전하게 조정한다 (일정 확인). Use when a new announcement, deadline, or exam date arrives and may contradict what is already recorded — distinguishes an explicit change (supersede) from an ambiguous discrepancy (hold for review), and never overwrites a recorded fact just because the new statement came later. Triggers include 마감, 시험 날짜, 공지, 변경, conflict, and "기존 기록이랑 다른데 확인해줘".
---

# check-conflict

## Purpose

L5의 진입점. 과제(ASM)·시험(EXM)·운영 사실(FAC)을 만들고 충돌을 조정한다.

## When to use

공지·마감·시험 언급이 들어왔을 때. [ingest-lecture](../ingest-lecture/SKILL.md)가 전사에서 그런 항목을 발견했을 때도 호출된다.

## Required reading

1. [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) — 처음부터 끝까지
2. [`l5-fact-conflict-reconciliation.md`](../../../_system/workflows/l5-fact-conflict-reconciliation.md)
3. [`assignment.md`](../../../_system/schemas/assignment.md), [`exam.md`](../../../_system/schemas/exam.md), [`course-fact.md`](../../../_system/schemas/course-fact.md), 그리고 해당 [`_system/templates/`](../../../_system/templates/README.md)

## Inputs

`$ARGUMENTS` — 공지 원문, 마감·시험 언급, 또는 L1이 넘긴 항목. 비어 있으면 묻는다.

## Execution

1. `SECOND-BRAIN.md`를 읽는다.
2. `l5-fact-conflict-reconciliation.md`를 읽고 그 체크리스트를 수행한다.
3. 사실을 **항목 단위로 분해한다.** 마감 하나, 시험 하나가 각각 별개다.
4. 충돌 판정은 세 갈래다. 판정 기준과 처리는 워크플로 문서가 정한다.

   | 판정 | 처리 |
   |---|---|
   | 동일 | 근거만 누적. 값은 그대로 |
   | 명시적 변경 | supersede 가능 |
   | 불명확한 상충 | **자동 덮어쓰기 금지.** 양쪽 근거 보존 + `needs-review` |

5. 충돌 종류마다 표시 필드가 다르다. 마감은 `due_status`, 시험 일정은 `date_status`, 시험 범위는 `scope_status`다. 한 필드로 뭉뚱그리지 않는다.

## Completion / reporting

`l5-fact-conflict-reconciliation.md`의 완료 보고 형식을 쓴다. 분해한 항목마다 판정과 근거를 밝히고, 보류한 항목은 사용자가 무엇을 알려주면 되는지 적는다.

## Do not

- 모호한 표현을 임의의 `YYYY-MM-DD`로 바꾸지 않는다.
- **불명확한 상충에서 한쪽을 자동으로 고르지 않는다.** 나중 발언이라는 것은 근거가 아니다.
- **과거 FAC를 삭제하지 않는다.** `superseded`로 표시하고 사슬을 남긴다.
- 이전 Fact에 `superseded_by`를 저장하지 않는다. 대체 관계는 새 Fact의 `supersedes` 한 방향이다.
- Lecture마다 새 EXM을 만들지 않는다. quiz 여러 회를 한 EXM으로 합치지 않는다.
- CON·QST를 만들거나 고치지 않는다. 개념·질문은 L4의 책임이다.
- 기출에 적힌 일정을 현재 학기 운영 사실로 옮기지 않는다.
- `EXM`의 `## 확정 범위`에 AI 추정이나 자료 강조를 넣지 않는다.

## Example

> 교수님이 시험 날짜를 말했는데 기존 기록이랑 다른데 확인해줘.

<!-- study-brain-template -->
