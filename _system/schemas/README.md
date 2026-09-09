# Schemas

Study Brain의 11개 Core Type과 공통 데이터 규칙을 정의한다.

먼저 [common.md](common.md)를 읽고 해당 타입 규격을 적용한다. 예시 YAML은 가상 데이터이며 실제 노트를 생성하지 않는다.

- [course](course.md)
- [lecture](lecture.md)
- [resource](resource.md)
- [concept](concept.md)
- [assignment](assignment.md)
- [exam](exam.md)
- [past-exam](past-exam.md)
- [course-fact](course-fact.md)
- [question](question.md)
- [review](review.md)
- [cluster](cluster.md)

wiki/patterns/는 Core Type이 아니다. 폴더별 README로 역할을 설명하며 .gitkeep이나 추가 ignore 정책을 만들지 않는다.

## 여기 두는 것

- Core Type의 필수·선택 필드와 타입
- 허용 상태값과 그 뜻
- ID 형식 계약과 Type별 권장 형태 ([common.md](common.md)의 `id` 절)
- 관계 필드와 역방향 유지 규칙
- 각 Type의 본문 절 구조

## 여기 두지 않는 것

- 처리 절차와 판단 기준 → 루트 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)
- 실행 체크리스트, 검색 명령, 보고 형식 → [`_system/workflows/`](../workflows/README.md)
- 새 노트 작성 양식 → [`_system/templates/`](../templates/README.md)
- 실제 학습 데이터. 예시 YAML은 전부 가상 데이터이며 노트를 생성하지 않는다

## 규칙을 바꿔야 할 때

스키마와 SECOND-BRAIN.md 또는 워크플로 문서가 충돌하면 조용히 한쪽을 따르지 않고 충돌 위치를 보고한다. 데이터 규격은 이 폴더가 기준이므로, 필드·상태값·관계를 바꾸려면 여기를 먼저 고친 뒤 참조하는 문서를 맞춘다. 스키마에 없는 필드나 상태값을 노트에서 임의로 만들지 않는다.
