# 10. Decisions

## D-001 — 독립 Template
기존 `second-brain-template`을 그대로 fork하지 않는다. 여러 좋은 설계를 합쳐 Study 전용 독립 Template을 만든다.  
상태: **확정**

## D-002 — Template/Private Repo 분리
```text
study-brain-template
+
실제 private brain repo
```
상태: **확정**

## D-003 — Desktop/Laptop 동기화는 Git
OneDrive 대신 GitHub Private repo를 실제 Brain의 주 동기화 수단으로 사용한다.  
상태: **확정**

## D-004 — OneDrive는 핵심 구조에서 제거
기존 학습 자료는 migration 검증 전까지 백업 가능하지만 새 구조의 핵심 의존성은 아니다.\
상태: **확정**

## D-005 — Git LFS V1 강제 안 함
PDF/PPT/이미지 사용량을 본 뒤 필요하면 도입한다.  
상태: **확정**

## D-006 — 최소 .gitignore
과도한 ignore 정책을 Template이 강제하지 않는다.  
상태: **확정**

## D-007 — .gitkeep 사용 안 함
빈 폴더는 의미 있는 README로 유지한다.  
상태: **확정** — D-031로 일부 개정. 동적 `<term>/<course-slug>/<kind>` 폴더에는 README를 두지 않는다. `.gitkeep` 사용 안 함은 그대로 유지한다.

## D-008 — 정보 계층
```text
inbox
raw
study
wiki
_system
```
상태: **확정**

## D-009 — 11 Core Types
```text
CRS Course
LEC Lecture
CON Concept
ASM Assignment
EXM Exam
PEX Past Exam
FAC Course Fact
QST Question
RES Resource
REV Review
CLU Cluster
```
상태: **확정**

## D-010 — Pattern은 V1 Core Type 아님
충분한 근거가 쌓이면 L9에서 승격하는 파생 지식 영역.  
상태: **현재 확정안**

## D-011 — 외부 transcription
V1에서 녹음→text 변환은 Study Brain 필수 기능이 아니다. 전체 전사본부터 ingest한다.  
상태: **확정**

## D-012 — Resource/Lecture N:N
한 Resource를 여러 Lecture에서 페이지 범위별로 사용한다.  
상태: **확정**

## D-013 — Concept는 cross-course
Concept를 Course별로 복제하지 않는다.  
상태: **확정**

## D-014 — Raw Source 보존
Transcript 등 text source는 구조화 전에 원문을 보존한다.  
상태: **확정**

## D-015 — 교수 발언/AI 해석 분리
AI 해석을 교수의 명시적 발언처럼 기록하지 않는다.  
상태: **확정**

## D-016 — 애매한 날짜 추측 금지
`다음 주`, `다음 수업` 등을 임의의 YYYY-MM-DD로 변환하지 않는다.  
상태: **확정**

## D-017 — Fact conflict 안전 우선
명시적 변경은 supersede 가능, 애매한 충돌은 사용자 확인.  
상태: **확정**

## D-018 — Human Section 보호
`My Notes`, `My Understanding`, `My Questions`, `Personal Reflection`은 자동 수정하지 않는다.  
상태: **확정**

## D-019 — SECOND-BRAIN.md 중심
핵심 운영 로직은 한곳에 두고 AGENTS/CLAUDE/Skills에서 중복하지 않는다.  
상태: **확정**

## D-020 — 구현 순서
```text
Architecture
→ Schema
→ SECOND-BRAIN
→ Workflows
→ Templates
→ Skills
→ Hooks
→ Obsidian UX
→ Tests
→ GitHub Template
→ Private Brain
→ Migration
```
상태: **확정**

## D-021 — 학기·과목 중심 저장 구조
구조화 노트와 원본의 물리적 저장 위치를 타입별 폴더에서 학기 → 과목 폴더 중심으로 바꾼다. CRS/LEC/RES/ASM/EXM/PEX/FAC/QST/REV 등의 ID와 frontmatter 관계 체계는 그대로 두고 저장 위치만 바꾼다. `wiki/`는 과목을 넘는 지식이므로 전역으로 유지한다. D-008의 정보 계층은 유지한다.
```text
study/
  <term>/
    <course-slug>/
      course.md
      lectures/
      resources/
      assignments/
      exams/
      past-exams/
      course-facts/
      questions/
      reviews/

raw/
  <term>/
    <course-slug>/
      resources/
      transcripts/
      assignments/
      past-exams/
      notices/

wiki/
  concepts/
  clusters/
  patterns/
```
`source` 경로와 내부 링크는 새 구조에서도 깨지지 않아야 한다.  
상태: **확정**

## D-022 — term 표기와 필수화
- 표기는 `YYYY-1`, `YYYY-2`, `YYYY-summer`, `YYYY-winter`다. 예: `2026-1`, `2026-2`, `2026-summer`, `2026-winter`
- CRS를 만들 때 term은 필수다.
- term 또는 course가 확정되지 않은 입력은 `inbox/`에 남긴다.

상태: **확정**

