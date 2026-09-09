# study-brain-template

대학 학습을 위한 AI-native Second Brain 템플릿이다. 수업 전사, 교수 자료, 과제, 시험, 기출, 개념, 복습을 하나의 규칙 아래 쌓고 근거와 함께 다시 꺼내는 것을 목표로 한다.

Obsidian 저장소이면서 동시에 여러 AI 에이전트가 같은 규칙으로 동작하는 운영 규격이다.

> **현재 상태**: 개발 중이다. 데이터 규격, 운영 기준서, 실행 워크플로 문서, 노트 템플릿은 작성됐고 자동 실행 계층(스킬·훅)은 아직 없다. 자세한 것은 [PROJECT-STATUS.md](PROJECT-STATUS.md)를 본다.

## 기존 second-brain-template의 fork가 아니다

이름만 바꾼 학습용 변형이 아니다. 기존 Project Brain 계열의 좋은 설계와 다른 AI-native Second Brain의 패턴을 참고하되, 학습 도메인에 맞게 데이터 모델부터 다시 설계했다.

**가져온 것**: 중앙 운영 기준서, frontmatter 우선 검색, 원본 보존, 통제된 topic 어휘, Cluster/MOC, 충돌 감지, supersede 이력, append-only 로그, capture/recall/maintain, 원문을 명령이 아닌 데이터로 다루는 규칙, 사람 확인 정책.

**버린 것**: meeting, decision, issue, project report, issue candidate, build workflow 등 프로젝트 관리 개념. 학습에는 대응물이 없거나 다른 형태여야 한다.

**새로 만든 것**: Lecture와 Resource의 N:N 관계, 현재 시험(EXM)과 기출(PEX)의 분리, 교수 발언·자료 강조·AI 해석의 3중 구분, 운영 사실(Course Fact)의 충돌 조정, 모호한 날짜를 확정하지 않는 정책.

## 구조

```text
inbox/    분류하지 못한 입력의 임시 보관소
raw/      원본 보존 영역. 전사, 자료, 기출, 과제, 공지, 문서
study/    과목·학기에 묶인 구조화 노트
wiki/     과목을 넘어 재사용되는 장기 지식
_system/  스키마, 템플릿, 워크플로, 설계 문서, 로그
```

흐름은 한 방향이다.

```text
inbox → raw → study · wiki
```

`raw/`는 증거이고 `study/`·`wiki/`는 해석이다. 구조화 노트가 원본을 가리키며 그 반대는 없다.

## 11 Core Type

| Prefix | Type | 위치 | 역할 |
|---|---|---|---|
| CRS | course | `study/courses/` | 학기·분반 단위 과목 대시보드 |
| LEC | lecture | `study/lectures/` | 실제 수업 세션 하나 |
| RES | resource | `study/resources/` | 자료. 여러 강의가 공유한다 |
| ASM | assignment | `study/assignments/` | 과제, 마감, 제출 상태 |
| EXM | exam | `study/exams/` | **현재** 과목의 시험 |
| PEX | past-exam | `study/past-exams/` | 기출·족보 분석 |
| FAC | course-fact | `study/course-facts/` | 일정·정책 등 운영 사실 |
| QST | question | `study/questions/` | 이해·검증이 필요한 질문 |
| REV | review | `study/reviews/` | 복습 회차와 학습 상태 |
| CON | concept | `wiki/concepts/` | 과목을 넘어 재사용하는 개념 |
| CLU | cluster | `wiki/clusters/` | 주제 중심 탐색 지도 |

`wiki/patterns/`는 Core Type이 아니다. 여러 근거가 쌓였을 때 L9에서만 만드는 파생 지식 영역이다.

## 워크플로

L1~L9로 나뉜다. 판단 기준은 [`SECOND-BRAIN.md`](SECOND-BRAIN.md)에, 실행 절차·검색 명령·보고 형식은 [`_system/workflows/`](_system/workflows/README.md)에 있다.

