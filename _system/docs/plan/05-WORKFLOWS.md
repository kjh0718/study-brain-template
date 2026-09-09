# 05. Workflows

Study Brain의 핵심 워크플로는 L1~L9로 설계한다.

## L1 — Lecture Ingestion
목적: 전체 강의 전사를 안전하게 구조화.

입력:
- Course
- 전체 전사본
- 날짜
- 주차(선택)
- 사용 Resource(선택)

절차:
```text
Course 식별
→ Lecture ID 생성
→ Raw transcript 보존
→ Lecture 구조화
→ Professor Emphasis 추출
→ Concept 후보 처리
→ Assignment 추출
→ Exam 업데이트
→ Course Fact 추출
→ Question 추출
→ Resource 연결
→ Past Exam 관련성 연결
→ Review Question 생성
→ Course Dashboard 업데이트
→ Cluster incremental update
→ Log
```

분류 카테고리:
- Lecture Content
- Professor Emphasis
- Concept
- Assignment
- Exam
- Course Fact
- Question
- Resource Reference
- Next Lecture / Notice

완료 보고 예:
```text
Lecture ingest 완료
- Lecture: LEC-...
- Raw source: saved
- Existing concepts linked: 4
- New concepts: 1
- Assignment: 1 (deadline needs review)
- Exam updates: 1
- Course facts: 2
- Questions: 3
- Resource: RES-... pages 21-38
- Past exam links: 2
- Review questions: 5
- Conflict: none
```

## L2 — Resource Ingestion
목적: PPT/PDF/교재/프린트/논문 등을 한 번만 등록하고 여러 Lecture에서 재사용.

```text
중복 Resource 검색
→ 기존이면 재사용
→ 신규면 RES 생성
→ resource_type 식별
→ authority 확인
→ Raw source/참조 보존
→ 자료 구조/목차 분석
→ Concept 후보 연결
→ Course 연결
→ 기존 Lecture 연결 가능 시 연결
→ Exam/Assignment 관련 근거 분리
→ Cluster 업데이트
→ Log
```

Resource 강조 표시만으로 시험 출제를 확정하지 않는다.

## L3 — Past Exam Ingestion
```text
Raw PEX 보존
→ 연도/학기/시험종류/교수 식별
→ 문제 단위 분석
→ Concept/Topic 매핑
→ 문제 유형/난이도
→ 답안 검증 상태
→ 현재 Lecture/Concept/EXM 연결
→ 반복 패턴 후보
→ Log
```

과거 출제 빈도는 현재 시험 출제 확정이 아니다.

## L4 — Knowledge Extraction
```text
candidate
→ 기존 Concept 검색
→ 의미상 동일하면 link/update
→ 신규 가치 평가
→ 충분한 경우만 CON 생성
→ 아니면 원 Note 내부에 유지
```

신규 Concept 승격 기준:
- 재사용성
- 반복성
- 핵심성
- 시험 중요도
- 이해 난이도
- 연결성

## L5 — Fact & Conflict Reconciliation
```text
새 주장
→ 기존 Fact 검색
→ 동일: source 추가
→ 명시적 변경: supersede
→ 애매한 충돌: stop / ask
→ log
```

## L6 — Recall
기본 검색 순서:
```text
Frontmatter
→ ID/type/course/topic filter
→ title/body
→ final candidates full read
```

원문 근거가 필요할 때만 Evidence Recall로 Raw 확장.

## L7 — Review
유형:
- daily
- weekly
- exam-prep
- concept

Exam Prep 입력:
```text
Lecture
+ Professor Emphasis
+ Exam
+ Concept
+ Past Exam
+ Assignment
+ Open Question
```

출력:
- 범위 핵심
- 교수 강조
- 암기/이해 구분
- 미해결 질문
- 반복 족보 유형
- 주의할 오개념
- Practice/Recall Questions

## L8 — Maintenance & Integrity
검사:
- invalid YAML
- broken ID/reference
- duplicate Concept
- duplicate Topic slug
- stale Course Fact
- supersede chain 오류
- orphan Note
- missing source
- invalid status
- Course dashboard 불일치

기본적으로 임의 재작성보다 무결성 검사와 안전한 정리를 우선한다.

## L9 — Knowledge Promotion / Merge
```text
Lecture 여러 개
+ Resource 여러 개
+ PEX 여러 개
→ Concept 강화
→ Cluster 연결
→ 충분한 증거가 있으면 Pattern 생성
```

Semantic duplicate Concept가 발견되면 자동 병합보다 merge 후보 제시를 우선한다.

## Daily Interface
세 개의 기본 동사를 유지한다.

- `capture`: 새 입력 분류 후 적절한 ingest workflow로 전달
- `recall`: 관련 지식을 구조적으로 검색
- `maintain`: 무결성/중복/링크/상태 검사
