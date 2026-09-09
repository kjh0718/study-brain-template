# HOME

Study Brain 시작 화면이다. 각 영역으로 이동하는 지도이며 데이터를 담는 곳이 아니다.

> 이 저장소는 아직 템플릿이다. 아래 목록은 비어 있는 것이 정상이며, 실제 노트가 쌓이면 각 폴더에서 확인한다.

새 입력을 넣거나 무언가를 찾으려면 에이전트에게 요청한다. 규칙은 [`SECOND-BRAIN.md`](SECOND-BRAIN.md)에 있다.

---

## 지금 할 일

| | 어디 | 무엇을 본다 |
|---|---|---|
| 마감 | [Assignments](study/assignments/README.md) | `status: open`, `in-progress`인 과제 |
| 시험 | [Exams](study/exams/README.md) | `status: planned`인 시험과 확정 범위 |
| 확인 필요 | 저장소 전체 | `status: needs-review`인 노트. 날짜·출처·충돌이 미확정이라는 뜻이다 |
| 미해결 질문 | [Questions](study/questions/README.md) | `status: open`, `investigating`인 질문 |
| 다음 복습 | [Reviews](study/reviews/README.md) | `next_review`가 가까운 회차 |

`needs-review`가 쌓이면 사람이 확인해야 한다는 신호다. 에이전트가 임의로 확정하지 않고 남겨 둔 것이다.

## 과목

[Courses](study/courses/README.md) — 과목마다 CRS 노트 하나가 대시보드 역할을 한다. 그 과목의 강의·과제·시험·자료·사실이 거기서 모인다.

과목 단위로 볼 때는 CRS 노트를 먼저 연다. 이 화면이 아니라 그쪽이 과목의 시작점이다.

## 수업과 자료

| 영역 | 담는 것 |
|---|---|
| [Lectures](study/lectures/README.md) | 실제 수업 세션 하나씩. 요약, 교수님 강조, 개념, 질문 |
| [Resources](study/resources/README.md) | 자료 노트. 자료 하나를 여러 강의가 페이지 범위별로 공유한다 |
| [Past Exams](study/past-exams/README.md) | 기출·족보의 문항별 분석 |
| [Course Facts](study/course-facts/README.md) | 일정·정책 등 운영 사실과 변경 이력 |

## 장기 지식

| 영역 | 담는 것 |
|---|---|
| [Concepts](wiki/concepts/README.md) | 과목을 넘어 재사용하는 개념. 과목별로 복제하지 않는다 |
| [Clusters](wiki/clusters/README.md) | 주제 중심 탐색 지도 |
| [Patterns](wiki/patterns/README.md) | 여러 근거에서 반복 확인된 패턴. L9에서만 만든다 |
| [Topic 어휘표](wiki/clusters/_topics.md) | 쓸 수 있는 `topics` 값의 정본 |
| [Wiki 색인](wiki/index.md) | 장기 지식 영역 안내 |

## 입력

| 영역 | 담는 것 |
|---|---|
| [Inbox](inbox/README.md) | 아직 분류하지 못한 입력. 비어 있는 것이 정상이다 |
| [Raw](raw/transcripts/README.md) | 원본 보존 영역. 전사, 자료, 기출, 과제, 공지, 문서 |

`raw/`의 원본은 읽기만 한다. 정리는 `study/`와 `wiki/`의 구조화 노트에서 한다.

## 시스템

| | |
|---|---|
| [SECOND-BRAIN.md](SECOND-BRAIN.md) | 운영 규칙의 정본 |
| [Schemas](_system/schemas/README.md) | 필드·상태값·관계 규격 |
| [Workflows](_system/workflows/README.md) | L1~L9 실행 문서 |
| [Templates](_system/templates/README.md) | 새 노트 작성 양식 |
| [Log](_system/log.md) | 작업 이력. append-only |
| [PROJECT-STATUS.md](PROJECT-STATUS.md) | 현재 구현 상태 |

---

## 찾는 방법

Obsidian 검색창이나 에이전트 어느 쪽이든 frontmatter로 좁히는 것이 빠르다.

```text
status: open          진행 중인 과제, 미해결 질문
status: needs-review  확인이 필요한 노트
type: lecture         강의 노트만
course: CRS-...       한 과목의 노트 전부
```

특정 플러그인을 전제하지 않는다. 위 검색은 Obsidian 기본 검색과 일반 텍스트 검색 모두에서 동작한다. 자동 갱신되는 목록 뷰는 이후 단계에서 추가한다.
