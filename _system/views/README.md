# Views

Obsidian **Bases** 표 뷰를 둔다. 노트의 frontmatter를 조건별로 모아 보여 주는 화면이며, **사람이 보는 용도**다.

에이전트의 회수 경로는 언제나 frontmatter 검색이다. 에이전트는 이 파일을 읽어서 노트를 찾지 않는다.

| 파일 | 담는 것 |
|---|---|
| [`study-overview.base`](study-overview.base) | 지금 할 일. 과제, 시험, 질문, 복습, 확인 필요 |
| [`knowledge-browser.base`](knowledge-browser.base) | 탐색. 강의, 개념, 자료, 기출 |

Obsidian에서 파일을 열면 상단 탭으로 뷰를 전환한다.

## 전제

- **Obsidian 1.9 이상.** Bases는 코어 플러그인이며 설정 → 코어 플러그인에서 켠다. 이 저장소의 [`core-plugins.json`](../../.obsidian/core-plugins.json)에는 이미 켜져 있다.
- **커뮤니티 플러그인을 쓰지 않는다.** Dataview 등 외부 플러그인 의존이 없다.
- **Obsidian이 없어도 저장소는 그대로 동작한다.** 이 폴더를 지워도 아무것도 깨지지 않는다. 링크로 하는 탐색은 [`HOME.md`](../../HOME.md)의 표가 그대로 담당한다.

## 뷰 목록

### study-overview.base

| 뷰 | 거르는 것 |
|---|---|
| 진행 중인 과제 | `assignment` 중 `open`, `in-progress` |
| 예정된 시험 | `exam` 중 `planned` |
| 열린 질문 | `question` 중 `open`, `investigating` |
| 진행/예정 복습 | `review` 중 `planned`, `in-progress` |
| 확인 필요 | 타입과 무관하게 `needs-review` |

### knowledge-browser.base

| 뷰 | 거르는 것 |
|---|---|
| 강의 | `lecture`. 과목(`course`)으로 묶는다 |
| 개념 | `concept` |
| 자료 | `resource` |
| 기출 | `past-exam` |

Cluster 뷰는 두지 않는다. Cluster는 표로 훑는 것이 아니라 열어서 읽는 지도다. Course 뷰도 두지 않는다. 과목 단위 화면은 CRS 노트의 대시보드가 정본이다.

## 날짜를 추측하지 않는다

**어떤 뷰도 `due`나 `date`로 거르지 않는다.** 스키마가 날짜와 확정 여부를 따로 두는 이유는 확인되지 않은 일정을 확정된 것처럼 다루지 않기 위해서다. 날짜로 걸러 버리면 미확정 항목이 화면에서 사라져 그 원칙이 UI에서 깨진다.

대신 `due_status`, `date_status`, `scope_status`를 **열로 함께 보여 준다.** `unknown`이나 `needs-review`가 그대로 눈에 보이는 것이 의도다.

## fixture를 잡지 않는다

`_system/docs/` 아래의 검증용 가상 노트와 `_system/templates/`의 양식에도 실제와 같은 `type`, `status` 값이 들어 있다. 그대로 두면 뷰가 학습 노트 대신 그것들을 보여 준다.

두 파일 모두 최상위 `filters`에서 대상 폴더를 제한한다. `study-overview`는 `study/`만, `knowledge-browser`는 `study/`와 `wiki/`만 본다. 최상위 `filters`는 모든 뷰에 AND로 결합된다.

**실제 학습 노트가 없는 동안에는 모든 뷰가 0행인 것이 정상이다.**

## 같은 파일명 구분

`study/`는 `study/<term>/<course-slug>/<kind>/` 중첩 구조다. `file.inFolder("study")`는 하위 폴더까지 포함하므로 학기·과목 폴더가 늘어도 뷰를 고치지 않는다.

CRS는 과목마다 파일명이 모두 `course.md`이고, 다른 노트도 과목끼리 파일명이 겹칠 수 있다. 그래서 파일명 옆에 frontmatter `title`(`note.title`, 제목)과 파일이 있는 폴더(`file.folder`, 폴더)를 열로 보여 준다. 폴더의 `<term>/<course-slug>`로 학기와 과목을 구분한다. 모든 노트가 `wiki/concepts/`에 있는 개념 뷰에는 제목 열만 더했다.

## 행 정렬

파일의 `order`는 **열 순서**다. 행 정렬은 그것과 별개이며, Obsidian에서 열 머리를 눌러 정렬하면 그 상태가 `sort` 키로 이 파일에 저장될 수 있다. 열 너비를 조절하면 `columnSize`가 같은 방식으로 저장된다. 공식 Bases 문법 문서에는 두 키의 설명이 아직 없다.

저장소에는 **의도적으로 정한 정렬만** 남긴다. 화면에서 우연히 만들어진 `sort`와 개인 화면 상태인 `columnSize`는 커밋하지 않는다.

## Graph

Graph 설정(`.obsidian/graph.json`)은 저장소에 두지 않는다. 확대 배율이나 창 상태 같은 개인 UI 값이 같은 파일에 섞이기 때문이다. 각자 아래를 설정한다.

- Graph의 Filters 검색어: `-path:_system -path:raw -path:inbox`
- 시스템 문서, 원본, 미분류 입력을 화면에서 빼는 것이 목적이다.

**다만 현재 Graph의 쓸모는 제한적이다.** 노트 사이의 관계는 frontmatter의 ID 목록(`course`, `concepts`, `resources` 등)으로 저장되며, 이것은 Obsidian이 인식하는 링크가 아니다. 파일명과 ID도 서로 다르다. 이 구조는 의도된 것이고 P8에서 바꾸지 않았다.

Concept를 중심으로 한 Local Graph를 depth 1~2로 보는 것은 실제 링크가 충분히 쌓인 뒤에 의미가 생긴다.
