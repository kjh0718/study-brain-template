# Study Brain Template — 현재 상태

최종 확인일: 2026-09-09

이 문서는 무엇이 실제로 만들어졌고 무엇이 아직 없는지를 기록한다. 운영 규칙은 [`SECOND-BRAIN.md`](SECOND-BRAIN.md)에, 소개는 [`README.md`](README.md)에 있다.

## 1. 현재 결론

**설계·규격 계층과 실행 문서 계층은 작성됐고, 자동 실행 계층은 아직 없다.**

데이터 스키마, 운영 기준서, L1~L9 실행 문서, 노트 템플릿, 에이전트 진입점이 있다. 사람이나 에이전트가 이 문서들을 읽고 절차를 따라 수업 전사를 처리할 수는 있다. Scenario A~K 통합 시험으로 그 문서들이 서로 일관되는지도 확인했다. 하지만 명령 한 번으로 자동 처리하는 Skill과 Hook은 없고, 에이전트가 실제로 그 문서를 읽고 같은 결과를 내는지는 검증되지 않았다.

이 저장소는 `study-brain-template` **개발 저장소**로 쓴다. 실제 학습 자료는 템플릿 완성 후 별도 비공개 저장소에 담는다.

## 2. Phase별 상태

| Phase | 상태 | 근거 |
|---|---|---|
| P1 저장소 골격 | **complete** | 폴더 구조, README-per-folder, 최소 `.gitignore`. `.gitkeep` 없음 |
| P2 Schema Layer | **complete** | `common.md` + 11개 Type 스키마. 자동 검사 통과 |
| P3 SECOND-BRAIN.md | **complete** | 운영 원칙과 L1~L9 판단 기준 |
| P4 Workflows | **complete** | `_system/workflows/`에 L1~L9 실행 문서 9개 + README |
| P5 Note Templates | **complete** | 11개 템플릿 + 사용 안내. 자동 검사 통과 |
| P6 Skills | **not started** | `.agents/skills/`, `.claude/skills/`에 README만 |
| P7 Hooks | **not started** | `.agents/hooks/`, `.claude/hooks/`에 README만 |
| P8 Obsidian UX | **partial** | `HOME.md`, `wiki/index.md`는 있음. 자동 갱신 뷰·Bases·Graph 설정 없음 |
| P9 Tests | **partial** | 템플릿 검증 + Scenario A~K 통합 시험 통과(FAIL 0). 에이전트 실행 시험과 Git 동기화 시험은 미실행 |
| P10 GitHub Template | **not started** | Template Repository 설정, LICENSE, 공개 검토 남음 |
| P11 Private Brain | **not started** | 실제 비공개 저장소 미생성 |
| P12 DEVSTUDY Migration | **not started** | 기존 자료 이관 미착수 |

P8을 partial로 둔 이유는 시작 화면과 색인이 plain Markdown 수준으로만 있기 때문이다. P9는 문서 간 일관성 시험은 통과했지만 에이전트 실행 시험과 Git 동기화 시험이 남아 partial이다.

## 3. 만들어진 것

### 3.1 저장소 골격

```text
inbox/    분류 전 입력
raw/      원본 보존 (transcripts, resources, past-exams, assignments, notices, documents)
study/    과목 종속 구조화 노트 (courses, lectures, resources, assignments,
          exams, past-exams, course-facts, questions, reviews)
wiki/     장기 지식 (concepts, clusters, patterns)
_system/  schemas, templates, workflows, docs, log.md
.agents/  .claude/   에이전트 진입 위치
```

각 주요 폴더의 `README.md`는 목적, 여기 두는 것, 여기 두지 않는 것, 규격, 관련 워크플로를 명시한다. `.gitkeep`을 쓰지 않는다.

현재 `.gitignore`:

```gitignore
.DS_Store
**/.obsidian/workspace*.json
.claude/worktrees/
```

### 3.2 데이터 스키마

`_system/schemas/`에 공통 규칙과 11개 Core Type이 있다.

