# 01. Project Vision

## 목적
`study-brain-template`은 대학 학습용 AI-native Second Brain 템플릿이다. 단순한 Obsidian 폴더가 아니라 다음을 함께 제공하는 **학습 지식 운영 시스템**을 목표로 한다.

- 수업 전사 원문 보존
- Lecture 단위 구조화
- 교수 강조사항 추출
- 과제/마감/시험 정보 자동 정리
- PPT/PDF/교재와 Lecture 연결
- 족보 분석과 현재 수업 연결
- Concept 재사용 및 중복 억제
- Course Dashboard 자동 갱신
- 질문/이해 공백 추적
- 일간/주간/시험 대비 Review
- 근거 기반 Recall
- 충돌하는 Course Fact의 안전한 변경 이력
- Git 기반 AI 변경 추적
- Claude/Codex/Gemini 등 여러 Agent가 같은 규칙을 따르는 구조

## 기본 사용 흐름
V1에서는 audio-to-text 자체를 Study Brain의 핵심 기능으로 두지 않는다.

```text
수업 녹음
→ CLOVA/Gemini/기타 transcription
→ 전체 전사본
→ Study Brain ingest
```

사용자는 예를 들어 다음처럼 요청한다.

> 이건 오늘 일반물리학2 전체 전사본이야. Study Brain에 넣어줘.

시스템은 다음을 수행한다.

```text
Raw transcript 보존
→ Course 식별
→ Lecture 생성
→ Summary / Core Content
→ Professor Emphasis
→ Concept 연결/후보
→ Assignment 추출
→ Exam 갱신
→ Course Fact 추출
→ Question 추출
→ Resource 연결
→ Past Exam 관련성 연결
→ Review Question 생성
→ Course Dashboard 갱신
→ Cluster 갱신
→ Log 기록
```

## 템플릿 정체성
기존 `second-brain-template`을 그대로 fork하지 않는다.

```text
기존 Project Second Brain의 강점
+ 공개 AI Second Brain의 좋은 설계
+ Study 전용 요구사항
= study-brain-template
```

가져올 핵심 원칙:
- 중앙 운영 규격
- frontmatter-first retrieval
- raw source 보존
- controlled topic vocabulary
- cluster/MOC
- conflict detection
- supersede history
- append-only log
- capture / recall / maintain
- untrusted input rule
- deterministic retrieval
- human confirmation policy

## 저장소 전략
최종적으로 저장소 두 개를 사용한다.

```text
study-brain-template
└─ 시스템/규칙/스키마/스킬/템플릿

my-second-brain (Private)
└─ 실제 수업/전사/과제/시험/개념/족보/복습
```

Template 완성 후 GitHub Template Repository로 만들고 실제 Private Brain을 생성한다.

## 성공 기준
V1 성공 조건:
1. 전체 전사본 하나를 안전하게 ingest한다.
2. Lecture/Assignment/Exam/Course Fact/Question을 분리한다.
3. 교수 발언과 AI 해석을 구분한다.
4. 기존 Concept를 우선 연결하고 Concept 폭증을 막는다.
5. Resource 하나가 여러 Lecture에서 페이지 범위별로 재사용된다.
6. Past Exam을 분석하되 현재 시험 출제를 임의로 확정하지 않는다.
7. 충돌하는 사실을 자동 덮어쓰지 않는다.
8. `My Notes` 등 사용자 작성 영역을 보호한다.
9. 모든 주요 write가 log에 기록된다.
10. Desktop/Laptop이 Git으로 동일한 Private Brain을 동기화한다.
