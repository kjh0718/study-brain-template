# 08. Implementation Roadmap

## Phase 0 — Reference Research
기존 `second-brain-template`, `project-brain`, `eodaego-brain`, 공개 AI-native Second Brain에서 좋은 패턴을 비교한다.

결과는 `KEEP / MODIFY / REMOVE / ADD` 관점으로 정리한다.

## Phase 1 — Repository Skeleton
현재 목표 구조:
```text
inbox/
raw/
study/
wiki/
_system/
.agents/
.claude/
```

원칙:
- `.gitkeep` 없음
- README-per-folder
- 최소 `.gitignore`

## Phase 2 — Schema Layer
권장 작성 순서:
```text
common
→ course
→ lecture
→ resource
→ concept
→ assignment
→ exam
→ past-exam
→ course-fact
→ question
→ review
→ cluster
```

각 Schema는 다음을 정의한다.
- type
- ID 규칙
- 필수/선택 frontmatter
- status
- 본문 기본 구조
- 관계
- source/provenance
- lifecycle
- validation

## Phase 3 — SECOND-BRAIN.md
Schema 안정화 후 작성한다.

포함:
- 전체 철학
- Vault layout
- 공통 규칙
- Topic vocabulary
- status/supersede
- trust/authority
- protected sections
- retrieval
- logging
- L1~L9
- capture/recall/maintain

운영 규칙의 Single Source of Truth로 만든다.

## Phase 4 — Workflows
`_system/workflows/`에 다음 세부 문서를 작성한다.

```text
l1-lecture-ingestion.md
l2-resource-ingestion.md
l3-past-exam-ingestion.md
l4-knowledge-extraction.md
l5-fact-conflict-reconciliation.md
l6-recall.md
l7-review.md
l8-maintenance.md
l9-knowledge-promotion.md
```

SECOND-BRAIN.md에는 핵심 규칙, workflow 문서에는 실행 세부사항을 둔다.

시스템 파일명은 lowercase-kebab-case를 기본으로 한다. Windows와 macOS의 기본 파일 시스템은 대소문자를 구분하지 않고 Linux는 구분하므로, 대문자를 섞으면 기기마다 링크가 깨질 수 있다. 문서 제목과 본문의 `L1`, `L2` 표기는 그대로 쓴다.

## Phase 5 — Note Templates
`_system/templates/`:
```text
course.md
lecture.md
concept.md
assignment.md
exam.md
past-exam.md
course-fact.md
question.md
resource.md
review.md
cluster.md
```

## Phase 6 — Skills
기본:
```text
capture
recall
maintain
```

전문화:
```text
ingest-lecture
ingest-resource
ingest-past-exam
review
course-status
check-conflict
```

특정 agent wrapper는 얇게 유지한다.

## Phase 7 — Hooks
세션 시작 시 전체 Vault가 아니라 최소 컨텍스트만 로드한다.

예:
- 활성 Course
- 최근 log
- 관련 topics
- current cluster

## Phase 8 — Obsidian UX
핵심 데이터 규격 이후 추가:
- HOME dashboard
- Course dashboard
- Bases
- Graph
- Review view
- Open Questions view
- Active Assignments view

## Phase 9 — Sample Test
실제와 유사한 샘플:
1. Lecture transcript
2. Professor PDF/PPT
3. Assignment notice
4. 충돌하는 exam date
5. Past exam
6. Duplicate concept
7. Protected My Notes

## Phase 10 — GitHub Template
테스트 통과 후 GitHub Template Repository로 설정한다.

## Phase 11 — Private Brain
Template에서 실제 Private repo 생성 후 Desktop/Laptop에 clone한다.

## Phase 12 — DEVSTUDY Migration
기존 자료를 한꺼번에 덤프하지 않고:
```text
Course
→ Lecture
→ Resource
→ Concept
→ Assignment/Exam
→ Past Exam
→ Review
```
순으로 옮긴다.

검증 후 기존 OneDrive DEVSTUDY를 정리한다.
