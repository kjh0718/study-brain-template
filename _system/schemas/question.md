# Question Schema

QST 노트는 이해 또는 사실 확인이 필요한 독립 질문 하나와 해결 근거를 관리한다. 저장 위치는 `study/questions/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: question
id: QST-20260908-01
title: 운동량 보존 조건 확인
status: open
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: null
question_type: conceptual
sources: []
answer_sources: []
resolved_on: null
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `question`, id는 `QST-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `course` | 예 | 관련 CRS ID. 공용 질문이면 null |
| `question_type` | 예 | conceptual, clarification, source-verification, problem-solving, other |
| `sources` | 예 | 질문 발생 근거가 되는 구조화 노트 ID 목록 |
| `answer_sources` | 예 | 답변 근거가 되는 구조화 노트 ID 목록 |
| `resolved_on` | 예 | 해결 확인일 YYYY-MM-DD. 미해결이면 null |

## Status

- open: 미해결
- investigating: 확인 중
- answered: 답변 후보 있음
- resolved: 근거와 해결 확인
- archived: 보존용

## Body Structure

```markdown
## 질문

## 발생 맥락

## 시도한 이해 / 풀이

## 답변 후보

## 해결 근거

## 남은 확인

## My Questions

<!-- AI-PROTECTED -->
```

## Rules

- 동일 의미와 맥락의 열린 질문을 먼저 검색한다. 표현이 다르다는 이유로 중복 생성하지 않는다.
- AI가 답변을 생성했다는 사실만으로 resolved로 바꾸지 않는다. 학습 질문은 사용자 이해 확인을, 사실 질문은 확인 가능한 근거를 기록한다.
- resolved는 resolved_on과 해결 근거가 있어야 한다. 외부 근거가 필요 없는 사용자 이해 확인은 본문에 확인 내용을 기록한다.
- 다시 의문이 생기면 open 또는 investigating으로 돌리고 resolved_on은 null로 둔다. 이전 답변과 해결 기록은 본문에 보존한다.
- My Questions 안의 질문을 별도 QST로 정리해 연결하더라도 원래 사용자 문장을 변경하지 않는다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

새 ID는 QST-YYYYMMDD-NN 형식으로 만들며 날짜는 노트 생성일이다. 저장소 전체에서 동일 Prefix·날짜의 번호 충돌을 확인한다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID를 유지한다.
