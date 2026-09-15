# HOME

Study Brain 시작 화면이다. 각 영역으로 이동하는 지도이며 데이터를 담는 곳이 아니다.

> 이 저장소는 아직 템플릿이다. 아래 목록은 비어 있는 것이 정상이며, 실제 노트가 쌓이면 각 폴더에서 확인한다.

새 입력을 넣거나 무언가를 찾으려면 에이전트에게 요청한다. 규칙은 [`SECOND-BRAIN.md`](SECOND-BRAIN.md)에 있다.

---

## 지금 할 일

Obsidian에서는 [`study-overview`](_system/views/study-overview.base) 표 뷰가 아래 다섯 가지를 자동으로 모아 준다. 열어서 상단 탭으로 전환한다.

아래 표는 각 현황을 확인하는 경로다. Obsidian이 없으면 [Study 구조 안내](study/README.md)를 따라 과목 노트를 찾고 frontmatter로 검색한다.

| | 어디 | 무엇을 본다 |
|---|---|---|
| 마감 | [진행 중인 과제](_system/views/study-overview.base) | `status: open`, `in-progress`인 과제 |
| 시험 | [예정된 시험](_system/views/study-overview.base) | `status: planned`인 시험과 범위 확정 상태 |
| 확인 필요 | 저장소 전체 | `status: needs-review`인 노트. 날짜·출처·충돌이 미확정이라는 뜻이다 |
| 미해결 질문 | [열린 질문](_system/views/study-overview.base) | `status: open`, `investigating`인 질문 |
| 다음 복습 | [진행/예정 복습](_system/views/study-overview.base) | `planned`, `in-progress` 회차의 `scheduled_on`과 `next_review` |

`needs-review`가 쌓이면 사람이 확인해야 한다는 신호다. 에이전트가 임의로 확정하지 않고 남겨 둔 것이다. `study-overview`의 확인 필요 탭은 `study/`만 조회하므로 전역 `wiki/`까지 확인하려면 저장소 전체를 검색한다.

## 과목

[과목 폴더 구조](study/README.md) — `study/<term>/<course-slug>/course.md`의 CRS 노트가 과목 대시보드 역할을 한다. 그 과목의 강의·과제·시험·자료·사실이 거기서 모인다.

과목 단위로 볼 때는 CRS 노트를 먼저 연다. 이 화면이 아니라 그쪽이 과목의 시작점이다.

## 수업과 자료

[Study 구조 안내](study/README.md)에서 아래 종류별 저장 위치를 확인한다.

| 영역 | 담는 것 |
|---|---|
| Lectures | 실제 수업 세션 하나씩. 요약, 교수님 강조, 개념, 질문 |
| Resources | 자료 노트. 자료 하나를 여러 강의가 페이지 범위별로 공유한다 |
| Past Exams | 기출·족보의 문항별 분석 |
| Course Facts | 일정·정책 등 운영 사실과 변경 이력 |

## 장기 지식

| 영역 | 담는 것 |
|---|---|
| [Concepts](wiki/concepts/README.md) | 과목을 넘어 재사용하는 개념. 과목별로 복제하지 않는다 |
| [Clusters](wiki/clusters/README.md) | 주제 중심 탐색 지도 |
| [Patterns](wiki/patterns/README.md) | 여러 근거에서 반복 확인된 패턴. L9에서만 만든다 |
| [Topic 어휘표](wiki/clusters/_topics.md) | 쓸 수 있는 `topics` 값의 정본 |
| [Wiki 색인](wiki/index.md) | 장기 지식 영역 안내 |
| [Knowledge Browser](_system/views/knowledge-browser.base) | 강의·개념·자료·기출을 표로 훑는 뷰 (Obsidian 전용) |

## 입력

| 영역 | 담는 것 |
|---|---|
| [Inbox](inbox/README.md) | 아직 분류하지 못한 입력. 비어 있는 것이 정상이다 |
| [Raw](raw/README.md) | 학기·과목별 원본 보존 영역. 전사, 강의자료·일반 자료, 기출, 과제, 공지 |

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

커뮤니티 플러그인을 전제하지 않는다. 위 검색은 Obsidian 기본 검색과 일반 텍스트 검색 모두에서 동작한다.

자동 갱신되는 목록 뷰는 [`_system/views/`](_system/views/README.md)에 있다. Obsidian 코어 플러그인 Bases를 쓰며, 없어도 이 화면의 링크만으로 모든 영역에 갈 수 있다.
