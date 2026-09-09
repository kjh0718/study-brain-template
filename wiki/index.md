# Wiki

과목을 넘어 재사용되는 장기 지식 영역이다. `study/`가 특정 과목·학기에 묶인 기록이라면, 여기는 학기가 끝나도 남는 지식을 둔다.

## 영역

| 영역 | Type | 담는 것 |
|---|---|---|
| [concepts/](concepts/README.md) | `concept` (CON) | 여러 과목에서 재사용되는 개념 |
| [clusters/](clusters/README.md) | `cluster` (CLU) | 주제 중심으로 개념과 노트를 잇는 탐색 지도 |
| [patterns/](patterns/README.md) | 없음 | 여러 근거에서 반복 확인된 패턴 |
| [_topics.md](clusters/_topics.md) | — | `topics` 값의 통제 어휘표 |

## 세 영역의 차이

**Concept**는 지식 자체다. 정의와 적용 조건을 담는다. 과목별로 복제하지 않는다. 일반물리학·공학수학·그래픽스에서 모두 벡터를 다뤄도 CON은 하나이며, 각 과목의 강의 노트가 그것을 가리킨다.

**Cluster**는 지식이 아니라 지도다. 관련된 개념·강의·자료·기출을 주제로 묶어 탐색을 돕는다. 여기에 새로운 설명을 쓰지 않는다. Cluster를 지워도 지식은 남아야 한다.

**Pattern**은 Core Type이 아니다. "이 과목의 중간고사에는 이런 유형이 반복된다" 같은 관찰을, 서로 독립적인 근거가 둘 이상 쌓였을 때만 문서로 남긴다. 생성 조건은 [L9](../_system/workflows/l9-knowledge-promotion.md)가 정한다. 근거 하나로는 만들지 않는다.

## 무엇이 여기 오지 않는가

- 특정 수업 한 회차의 내용 → `study/lectures/`
- 특정 학기의 시험·과제·일정 → `study/exams/`, `study/assignments/`, `study/course-facts/`
- 기출 분석 → `study/past-exams/`
- 원본 자료 → `raw/`

과목·학기 맥락이 있어야만 의미가 있는 것은 `study/`에 둔다. 그 맥락을 떼어도 성립하는 것만 여기 온다.

## 새 노트를 만들기 전에

개념을 만들기 전에 기존 개념을 먼저 찾는다. 표기가 달라도 같은 개념이면 하나로 연결한다. 용어가 한 번 등장했다는 이유만으로 개념 노트를 만들지 않는다.

승격 기준과 검색 방법은 [L4](../_system/workflows/l4-knowledge-extraction.md)에, 데이터 규격은 [`concept.md`](../_system/schemas/concept.md)와 [`cluster.md`](../_system/schemas/cluster.md)에 있다.

## 현재 상태

아직 등록된 개념과 Cluster가 없다. 실제 학습 자료가 들어오면서 채워진다.
