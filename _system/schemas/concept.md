# Concept Schema

CON 노트는 과목을 넘어 재사용할 수 있는 하나의 개념을 정의한다. 저장 위치는 `wiki/concepts/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: concept
id: CON-20260908-01
title: 운동량
status: draft
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
aliases: []
sources: []
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `concept`, id는 `CON-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `aliases` | 예 | 대체 명칭 문자열 목록. 없으면 [] |
| `sources` | 예 | 근거가 되는 LEC·RES·PEX 등 구조화 노트 ID 목록 |

## Status

- draft: 정리 중
- needs-review: 근거 또는 설명 검토 필요
- active: 사용 가능한 설명
- archived: 보존용

## Body Structure

```markdown
## 정의

## 직관

## 공식 / 적용 조건

## 예제

## 흔한 오해

## 연결 개념

## Sources

## 검증 필요

## My Understanding

<!-- AI-PROTECTED -->
```

## Rules

- 새 노트 전에 title, aliases와 본문 의미를 검색한다. 같은 개념이면 기존 노트를 보강한다.
- 단순 용어 출현만으로 독립 노트를 생성하지 않는다. 반복 사용, 핵심성, 독립 설명 가치 중 근거를 기록한다.
- sources와 Sources 본문의 직접 원본 근거가 모두 비어 있으면 draft 또는 needs-review로 둔다. AI 설명 자체를 외부 근거처럼 취급하지 않는다.
- 같은 이름이라도 분야별 의미가 다르면 제목과 정의에서 범위를 구분한다.
- 공식에는 기호·단위·적용 조건을 함께 기록한다. 수업 운영 사실은 FAC로 분리한다.
- related는 다른 CON 등 의미상 연결이다. sources에 있는 ID를 반복하지 않는다. 병합 시 참조와 사용자 필기를 보존하고 원래 ID를 무단 재사용하지 않는다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

권장 형태는 `CON-<개념 slug>`다. 예: `CON-momentum`. 개념은 과목·날짜에 종속되지 않으므로 날짜를 넣지 않는다. 같은 개념을 여러 기기에서 만들어도 같은 ID가 나오도록 대표 명칭 하나를 slug로 고정하고, 다른 표기는 `aliases`에 둔다.

형식 계약과 Type별 권장 형태는 [common.md](common.md)의 `id` 절이 정본이다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID는 유지하며, 권장 형태로 바꾸려고 기존 ID를 재발급하지 않는다.
