---
name: review
description: 복습 회차 하나를 계획하고 수행하고 기록한다 (복습 만들어줘). Use when the user wants a daily, weekly, exam-prep, or concept review — decides whether this is a new session or a continuation before writing anything, generates questions marked as AI-generated, records only actual answers, and never marks a session complete just because questions were produced. Triggers include 복습, 시험 대비, review, "이번 주 복습 만들어줘", and study-session requests.
---

# review

## Purpose

L7의 진입점. 복습 회차 **하나**를 계획하고 수행하고 기록한다. 지식이 아니라 학습 상태를 남긴다.

## When to use

사용자가 복습을 요청하거나 기존 회차를 이어갈 때.

## Required reading

1. [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) — 처음부터 끝까지
2. [`l7-review.md`](../../../_system/workflows/l7-review.md)
3. [`review.md`](../../../_system/schemas/review.md) — **`review_type` 허용 값은 여기서 읽는다.** 새 노트를 만들면 [`_system/templates/review.md`](../../../_system/templates/review.md)
4. 질문을 다루면 [`question.md`](../../../_system/schemas/question.md)

## Inputs

`$ARGUMENTS` — 복습 요청(유형·과목·범위) 또는 이어갈 기존 REV. 비어 있으면 묻는다.

## Execution

1. `SECOND-BRAIN.md`를 읽는다.
2. `l7-review.md`를 읽고 그 체크리스트를 수행한다.
3. **회차 판정을 가장 먼저 한다.** 신규인지 이어하기인지 재개인지 확정한다. 어느 쪽인지 불명확하면 **새 REV를 만들지도, 기존 REV를 되돌리지도 않고** 회차만 확인 요청한다.
4. `review_type`은 `review.md`가 정한 값에서 고른다. 이 문서에 값을 베껴 두지 않는다.
5. 질문 해결 처리는 종류에 따라 다르다. `conceptual` 계열은 사용자 확인으로 해결하지만, `source-verification`은 확인 가능한 근거가 있어야 해결한다.

## Completion / reporting

`l7-review.md`의 완료 보고 형식을 쓴다. 회차 판정 결과, 생성 문항 수, 사용자 응답 수, 미평가 항목, QST 처리 내역, `next_review`를 밝힌다.

## Do not

- **질문을 만든 것만으로 완료 처리하지 않는다.** 실제 수행 근거와 `completed_on`이 있어야 한다.
- 응답이 없는 항목에 점수나 이해도를 추정해 넣지 않는다. 미평가로 표시한다.
- 같은 요청을 다시 받았다는 이유로 새 회차를 만들지 않는다.
- 완료된 REV를 `archived`로 바꿀 때 `completed_on`과 결과를 지우지 않는다.
- LEC·CON의 내용을 고치지 않는다.
- `## Personal Reflection`을 쓰거나 고치지 않는다.
- 과거 기출 빈도를 근거로 "이번 시험에 나온다"라고 쓰지 않는다.
- `next_review`를 적었다고 알림이 설정됐다고 말하지 않는다. 계획값이다.

## Example

> 이번 주 일반물리학2 복습 만들어줘.

<!-- study-brain-template -->
