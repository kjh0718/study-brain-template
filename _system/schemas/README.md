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

운영 흐름은 향후 루트 SECOND-BRAIN.md에서 정의한다. 현재 파일들은 스키마 초안이며 자동화 구현이 아니다.
