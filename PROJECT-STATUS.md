# Study Brain Template — 현재 상태와 Git 동기화 계획

최종 확인일: 2026-09-09  
대상 폴더: `C:/Users/ranbo/Projects/study-brain-template`

## 1. 현재 결론

Study Brain의 **데이터 설계, 운영 기준, 새 노트 템플릿은 작성 완료** 상태다. 아직 일상 명령을 실제로 수행하는 Workflow 예시, Agent Skill, Hook, 진입 문서가 없으므로 **자동으로 수업 전사를 처리하는 완제품은 아니다.**

현재 단계에서도 GitHub에 올려 데스크탑과 노트북 사이에서 소스와 설계를 동기화할 수 있다. 이 저장소는 `study-brain-template` 개발 저장소로 사용하고, 나중에 완성된 템플릿에서 실제 개인 학습 자료를 담는 별도 비공개 저장소를 만드는 것이 최종 구조다.

## 2. 완성도

완성도는 무엇을 기준으로 보느냐에 따라 다르다.

| 기준 | 추정 완성도 | 의미 |
|---|---:|---|
| 설계·규격 | 약 75% | 11개 스키마, L1~L9 운영 기준, 템플릿이 완성됨 |
| 실제 자동 처리 기능 | 약 35% | Skill, Hook, Workflow 예시, L8 자동 검사 도구가 아직 없음 |
| GitHub 템플릿 출시 준비 | 약 50% | 핵심 파일은 있으나 README, Agent 진입점, 사용 안내와 통합 시험이 남음 |
| 전체 프로젝트 | 약 55% | 기반 3단계를 끝냈고 실행 계층과 배포 문서가 남음 |

이 숫자는 코드 줄 수가 아니라, 아래 전체 개발 단계에서 실제 사용에 필요한 비중을 기준으로 한 추정치다.

## 3. 완료된 단계

### 3.1 저장소 골격

- `inbox/`: 아직 분류하지 못한 입력
- `raw/`: 전사, 자료, 기출, 과제, 공지, 기타 원본
- `study/`: 과목에 종속되는 구조화 노트
- `wiki/`: 과목을 넘어 재사용되는 개념과 Cluster
- `_system/`: 스키마, 템플릿, Workflow, 검증 문서와 로그
- `.agents/`, `.claude/`: 향후 Skill과 Hook이 들어갈 위치
- 각 주요 폴더는 `.gitkeep` 대신 역할을 설명하는 `README.md`로 유지
- `.gitignore`는 최소 규칙만 유지

현재 `.gitignore`:

```gitignore
.DS_Store
**/.obsidian/workspace*.json
.claude/worktrees/
```

### 3.2 데이터 스키마

`_system/schemas/`에 공통 규칙과 11개 Core Type 규격이 있다.

| Prefix | Type | 저장 위치 | 역할 |
|---|---|---|---|
| CRS | course | `study/courses/` | 학기·분반 단위 과목 Dashboard |
| LEC | lecture | `study/lectures/` | 실제 수업 세션과 전사 기반 정리 |
| CON | concept | `wiki/concepts/` | 과목을 넘어 재사용하는 개념 |
| ASM | assignment | `study/assignments/` | 과제, 마감, 제출 상태 |
| EXM | exam | `study/exams/` | 현재 과목 시험 일정·범위·언급 |
| PEX | past-exam | `study/past-exams/` | 기출 원본·복원본 분석 |
| FAC | course-fact | `study/course-facts/` | 일정·정책 등 근거 있는 운영 사실 |
| QST | question | `study/questions/` | 이해·검증이 필요한 질문 |
| RES | resource | `study/resources/` | 여러 강의·과목에서 재사용하는 자료 |
| REV | review | `study/reviews/` | 복습 계획, 수행 결과와 다음 복습 |
| CLU | cluster | `wiki/clusters/` | 관련 지식을 연결하는 탐색 지도 |

공통 규칙에는 다음이 포함된다.

- ID 불변과 전역 충돌 확인
- `source`와 `sources`의 역할 구분
- 통제된 topic vocabulary
- 교수, LMS, 교재, 학생 자료, 외부 자료, AI 생성 내용의 출처 분류
- 사용자 작성 영역 보호
- 날짜와 관계 필드의 공통 형식
- `raw/` 원본과 구조화 노트의 경계

### 3.3 운영 기준서

루트 `SECOND-BRAIN.md`가 단일 운영 기준점이다. 주요 내용:

