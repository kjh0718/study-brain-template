# Assignments

과제와 마감, 제출 상태를 관리한다.

## 여기 두는 것

- 과제당 ASM 노트 하나
- 요구사항, 마감의 원문 표현, 제출 기록

## 여기 두지 않는 것

- 과제 원문 → `raw/assignments/`
- 제출 결과물 자체
- 추정한 마감 날짜

## 규격

[`assignment.md`](../../_system/schemas/assignment.md)

## 관련 워크플로

[L5 Fact & conflict reconciliation](../../_system/workflows/l5-fact-conflict-reconciliation.md)

마감이 모호하면 `due: null`, `due_status: needs-review`로 두고 원문 표현을 본문에 그대로 적는다.
