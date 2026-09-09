# 03. Data Model

## 11 Core Types
| Prefix | Type | 역할 | 위치 |
|---|---|---|---|
| CRS | course | 과목 Dashboard/허브 | `study/courses/` |
| LEC | lecture | 실제 수업 세션 | `study/lectures/` |
| CON | concept | 재사용 가능한 장기 개념 | `wiki/concepts/` |
| ASM | assignment | 과제/제출/마감 | `study/assignments/` |
| EXM | exam | 현재 과목의 실제 시험 | `study/exams/` |
| PEX | past-exam | 족보/과거 시험 분석 | `study/past-exams/` |
| FAC | course-fact | 과목 운영 사실 | `study/course-facts/` |
| QST | question | 이해/확인/교수 질문 | `study/questions/` |
| RES | resource | 학습 자료 분석 | `study/resources/` |
| REV | review | 복습/시험 대비 상태 | `study/reviews/` |
| CLU | cluster | Concept/Study Note MOC | `wiki/clusters/` |

`wiki/patterns/`는 V1 Core Type이 아니라 L9에서 충분한 근거가 쌓일 때 승격하는 파생 지식 영역으로 둔다.

## 관계 개요
```text
                         COURSE
                           │
          ┌────────────────┼────────────────┐
          │                │                │
       Lecture          Resource           Exam
          │                │                │
     ┌────┼────┬─────┐     │                │
     │    │    │     │     │                │
     ▼    ▼    ▼     ▼     │                │
  Concept ASM  Fact Question               Past Exam
     │                     │                │
     └──────────┬──────────┴───────┬────────┘
                │                  │
                ▼                  ▼
             Cluster             Review
```

## 공통 Frontmatter 방향
```yaml
---
schema: 1
type: lecture
id: LEC-20260908-01
title: 운동량과 충격량
status: active
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
---
```

원칙:
- id는 생성 후 불변
- type은 통제값
- topics는 `_topics.md` controlled vocabulary
- 관계는 가능하면 ID 기반
- created는 불변
- updated는 의미 있는 write에서만 변경
- unknown을 사실처럼 생성하지 않음
- 중요한 사실은 provenance 보유

## ID 방향
전역 단순 카운터만 사용하지 않는다. Desktop/Laptop 동시 생성 충돌을 줄이는 사람이 읽을 수 있는 ID를 선호한다.

예:
```text
CRS-2026-2-general-physics-2
LEC-20260908-01
CON-momentum
ASM-general-physics-2-20260908-01
EXM-general-physics-2-2026-2-midterm
PEX-general-physics-2-2024-2-midterm
FAC-general-physics-2-20260908-01
QST-general-physics-2-20260908-01
RES-general-physics-2-ch03-slides
REV-general-physics-2-20260913-weekly
CLU-classical-mechanics
```

## 타입별 핵심
### Course
내용 덤프가 아니라 Dashboard. 최근 Lecture, 활성 Assignment, Exam, Course Fact, Concept, Open Question, Review, Resource를 연결한다.

### Lecture
실제 수업 세션 1회. Resource와 독립.
권장 본문:
`Summary / Core Content / Professor Emphasis / Formulas / Examples / Exam Related / Assignments / Course Facts / Concepts / Questions / Resources / Past Exam Links / Review Questions / My Notes / Source`

### Concept
과목별로 복제하지 않는 cross-course 지식.
신규 생성은 재사용성·반복성·핵심성·시험 중요도·이해 난도·연결성을 평가한다.

### Assignment
애매한 마감일은 추론하지 않는다.
```yaml
due: null
due_status: needs-review
```

### Exam
현재 과목의 실제 중간/기말/퀴즈. Lecture마다 새 EXM을 만들지 않고 기존 EXM에 근거를 누적한다.

### Past Exam
현재 Exam과 분리. 연도/학기/시험종류/교수/문제별 Concept/유형/난이도/답안 검증 상태를 분석한다. 과거 빈도는 현재 출제 확정 근거가 아니다.

### Course Fact
시험 일정, 휴강, 강의실, 출석, 평가비율, 제출방식 등 운영 사실. 변경 이력은 supersede로 추적한다.

### Question
`understanding`, `clarification`, `source-verification`, `professor` 등으로 학습 공백과 사실 검증을 관리한다.

### Resource
하나의 Resource는 한 번만 등록하고 Lecture와 N:N 관계를 갖는다.
```text
RES Chapter 3
├─ LEC 09/08 → 1-20p
├─ LEC 09/10 → 21-31p
├─ LEC 09/15 → 32-45p
└─ LEC 09/17 → 46-end
```

### Review
지식 자체가 아니라 학습 상태 출력. daily/weekly/exam-prep/concept 유형.

### Cluster
Concept/Lecture/Resource/Past Exam/Question을 주제 중심으로 연결하는 MOC.