## D-023 — course-slug
- 과목을 처음 만들 때 정하는 영문 kebab-case의 안정적인 식별자다. 예: `computer-network`
- 폴더와 관련 ID에서 같은 slug를 사용하며 이후 임의로 변경하지 않는다.
- 새 frontmatter 필드는 추가하지 않는다.
- 분반은 일반적으로 slug에 넣지 않는다. 같은 학기에 같은 과목을 여러 분반으로 실제 관리해야 하는 경우에만 처음 생성할 때 `computer-network-01` 같은 고유 slug를 사용한다.
- 같은 과목을 다른 학기에 다시 수강하면 같은 slug를 재사용한다. 학기 폴더와 ID의 term·날짜 부분으로 구분한다.
- slug를 담지 않은 기존 ID도 형식 계약을 지키면 유효하다. 이때 slug의 기준은 폴더다.

상태: **확정**

## D-024 — course-scoped 노트는 실제 CRS에 연결
- `study/`의 course-scoped 구조화 노트에서는 `course: null`을 사용하지 않는다.
- RES, PEX, QST, REV도 `study/`에 들어가려면 실제 CRS에 연결되어야 한다.
- 과목이 미확정이면 `inbox/`에 남긴다.
- 과목을 초월한 지식은 `wiki/`가 담당한다.
- 여러 과목에 걸친 복습(REV)은 주 과목 CRS에 두고 나머지 과목은 `related`로 연결한다.
- 과목을 특정할 수 없는 질문(QST)은 만들지 않고 사용자에게 과목을 확인한다.

상태: **확정**

## D-025 — Past Exam 저장 위치
- 기출은 시험이 시행된 과거 학기 폴더가 아니라, 현재 이 기출을 사용하는 CRS의 학기·과목 폴더 아래에 저장한다.
- 실제 시험 연도·학기는 PEX metadata로 보존한다. 새 필드를 추가하지 않고 `year` 필드, ID의 학기 부분, 본문 출처 절에 기록한다.
- 이미 등록된 기출을 다른 CRS가 다시 사용하면 D-026과 같은 방식으로 처음 등록된 CRS 폴더에 두고 `related`로 재사용한다.

상태: **확정**

## D-026 — 공유 Resource의 canonical home
- 자료를 과목마다 복제하지 않는다.
- 처음 등록된 course를 canonical home으로 두고 한 번만 저장한다.
- 다른 course에서는 `related` 관계로 재사용한다.
- 중복 검사는 항상 `study/` 전체에서 수행한다.

상태: **확정**

## D-027 — raw/documents 폐지
- `raw/documents/`를 폐지한다.
- 일반 문서와 강의자료는 `resources/`, 공지는 `notices/`, 과제 원본은 `assignments/`로 분류한다.

상태: **확정**

## D-028 — 표준 입력 형식
- PPT/PPTX/HWP/DOCX/이미지(JPG/JPEG/PNG 등)는 현재 표준 ingest 대상으로 받지 않는다.
- 이런 입력이 `inbox/`에 들어오면 파일을 이동하거나 변환하지 않고 사용자에게 PDF 변환을 요청한다. PDF로 변환된 뒤 다시 ingest한다.
- PDF는 원본 그대로 보존한다.
- transcript의 표준 입력은 Markdown(`.md`)이며 `raw/<term>/<course-slug>/transcripts/`에 보존한다.
- txt/srt/vtt는 자동 변환하지 않는다.
- 사용자가 채팅에 직접 붙여넣은 transcript 텍스트는 원문을 그대로 Markdown(`.md`)으로 저장하는 것을 허용한다.
- Obsidian의 Detect all file extensions 설정에 의존하지 않는다.
- 이미지 직접 ingest가 필요해지면 별도 설계 결정으로 추가한다.

상태: **확정**

## D-029 — course 재배정은 migration
- 이미 구조화된 항목의 course 재배정은 예외적인 migration으로 처리한다.
- 사용자의 명시적 요청과 conflict check 후에만 수행한다.
- raw 원본과 노트를 함께 이동하고, `source`와 관련 링크를 같은 변경에서 갱신한다.
- 기존 ID는 변경하지 않는다.

상태: **확정**

## D-030 — CRS 파일명
- 과목의 CRS 노트 파일명은 `course.md`다.
- Obsidian Bases에서 `note.title`과 `file.folder`를 표시해 구분한다.
- Quick Switcher 파일명 정책 변경은 이번 리팩터링 범위에 넣지 않는다.

상태: **확정**

## D-031 — 동적 폴더에 README를 두지 않음
- 동적 `<term>/<course-slug>/<kind>` 폴더에는 README를 만들지 않는다.
- `study/README.md`와 `raw/README.md`가 구조 설명을 담당한다.
- `.gitkeep`과 `.gitattributes`는 추가하지 않는다.
- D-007의 "빈 폴더는 의미 있는 README로 유지한다"를 동적 폴더에 한해 개정한다.

상태: **확정**

## 보류 사항
- PDF/PPT를 Private Brain Git에 직접 넣을지 — **해소(D-028)**: PDF는 원본 그대로 보존하고, PPT/PPTX는 표준 입력으로 받지 않는다. Git LFS 도입 시점은 아래 항목으로 계속 보류한다.
- Git LFS 도입 시점
- binary source naming
- exact ID generator algorithm
- nested relation 허용 범위
- Pattern 정식 schema/type 승격 여부
- Obsidian Bases 기본 포함 범위
- 모바일 Git workflow
