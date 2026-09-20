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
하나의 PDF를 4개 Lecture에서 사용하고, 그중 두 Lecture는 두 번째 자료도 함께 사용한다.

기대:
```text
RES 슬라이드 → Lecture 4개, 각각 다른 page range (겹쳐도 정상)
RES 유인물   → Lecture 3개 (슬라이드와 Lecture 집합이 서로 포함되지 않는 교차 M:N)
Lecture 1개  → RES 2개 (자료마다 항목 하나)
```

- 동일 PDF를 RES 4개로 중복 생성하면 실패.
- 한 Lecture의 `resources`에 같은 RES가 두 항목으로 들어가면 실패. 떨어진 구간은 한 `pages` 문자열에 담는다.
- `pages` 생략은 범위 미확인이다. 자료 전체로 해석해 채우면 실패.
- 두 방향 모두 ID로 찾아 검사한다. 항목 순서에 의존하면 실패.

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

## P9 완료 기준

- core architecture regression 없음
- workflow integration A~K 통과
- Claude Code 실제 Skill runtime 검증
- 보호 영역 실제 agent 재실행 후 보존
- evidence/provenance 유지
- conflict 처리 검증
- duplicate Concept 처리 검증
- broken relative link 0
- fixture와 production 데이터 격리
- fixture만으로 재현 가능
- run_all 일괄 실행 가능
- Codex project Skill discovery + 실제 invocation 확인
- 문서 상태와 실제 구현 상태 일치

P8의 HOME·Bases·Knowledge Browser 결과는 회귀 확인의 참고 근거로만 사용하며 P9 acceptance criteria 자체로 재사용하지 않는다. fixture 재현에는 runtime workspace 생성과 실제 Skill 호출이 포함되며, `run_all.py`가 그 준비를 대신하지 않는다.

## 결정 기록 — Git 동기화 시험을 P11로 옮긴다 (2026-09-13)

위 V1 완료 기준의 마지막 항목 `Desktop/Laptop Git sync 정상`은 **P9 complete 조건에서 제외한다.** 기준 자체를 지우지 않고 수행 시점만 옮긴다.

- **어디로**: P11 Private Brain 직전 또는 초기 검증
- **왜**: 나머지 P9 항목은 이 저장소의 규칙·문서·Skill을 검증하지만, 이 항목은 **Git과 사용자 기기 두 대**를 검증한다. 템플릿 자체 테스트가 아니라 실제 2-device 사용자 환경 검증이다.
- **부수 이유**: 기기 2대가 없으면 재현할 수 없어, P9에 묶어 두면 기기가 생길 때까지 P9가 닫히지 않는다. 실제 비공개 Brain을 두 기기에서 쓰기 시작하는 시점이 이 시험의 자연스러운 자리다.
- Phase 번호를 새로 만들지 않았다.
