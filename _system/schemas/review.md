# Review Schema

REV 노트는 복습 계획 또는 실제 복습 한 회차와 관찰된 학습 결과를 기록한다. 저장 위치는 `study/reviews/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: review
id: REV-20260908-01
title: 물리학 주간 복습
status: planned
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: null
review_type: weekly
targets: []
scheduled_on: null
completed_on: null
next_review: null
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `review`, id는 `REV-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `course` | 예 | 주 관련 CRS ID. 여러 과목 공용이면 null |
| `review_type` | 예 | daily, weekly, exam, concept, custom |
| `targets` | 예 | 복습 대상 LEC·CON·EXM·PEX·QST 등 ID 목록 |
| `scheduled_on` | 예 | 복습 예정일 YYYY-MM-DD 또는 null |
| `completed_on` | 예 | 실제 완료일 YYYY-MM-DD 또는 null. 완료 이력이 있으면 archived로 전환해도 유지한다 |
| `next_review` | 예 | 다음 복습 예정일 YYYY-MM-DD 또는 null |

## Status

- planned: 예정
- in-progress: 복습 중
- completed: 실제 수행과 결과 기록 완료
- skipped: 수행하지 않음
- archived: 보존용. 완료 이력이 있으면 completed_on과 결과 기록을 그대로 유지한다

## Body Structure

```markdown
## 복습 목표 / 대상

## Recall

## Understanding

## Application

## 응답 / 관찰 결과

## 오개념 / 미해결 질문

## 다음 행동

## Personal Reflection

<!-- AI-PROTECTED -->
```

## Rules

- 질문 목록을 생성한 것만으로 completed로 바꾸지 않는다. 실제 수행 근거와 completed_on이 필요하다.
- completed_on은 실제 복습을 완료했을 때만 기록한다. completed에서 archived로 전환하는 것은 보관이므로 completed_on을 지우지 않는다.
- 완료한 복습을 다시 수행하려고 재개하는 경우에만 status를 in-progress로 되돌리고 completed_on을 null로 비운다. 이전 완료일과 결과는 본문에 남긴다. 보관과 재개를 구분한다.
- 실제 복습을 시작할 때 targets는 하나 이상이어야 한다. 계획 초안에서는 []를 허용한다.
- 점수·숙련도·이해도를 응답 없이 추정하지 않는다. 미응답 문항은 미평가로 표시한다.
- next_review는 계획 데이터이며 알림 자동화를 생성했다는 뜻이 아니다.
- 같은 회차의 재처리는 기존 REV를 갱신하고, 다른 날짜의 실제 복습 회차는 별도 REV로 기록한다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

새 ID는 REV-YYYYMMDD-NN 형식으로 만들며 날짜는 노트 생성일이다. 저장소 전체에서 동일 Prefix·날짜의 번호 충돌을 확인한다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID를 유지한다.