- 문서 우선순위와 충돌 처리
- `inbox → raw → study/wiki` 흐름
- 원문을 명령이 아닌 untrusted data로 취급
- 교수 발언, 자료 강조, AI 해석 분리
- 중복 노트 방지와 재실행 처리
- 사용자 필기 보호
- Course Dashboard의 결정적 갱신 방식
- Lecture–Resource 양방향 연결
- append-only 로그와 통제된 작업 코드
- 부분 실패와 복구 절차
- L1~L9의 입력, 선행조건, 읽는 범위, 처리 순서, 수정 대상, 완료·보류·재실행 조건

L1~L9 배치:

| Layer | 역할 |
|---|---|
| L1 | Lecture ingestion |
| L2 | Resource ingestion |
| L3 | Past-exam ingestion |
| L4 | Knowledge extraction |
| L5 | Fact and conflict reconciliation |
| L6 | Recall |
| L7 | Review |
| L8 | Maintain and integrity |
| L9 | Knowledge promotion and duplicate cleanup |

운영 기준 v1은 작성 완료됐지만 실제 Agent 실행 시험은 아직 하지 않았다.

### 3.4 노트 템플릿

`_system/templates/`에 11개 타입의 새 노트 템플릿과 사용 안내가 있다.

- 모든 템플릿은 해당 스키마의 필수 필드를 포함한다.
- 타입별 초기 상태값이 유효하다.
- 선택 필드는 확인됐을 때만 추가한다.
- `{{...}}` 자리표시자는 모두 치환해야 한다.
- 사용자 영역에 `AI-PROTECTED` 표식이 있다.
- Course의 `Related Notes`에는 자동 관리 경계가 있다.
- 기존 노트를 템플릿으로 통째로 덮어쓰지 않는다.

### 3.5 템플릿 검증 자료

`_system/docs/template-validation/`에 다음이 있다.

- `check_templates.py`: 템플릿과 스키마의 정합성 검사
- `build_filled.py`: 가상 값으로 11개 노트를 생성
- `check_filled_notes.py`: 가상 노트의 타입·관계·출처·대시보드 검사
- `filled/`: 실제 학습 자료가 아닌 가상 검증 fixture

2026-09-09 재검증 결과:

- 템플릿 11개 YAML 파싱 성공
- 스키마 필수 필드와 추가 필드 검사 통과
- 타입별 초기 status 검사 통과
- 가상 노트 11개 파싱 성공
- 로컬 source 파일 존재 검사 통과
- 외부 URL source 분기 확인
- Lecture–Resource 양방향 관계 검사 통과
- Course Dashboard 재구성 결과 일치
- Course 사용자 보호 영역 유지 확인
- 검사 결과 문제 0건

이 검증은 **템플릿 검증**이며, L1~L9 전체 Workflow가 실제로 동작한다는 통합 시험은 아니다.

## 4. 아직 비어 있거나 미구현인 부분

| 영역 | 현재 상태 | 다음 작업 |
|---|---|---|
| 루트 `README.md` | 0바이트 | 설치·사용법·구조·GitHub Template 안내 작성 |
| `HOME.md` | 0바이트 | 실제 Obsidian 시작 화면 설계 |
| `AGENTS.md` | 0바이트 | 범용 Agent가 SECOND-BRAIN을 읽도록 연결 |
| `CLAUDE.md` | 0바이트 | Claude Code 진입점 작성 |
| `GEMINI.md` | 0바이트 | Gemini 진입점 작성 |
| `wiki/index.md` | 0바이트 | Concept·Cluster 탐색 인덱스 작성 |
| `_system/workflows/` | README만 존재 | L1~L9 실행 예시·체크리스트 작성 |
| `.agents/skills/` | README만 존재 | capture, recall, maintain, ingest 계열 Skill 작성 |
| `.claude/skills/` | README만 존재 | Claude용 진입 Skill 또는 공용 Skill 연결 |
| Hook | README만 존재 | 세션 시작 안내와 안전 검사 Hook 검토 |
| `_topics.md` | 비어 있음 | 실제 자료 처리 시 통제 어휘를 점진적으로 등록 |
| `_system/log.md` | 비어 있음 | 첫 실제 쓰기 작업부터 append-only 기록 |
| L8 자동 검사 | 미구현 | 스키마·관계·ID·topic·source 검사 도구 작성 |
| 실제 통합 시험 | 미실행 | 가상 전사·자료·기출을 L1~L9 절차로 처리 |

## 5. 현재 알려진 제한과 주의점