| Prefix | Type | 위치 |
|---|---|---|
| CRS | course | `study/courses/` |
| LEC | lecture | `study/lectures/` |
| RES | resource | `study/resources/` |
| ASM | assignment | `study/assignments/` |
| EXM | exam | `study/exams/` |
| PEX | past-exam | `study/past-exams/` |
| FAC | course-fact | `study/course-facts/` |
| QST | question | `study/questions/` |
| REV | review | `study/reviews/` |
| CON | concept | `wiki/concepts/` |
| CLU | cluster | `wiki/clusters/` |

`common.md`가 정하는 것: ID 형식 계약과 Type별 권장 형태, `source`와 `sources`의 구분, 통제된 topic 어휘, authority 분류, 보호 영역, 날짜·관계 필드의 공통 형식, `raw/`와 구조화 노트의 경계.

### 3.3 운영 기준서

루트 `SECOND-BRAIN.md`가 단일 기준점이다. 문서 우선순위, `inbox → raw → study·wiki` 흐름, 원문을 untrusted data로 다루는 규칙, 교수 발언·자료 강조·AI 해석의 구분, 중복 방지와 재실행 처리, 사용자 필기 보호, Course 대시보드의 결정적 갱신, Lecture–Resource 양방향 연결, append-only 로그와 통제된 작업 코드, 부분 실패 복구, L1~L9의 입력·선행조건·읽는 범위·처리 순서·수정 대상·완료/보류/재실행 조건을 담는다.

### 3.4 워크플로 실행 문서

`_system/workflows/`에 L1~L9 문서가 있다. 파일명은 lowercase-kebab-case다.

| | 문서 | 저장소 쓰기 |
|---|---|---|
| L1 | `l1-lecture-ingestion.md` | 예 |
| L2 | `l2-resource-ingestion.md` | 예 |
| L3 | `l3-past-exam-ingestion.md` | 예 |
| L4 | `l4-knowledge-extraction.md` | 예 |
| L5 | `l5-fact-conflict-reconciliation.md` | 예 |
| L6 | `l6-recall.md` | 아니오 |
| L7 | `l7-review.md` | 예 |
| L8 | `l8-maintenance.md` | 모드에 따라 다름 |
| L9 | `l9-knowledge-promotion.md` | 예 |

각 문서는 같은 구성이다. 시작 전 확인, 검색 방법, 실행 체크리스트, 사용자 확인 지점, 하지 않는 것, 완료 조건, 완료 보고 형식, 로그 기록, 실행 예시.

판단 기준은 복제하지 않고 `SECOND-BRAIN.md`로 위임한다. 공통 검색 명령은 `workflows/README.md`에 한 번만 둔다.

### 3.5 노트 템플릿

`_system/templates/`에 11개 타입의 템플릿과 사용 안내가 있다. 필수 필드 포함, 타입별 유효한 초기 상태값, `{{...}}` 자리표시자, `AI-PROTECTED` 표식, Course `Related Notes`의 `AUTO-MANAGED` 경계를 갖춘다. 특정 플러그인 문법을 쓰지 않는다.

### 3.6 에이전트 진입점

| 파일 | 역할 |
|---|---|
| `AGENTS.md` | 도구 중립 공통 규약. 읽을 순서, 문서 우선순위, 자주 깨지는 다섯 가지 |
| `CLAUDE.md` | Claude Code에서만 다른 것. 도구 선택, 병렬 처리, 전역 지침과의 우선순위 |
| `GEMINI.md` | Gemini에서만 다른 것. 긴 컨텍스트를 이유로 전체를 읽지 않는 규칙 |

세 파일 모두 `SECOND-BRAIN.md`를 정본으로 가리키며 규칙을 복제하지 않는다.

### 3.7 사용자 문서

`README.md`(소개·구조·현재 상태), `HOME.md`(Obsidian 시작 화면), `wiki/index.md`(장기 지식 색인), `wiki/clusters/_topics.md`(topic 어휘 registry, 아직 비어 있음).

### 3.8 검증 자료

`_system/docs/template-validation/`:

- `check_templates.py` — 템플릿과 스키마의 정합성
- `build_filled.py` — 가상 값으로 11개 노트 생성
- `check_filled_notes.py` — 가상 노트의 타입·ID 계약·관계·출처·대시보드 검사
- `filled/` — 실제 학습 자료가 아닌 가상 fixture