| | 이름 | 하는 일 |
|---|---|---|
| L1 | Lecture ingestion | 전사 하나를 보존하고 Lecture로 정리 |
| L2 | Resource ingestion | 자료를 한 번만 등록해 여러 강의에서 재사용 |
| L3 | Past-exam ingestion | 기출을 문항 단위로 분석 |
| L4 | Knowledge extraction | 개념과 질문 추출 |
| L5 | Fact & conflict reconciliation | 과제·시험·운영 사실과 충돌 조정 |
| L6 | Recall | 근거를 붙여 다시 꺼내기 (읽기 전용) |
| L7 | Review | 복습 회차 계획·수행·기록 |
| L8 | Maintain & integrity | 무결성 검사와 정리 |
| L9 | Knowledge promotion & merge | 패턴 승격과 중복 정리 |

일상적으로는 세 동사로 쓴다. `capture`(새 입력 넣기), `recall`(찾기), `maintain`(정리).

### 이 시스템이 하지 않는 것

설계상 일부러 하지 않는 것들이다. 기능 부족이 아니라 정책이다.

- 녹음을 텍스트로 바꾸지 않는다. 전사는 외부 도구로 만들어 넣는다.
- 모호한 마감을 날짜로 확정하지 않는다.
- 족보에 자주 나왔다는 이유로 이번 시험 출제를 확정하지 않는다.
- 상충하는 사실을 자동으로 덮어쓰지 않는다.
- 사용자가 쓴 영역을 고치지 않는다.

## Template repo와 Private Brain

저장소를 둘로 나눈다.

| | `study-brain-template` (이 저장소) | 개인 Brain (별도 Private repo) |
|---|---|---|
| 담는 것 | 규칙, 스키마, 템플릿, 워크플로, 진입점 | 실제 수업·전사·과제·시험·개념 |
| 공개 | 공개 가능 | Private |
| 개인 자료 | **넣지 않는다** | 넣는다 |

이 저장소에 실제 강의 전사나 개인 학습 자료를 넣지 않는다. 여기 있는 예시 값은 전부 가상 데이터다.

동기화는 Git으로 한다. OneDrive 같은 파일 동기화에 의존하지 않는다.

## 앞으로의 사용 흐름

아직 여기까지 오지 않았다. 목표 흐름은 다음과 같다.

```text
템플릿 완성
→ GitHub Template Repository로 설정
→ 그 템플릿에서 Private Brain 생성
→ Desktop / Laptop에서 clone
→ 실제 수업 자료 이관
```

## 문서

| 문서 | 내용 |
|---|---|
| [`SECOND-BRAIN.md`](SECOND-BRAIN.md) | **운영 규칙의 정본.** 원칙과 L1~L9의 판단 기준 |
| [`AGENTS.md`](AGENTS.md) | 에이전트 진입점 (도구 중립) |
| [`CLAUDE.md`](CLAUDE.md) / [`GEMINI.md`](GEMINI.md) | 도구별 진입점 |
| [`HOME.md`](HOME.md) | Obsidian 시작 화면 |
| [`_system/schemas/`](_system/schemas/README.md) | 11개 Type의 필드·상태값·관계 규격 |
| [`_system/workflows/`](_system/workflows/README.md) | L1~L9 실행 문서 |
| [`_system/templates/`](_system/templates/README.md) | 새 노트 작성 양식 |
| [`_system/docs/plan/`](_system/docs/plan/README.md) | 설계 배경과 결정 이력 |
| [`PROJECT-STATUS.md`](PROJECT-STATUS.md) | Phase별 현재 구현 상태 |

에이전트로 작업한다면 `SECOND-BRAIN.md`를 먼저 끝까지 읽는다. 이 README는 소개이지 운영 기준이 아니다.

## 검증

노트 규격을 자동으로 검사하는 스크립트가 [`_system/docs/template-validation/`](_system/docs/template-validation/README.md)에 있다. Python 3과 PyYAML만 쓰며 별도 의존성은 없다.

```bash
cd _system/docs/template-validation
python check_templates.py                          # 템플릿 자체 검사
python build_filled.py && python check_filled_notes.py   # 값을 채운 가상 노트 검사
```

실제 학습 노트 전체의 무결성 검사(L8)는 아직 수동 절차다.
