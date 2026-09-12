---
name: recall
description: 저장된 학습 지식을 근거 ID와 함께 다시 꺼낸다 (찾아줘). Use when the user asks what is known about a concept, course, exam scope, or deadline — answers from structured notes first and expands to raw transcripts only when the user asks for the professor's exact words or the evidence behind a date. Read-only, never writes. Triggers include 찾아줘, 정리해줘, recall, "교수님이 뭐라고 했어", "근거가 뭐야", and context requests before studying.
---

# recall

## Purpose

L6 Recall의 진입점. 저장된 지식을 근거와 함께 답한다. **읽기 전용이다.**

## When to use

사용자가 무엇을 아는지 묻거나 공부 전 맥락이 필요할 때. 수정 요청은 이 Skill이 아니다.

## Required reading

1. [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) — 처음부터 끝까지
2. [`l6-recall.md`](../../../_system/workflows/l6-recall.md)
3. [`README.md`](../../../_system/workflows/README.md)의 공통 검색 명령

## Inputs

`$ARGUMENTS` — 질문 또는 검색 요청. 비어 있으면 묻는다.

## Execution

1. `SECOND-BRAIN.md`를 읽는다.
2. `l6-recall.md`를 읽고 그 절차를 그대로 수행한다.
3. **일반 Recall과 Evidence Recall을 구분한다.** 원본 확장 조건은 `l6-recall.md`가 정한다. 사용자가 정확한 인용·날짜 근거·원문 확인을 요구하지 않으면 구조화 노트에서 끝낸다.
4. 답변의 각 진술에 근거 노트 ID를 붙인다.

## Completion / reporting

`l6-recall.md`의 답변 형식을 쓴다. 답변, 근거, 확인하지 못한 것, 읽은 범위를 구분해 적는다. Evidence Recall이면 원문 위치와 인용을 함께 낸다.

## Do not

- **노트를 만들거나 고치지 않는다. 로그도 쓰지 않는다.** 오류를 발견해도 보고만 한다.
- 매 질문마다 `raw/` 전체를 읽지 않는다. frontmatter로 먼저 좁힌다.
- 근거 없이 답하지 않는다. 없으면 없다고 답한다.
- 상충하는 사실 중 한쪽을 임의로 고르지 않는다. 양쪽을 보여주고 처리 레이어를 제안만 한다.
- AI 해석을 교수 발언처럼 인용하지 않는다.

## Example

> 운동량을 지금까지 어떻게 배웠는지 정리해줘.

구조화 노트만으로 답한다. 반면 "교수님이 과제 마감을 정확히 뭐라고 했어?"는 Evidence Recall이므로 `sources`를 따라 원문까지 연다.

<!-- study-brain-template -->
