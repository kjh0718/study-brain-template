# 02. Architecture

## 상위 구조
```text
study-brain-template/
├─ README.md
├─ HOME.md
├─ SECOND-BRAIN.md
├─ AGENTS.md
├─ CLAUDE.md
├─ GEMINI.md
├─ .gitignore
├─ inbox/
├─ raw/
│  ├─ transcripts/
│  ├─ resources/
│  ├─ past-exams/
│  ├─ assignments/
│  ├─ notices/
│  └─ documents/
├─ study/
│  ├─ courses/
│  ├─ lectures/
│  ├─ resources/
│  ├─ assignments/
│  ├─ exams/
│  ├─ past-exams/
│  ├─ course-facts/
│  ├─ questions/
│  └─ reviews/
├─ wiki/
│  ├─ concepts/
│  ├─ patterns/
│  ├─ clusters/
│  │  └─ _topics.md
│  └─ index.md
├─ _system/
│  ├─ schemas/
│  ├─ templates/
│  ├─ workflows/
│  ├─ docs/
│  └─ log.md
├─ .agents/
│  ├─ hooks/
│  └─ skills/
└─ .claude/
   ├─ hooks/
   └─ skills/
```

## 계층 역할
### inbox
아직 분류되지 않은 입력의 임시 영역. 아직 구조화 지식이 아니다.

### raw
Evidence Layer. 원문을 가능한 그대로 보존한다.
- transcripts: 수업 전체 전사
- resources: 교수 PPT/PDF/교재/프린트 원본 또는 참조
- past-exams: 족보 원본 또는 참조
- assignments: 과제 원문
- notices: LMS/교수 공지
- documents: 기타 원자료

Raw는 AI가 편의를 위해 조용히 재작성하는 영역이 아니다.

### study
Course-bound Structured Layer.
특정 과목/학기와 직접 연결되는 Lecture, Resource, Assignment, Exam, Past Exam, Course Fact, Question, Review를 둔다.

### wiki
Long-term Reusable Knowledge Layer.
특정 과목 하나에 종속되지 않는 Concept, Pattern, Cluster/MOC를 둔다.

### _system
Study Brain 내부 규격.
- schemas: frontmatter/데이터 모델
- templates: Note 생성 양식
- workflows: L1~L9
- docs: 설계/운영 문서
- log.md: append-only 작업 이력

### .agents / .claude
Agent 진입점. 핵심 규칙을 중복하지 않고 `SECOND-BRAIN.md`와 `_system/`을 읽고 실행한다.

## 정보 흐름
```text
INPUT
→ inbox / raw
→ INGEST
→ study
→ PROMOTION / LINKING
→ wiki
→ RECALL / REVIEW / MAINTAIN
```

## Raw/Structured 분리 예시
```text
raw/transcripts/원문
→ L1
study/lectures/구조화 Lecture

raw/resources/원본
→ L2
study/resources/Resource Note

raw/past-exams/원본
→ L3
study/past-exams/Past Exam 분석
```

## README-per-folder
`.gitkeep` 대신 각 의미 있는 폴더에 `README.md`를 둔다. README는 단순 placeholder가 아니라 다음을 정의하는 directory contract다.
- 폴더 목적
- 허용 문서
- 금지 문서
- 관련 schema/workflow