1. 저장소가 Git으로 초기화되어 있고 브랜치는 `main`이지만 아직 첫 커밋이 없다.
2. GitHub 원격 저장소가 아직 연결되지 않았다.
3. `.obsidian/workspace.json`은 ignore되지만 `app.json`, `appearance.json`, `core-plugins.json`은 추적 대상이다. 이 설정들은 템플릿의 기본 Obsidian 환경으로 공유할지 첫 커밋 전에 최종 확인한다.
4. Obsidian `sync` Core Plugin이 활성화되어 있다. Git 동기화와 Obsidian Sync를 같은 Vault에 동시에 사용할 계획이라면 충돌 가능성을 검토한다.
5. 검증 스크립트는 Python과 PyYAML이 필요하다. 현재 PC에서는 기본 `python` 명령이 없어 Codex 번들 Python과 임시 PyYAML 경로로 실행했다. 다른 PC에서 재현 가능한 실행 방법과 의존성 선언은 아직 없다.
6. `_system/docs/template-validation/filled/`는 가상 자료다. 저장소에 포함할 수 있지만 사용자가 실제 학습 자료로 오인하지 않도록 README 안내를 유지한다.
7. 실제 개인 Brain에는 전사·과제·시험 정보가 들어갈 수 있으므로 반드시 별도 비공개 저장소를 사용한다.

## 6. GitHub에 올리는 목적과 저장소 구분

권장 구조:

```text
study-brain-template
├─ 공개 또는 비공개 개발 템플릿
├─ 스키마, 운영 규칙, 템플릿, Skill, Hook
└─ 실제 개인 수업 자료 없음

my-study-brain
├─ study-brain-template에서 생성
├─ 비공개 GitHub 저장소
└─ 실제 전사, 과제, 시험, 복습 데이터
```

현재는 미완성 개발본이므로 `study-brain-template`을 **비공개 GitHub 저장소로 먼저 업로드**하는 것이 안전하다. 공개 전환은 루트 README, 사용법, 라이선스, 예제의 개인정보 여부를 검토한 뒤 진행한다.

## 7. 데스크탑·노트북 전환 방법

### 첫 업로드를 완료한 PC

```powershell
git status
git add .
git commit -m "Initialize Study Brain template"
git push -u origin main
```

### 다른 PC에서 처음 받기

```powershell
Set-Location "$HOME/Projects"
git clone <PRIVATE_REPOSITORY_URL> study-brain-template
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

한 PC의 변경을 push하지 않은 채 다른 PC에서 같은 파일을 수정하면 충돌할 수 있다. PC를 바꾸기 전에 `status → add → commit → push`, 시작할 때 `pull → status` 순서를 습관으로 둔다.

## 8. 다음 개발 계획

### 단계 4 — Workflow 예시와 체크리스트

`_system/workflows/`에 L1~L9 보조 문서를 작성한다. 판단 정책은 SECOND-BRAIN에 유지하고, 이 폴더에는 실제 입력 예시, 체크리스트, 예상 출력과 실패 복구 예시만 둔다.

### 단계 5 — Skill과 Agent 진입점

- `capture`: 입력 종류를 판별해 적절한 Layer로 연결
- `ingest-lecture`, `ingest-resource`, `ingest-past-exam`
- `recall`, `review`, `maintain`
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`에서 SECOND-BRAIN을 먼저 읽도록 연결

### 단계 6 — Hook과 L8 검사 도구

- 세션 시작 시 운영 기준 안내
- ID, 필수 필드, 상태값, 관계, source, topic 검사
- 검사 모드와 수정 모드 분리

### 단계 7 — 사용자 문서와 Obsidian 화면

- 루트 README
- HOME Dashboard
- wiki/index
- 설치·업데이트·Git 동기화 안내

### 단계 8 — 가상 통합 시험

- 첫 Course가 없는 상태에서 전사 ingest
- 같은 전사 재입력
- 미등록 Resource 연결
- 애매한 과제 마감과 시험 일정 충돌
- 기출과 Concept 연결
- Review 회차 생성과 재개
- 사용자 보호 영역이 있는 노트 재처리
- 중간 실패 후 복구

### 단계 9 — 템플릿 공개 준비

- 문서와 예제에서 개인정보 제거 확인
- LICENSE와 기여 정책 결정
- GitHub Template Repository 설정
- 실제 비공개 `my-study-brain` 생성 및 데스크탑·노트북 clone 시험

## 9. 다음 작업자가 읽을 순서

1. `PROJECT-STATUS.md`
2. `SECOND-BRAIN.md`
3. `_system/schemas/README.md`와 해당 타입 스키마
4. `_system/templates/README.md`
5. `_system/workflows/README.md`

규칙을 바꾸려면 문서 간 역할을 확인한다. 데이터 필드·상태값은 스키마, 실행 판단은 SECOND-BRAIN, 예시와 체크리스트는 Workflow 문서가 기준이다.

## 10. Git 상태

이 문서를 작성하기 직전 기준:

```text
branch: main
commits: 0
remote: 없음
working tree: 모든 프로젝트 파일이 untracked
```

첫 커밋과 GitHub 업로드가 완료되면 저장소 URL과 첫 커밋 ID를 이 절에 기록한다.
