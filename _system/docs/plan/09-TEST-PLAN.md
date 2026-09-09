# 09. Test Plan

## 테스트 목적
예쁜 문서 생성보다 **안전하게 지식을 누적하고 다시 꺼낼 수 있는가**를 검증한다.

## L1 Lecture 테스트
입력:
- 60~90분 수업 전사
- 교수 강조
- 과제 언급
- 시험 언급
- 애매한 날짜
- PPT 페이지 언급
- 학생 질문

기대:
- Raw 원문 보존
- Lecture 생성
- 교수 발언/AI 해석 분리
- Assignment 생성
- 애매한 due는 null
- EXM 업데이트
- Course Fact 생성
- Question 생성
- Resource pages 연결
- Review Question 생성
- log append

## Resource N:N 테스트
하나의 PDF를 4개 Lecture에서 사용.

기대:
```text
RES 1개
→ Lecture 4개
→ 각각 다른 page range
```

동일 PDF를 RES 4개로 중복 생성하면 실패.

## Concept 중복 테스트
`momentum`, `운동량`, `linear momentum` 표현을 섞는다.

기대:
- 기존 Concept 검색
- 의미상 동일하면 하나로 연결
- 유사 topic slug 중복 방지

## Assignment 날짜 테스트
교수 발언:
```text
다음 주까지 제출하세요.
```

기대:
```yaml
due: null
due_status: needs-review
```

임의 날짜 생성은 실패.

## Course Fact Conflict 테스트
기존: 시험 10/15  
신규: 시험은 10/17로 변경

기대:
- 기존 FAC superseded
- 신규 FAC active
- chain 연결

애매한 충돌에서는 자동 supersede 금지.

## Past Exam 테스트
과거 3개 시험에 같은 Topic 반복.

기대:
- 반복성 기록
- Pattern 후보 가능
- 현재 시험 출제 확정 금지

## Protected Section 테스트
`## My Notes` 내용이 ingest/review/maintain 재실행 후에도 변하지 않아야 한다.

## Evidence Recall 테스트
질문:
> 교수님이 과제 마감일을 정확히 뭐라고 했어?

기대:
- structured note만으로 확정하지 않음
- 관련 raw transcript 검색
- 원문 근거 제시

## Integrity 테스트
의도적으로 다음 오류를 만든다.
- invalid YAML
- 없는 ID reference
- duplicate topic
- orphan Note
- invalid status
- 끊어진 supersede chain

maintain이 탐지해야 한다.

## Git 동기화 테스트
Desktop:
```text
note A → commit → push
```

Laptop:
```text
pull → A 확인 → note B → commit → push
```

Desktop:
```text
pull → B 확인
```

## V1 완료 기준
- L1/L2/L3 정상
- conflict test 정상
- protected section 정상
- evidence recall 정상
- duplicate concept/topic 억제
- Desktop/Laptop Git sync 정상