2026-09-09 재검증 결과: 템플릿 11개 YAML 파싱 성공, 필수·추가 필드 검사 통과, 타입별 초기 status 통과, 가상 노트 11개 파싱 성공, ID 형식 계약 통과, 로컬 source 존재 검사 통과, 외부 URL source 분기 확인, Lecture–Resource 양방향 통과, Course 대시보드 재구성 일치, 보호 영역 유지 확인. **문제 0건.**

이것은 **템플릿 검증**이며 워크플로 결과의 일관성은 아래 통합 시험이 본다.

### 3.9 통합 시험

`_system/docs/integration-test/`에 Scenario A~K 통합 시험이 있다.

- `build_fixtures.py` — 가상 vault(정상 노트 34건)와 고의 오류 fixture 9건 생성
- `check_scenarios.py` — Scenario A~K + 공통 스키마 적합성 + L8 탐지 검사. FAIL이 있으면 exit 1
- 보고서와 fixture 설명은 [`integration-test/README.md`](_system/docs/integration-test/README.md)

2026-09-09 결과: **PASS 11 / PASS WITH NOTES 2 / FAIL 0.**

이 시험이 EXM ID의 학기 간 충돌을 찾아냈고, 승인 후 `EXM-<과목 slug>-<term>-<exam_type>`으로 고쳤다. `common.md`의 Concept–topic 결합 문장, L1 재개 지점 매핑 부재, 어휘표 파싱 위험도 함께 잡아 수정했다.

**한계**: 문서대로 만든 결과물이 규칙과 일관되는지를 본다. 에이전트가 실제로 그 문서를 읽고 같은 결과를 내는지는 검증하지 않는다.

## 4. 아직 없는 것

| 영역 | 현재 | 다음 작업 |
|---|---|---|
| `.agents/skills/`, `.claude/skills/` | README만 | `capture`, `recall`, `maintain` + ingest 계열 Skill |
| `.agents/hooks/`, `.claude/hooks/` | README만 | 세션 시작 시 최소 컨텍스트 로드 |
| `wiki/clusters/_topics.md` | 형식·규칙만 있고 registry 비어 있음 | 실제 자료 처리 시 점진적으로 등록 |
| `_system/log.md` | 비어 있음 | 첫 실제 쓰기부터 append-only 기록 |
| L8 자동 검사 | 수동 절차 | 스키마·관계·ID·topic·source 검사 도구 |
| Obsidian 뷰 | 없음 | Course 대시보드 뷰, Open Questions, Active Assignments |
| 에이전트 실행 시험 | 미실행 | 에이전트가 문서를 읽고 같은 결과를 내는지 확인. Skills 구현 이후 |
| Git 동기화 시험 | 미실행 | Desktop/Laptop 2대 필요 |
| LICENSE | 없음 | 공개 전 결정 |

## 5. 알려진 제한과 주의점

1. **에이전트가 문서를 그대로 수행하는지는 검증되지 않았다.** 통합 시험은 문서대로 만든 결과물의 일관성을 볼 뿐, 에이전트의 실제 동작을 보지 않는다.
2. 검증 스크립트는 가상 fixture만 본다. 실제 `study/`·`wiki/` 노트를 검사하는 L8 도구는 아직 없다.
3. 실행 환경은 Python 3.13.3 + PyYAML 6.0.3에서 확인했다. 의존성 선언 파일은 없다. 다른 PC에서는 PyYAML 설치가 필요할 수 있다.
4. 검증 스크립트는 Windows 기본 콘솔(cp949)에서 출력이 깨지지 않도록 stdout을 UTF-8로 맞춘다. 이 처리를 지우면 한글·em dash 출력에서 `UnicodeEncodeError`가 난다.
5. `.obsidian/workspace*.json`은 ignore되지만 `app.json`, `appearance.json`, `core-plugins.json`은 추적된다. 템플릿의 기본 Obsidian 환경으로 공유할지 공개 전에 확정한다.
6. Obsidian `sync` Core Plugin이 활성화되어 있다. Git 동기화와 함께 쓰면 충돌할 수 있으므로 하나로 정한다. 이 프로젝트의 결정은 Git이다.
7. `_system/docs/template-validation/filled/`와 `_system/docs/integration-test/vault/`는 가상 자료다. 실제 학습 자료로 오인하지 않도록 README 안내와 파일 상단 배너를 유지한다.
8. 실제 개인 Brain에는 전사·과제·시험 정보가 들어가므로 반드시 별도 비공개 저장소를 쓴다.

