# Past Exam Schema

PEX 노트는 과거 시험 원본 또는 복원 자료 한 묶음의 출처와 문제 분석을 관리한다. 저장 위치는 `study/past-exams/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: past-exam
id: PEX-20260908-01
title: 물리학 2024 중간고사 기출
status: needs-review
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: null
year: 2024
exam_type: midterm
source: raw/past-exams/physics-2024-midterm.pdf
authority: student-provided
provenance: reconstructed
concepts: []
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `past-exam`, id는 `PEX-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `course` | 예 | 연결 가능한 현재 CRS ID. 미연결이면 null |
| `year` | 예 | 확인된 시험 연도 정수 또는 null |
| `exam_type` | 예 | midterm, final, quiz, practical, other, unknown |
| `source` | 예 | raw/past-exams/ 원본 경로 또는 실제 외부 참조 |
| `authority` | 예 | 공통 출처 분류값 |
| `provenance` | 예 | official, reconstructed, unknown |
| `concepts` | 예 | 관련 CON ID 목록 |

## Status

- draft: 등록 중
- needs-review: 출처·문항·해설 확인 필요
- analyzed: 현재 자료 분석 완료
- archived: 보존용

## Body Structure

```markdown
## 자료 식별 / 출처

## 문항별 분석

## 제공된 정답 / 해설

## AI 풀이 / 검증 필요

## Concept 연결

## 출제 경향의 근거

## My Notes

<!-- AI-PROTECTED -->

## Source
```

## Rules

- 원본 시험과 학생 복원본을 provenance로 구분한다. 과거 강사·과목명은 확인된 범위만 본문에 기록한다.
- 같은 파일·시험의 재입력은 기존 노트를 사용한다. 부분 복원본과 다른 판본은 동일성 확인 후 연결한다.
- 각 문항은 원본 페이지·문항 번호를 남긴다. 번호가 없으면 로컬 식별 표기를 사용하고 원본 번호인 것처럼 표시하지 않는다.
- 원본 정답, 학생 해설, AI 풀이를 분리한다. analyzed는 공식 정답 검증 완료라는 뜻이 아니다.
- 기출 한 번으로 보편적 패턴이나 다음 시험 출제를 확정하지 않는다. 표본 수와 출처 범위를 기록한다.
- 별도의 새로운 Core Type을 만들지 않는다. 반복 패턴 승격은 L9의 근거 검토 대상으로 둔다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

권장 형태는 `PEX-<과목 slug>-<연도>-<학기>-<exam_type>`이다. 예: `PEX-general-physics-2-2024-2-midterm`. 회차가 ID를 특정하므로 등록일을 넣지 않는다. 같은 회차의 다른 판본이 별도 자료로 확인되면 뒤에 구분자를 덧붙인다. 예: `...-midterm-b`. 어느 회차인지 확인할 수 없으면 PEX를 만들지 않고 보류한다.

형식 계약과 Type별 권장 형태는 [common.md](common.md)의 `id` 절이 정본이다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID는 유지하며, 권장 형태로 바꾸려고 기존 ID를 재발급하지 않는다.
