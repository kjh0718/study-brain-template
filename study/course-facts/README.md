# Course Facts

시험 일정, 휴강, 평가 방식 등 과목 운영 사실과 그 변경 이력을 관리한다.

## 여기 두는 것

- 사실 항목당 FAC 노트 하나
- 근거 원문, 적용 범위, 변경 이력

## 여기 두지 않는 것

- 공지 원문 → `raw/notices/`
- 개념·질문 → `wiki/concepts/`, `study/questions/`
- 삭제된 과거 사실. 지우지 않고 `superseded`로 남긴다

## 규격

[`course-fact.md`](../../_system/schemas/course-fact.md)

## 관련 워크플로

[L5 Fact & conflict reconciliation](../../_system/workflows/l5-fact-conflict-reconciliation.md)

대체 관계는 새 Fact의 `supersedes` 한 방향만 저장한다. 이전 Fact에 `superseded_by`를 두지 않는다.