## 6. 저장소 구분

```text
study-brain-template          ← 이 저장소
├─ 스키마, 운영 규칙, 템플릿, 워크플로, 진입점
└─ 실제 개인 수업 자료 없음

my-study-brain                ← 아직 만들지 않음
├─ study-brain-template에서 생성
├─ 비공개 GitHub 저장소
└─ 실제 전사, 과제, 시험, 복습 데이터
```

현재는 미완성 개발본이다. 공개 전환은 개인정보 검토, LICENSE, 사용법 문서를 마친 뒤에 한다.

## 7. 데스크탑·노트북 전환 방법

### 다른 PC에서 처음 받기

```powershell
Set-Location "$HOME/Projects"
git clone https://github.com/kjh0718/study-brain-template.git
Set-Location study-brain-template
git status
```

### PC를 바꾸기 전

```powershell
git status
git add .
git commit -m "Describe the work completed"
git push
```

### 다른 PC에서 작업을 시작할 때

```powershell
git pull --ff-only
git status
```

한 PC의 변경을 push하지 않은 채 다른 PC에서 같은 파일을 수정하면 충돌한다. 바꾸기 전에 `status → add → commit → push`, 시작할 때 `pull → status`를 습관으로 둔다.

## 8. 다음 개발 계획

### 단계 A — Skills (P6)

- `capture`: 입력 종류를 판별해 적절한 레이어로 연결
- `recall`, `maintain`
- `ingest-lecture`, `ingest-resource`, `ingest-past-exam`, `review`, `check-conflict`

스킬은 규칙을 다시 정의하지 않는다. `SECOND-BRAIN.md`와 해당 워크플로 문서를 읽어 실행하는 얇은 진입점으로 둔다.

### 단계 B — Hooks (P7)

세션 시작 시 저장소 전체가 아니라 최소 컨텍스트만 로드한다. 활성 Course, 최근 로그, 관련 topics 정도다.

### 단계 C — 에이전트 실행 시험 (P9 잔여)

Scenario A~K 통합 시험은 통과했다. 남은 것은 에이전트가 `SECOND-BRAIN.md`와 워크플로 문서를 실제로 읽고 같은 결과를 내는지 확인하는 것이다. Skills 구현 이후에 가능하며, `integration-test/vault/`를 기대 출력으로 재사용한다.

### 단계 D — L8 자동 검사 도구

현재 `l8-maintenance.md`의 검사 항목 10개를 스크립트로 만든다. 새 의존성 없이 표준 라이브러리와 PyYAML만 쓴다.

### 단계 E — Obsidian UX (P8)

Course 대시보드 뷰, Open Questions, Active Assignments, Review 뷰. 플러그인 의존을 최소화한다.

### 단계 F — 공개 준비 (P10~P12)

개인정보 검토, LICENSE, GitHub Template Repository 설정, 실제 비공개 Brain 생성과 이관.

## 9. 다음 작업자가 읽을 순서

1. `PROJECT-STATUS.md` (이 문서)
2. `SECOND-BRAIN.md`
3. `AGENTS.md`와 도구별 진입 파일
4. `_system/schemas/README.md`와 해당 타입 스키마
5. `_system/workflows/README.md`와 해당 레이어 문서
6. `_system/templates/README.md`

규칙을 바꿀 때는 역할을 확인한다. **데이터 필드·상태값·ID는 스키마, 실행 판단은 SECOND-BRAIN, 체크리스트와 예시는 워크플로 문서**가 기준이다.

## 10. Git 상태

```text
remote: https://github.com/kjh0718/study-brain-template.git
default branch: main
최초 커밋: 8f4c421 Initialize Study Brain template
```

이 문서를 갱신한 시점의 작업은 아직 커밋되지 않았다. 작업 브랜치와 커밋 여부는 `git status`로 확인한다.
