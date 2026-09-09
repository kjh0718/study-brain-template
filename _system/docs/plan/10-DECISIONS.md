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
기존 DEVSTUDY는 migration 검증 전까지 백업 가능하지만 새 구조의 핵심 의존성은 아니다.  
상태: **확정**

## D-005 — Git LFS V1 강제 안 함
PDF/PPT/이미지 사용량을 본 뒤 필요하면 도입한다.  
상태: **확정**

## D-006 — 최소 .gitignore
과도한 ignore 정책을 Template이 강제하지 않는다.  
상태: **확정**

## D-007 — .gitkeep 사용 안 함
빈 폴더는 의미 있는 README로 유지한다.  
상태: **확정**

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

## 보류 사항
- PDF/PPT를 Private Brain Git에 직접 넣을지
- Git LFS 도입 시점
- binary source naming
- exact ID generator algorithm
- nested relation 허용 범위
- Pattern 정식 schema/type 승격 여부
- Obsidian Bases 기본 포함 범위
- 모바일 Git workflow
