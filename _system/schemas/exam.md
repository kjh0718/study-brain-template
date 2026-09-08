# Exam Schema

EXM 노트는 현재 과목의 시험 한 회차에 대한 일정·범위·교수 언급을 누적한다. 저장 위치는 `study/exams/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: exam
id: EXM-20260908-01
title: 일반물리학 중간고사
status: planned
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: CRS-20260908-01
exam_type: midterm
date: null
date_status: unknown
scope_status: unknown
sources: []
concepts: []
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `exam`, id는 `EXM-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `course` | 예 | 소속 CRS ID |
| `exam_type` | 예 | midterm, final, quiz, practical, other |
| `date` | 예 | 확인된 날짜 또는 시간대 포함 일시 문자열. 미확인이면 null |
| `date_status` | 예 | unknown, needs-review, confirmed |
| `scope_status` | 예 | unknown, needs-review, confirmed |
| `sources` | 예 | 근거 LEC·RES·FAC ID 목록 |
| `concepts` | 예 | 시험과 연결된 CON ID 목록 |

## Status

- planned: 예정
- completed: 시험 실시 확인
- cancelled: 취소 확인
- archived: 보존용

## Body Structure

```markdown
## 일정 / 장소

## 확정 범위

## 교수님 시험 언급

## AI 예상 / 검증 필요

## 준비 체크리스트

## 관련 기출

## Sources

## My Notes

<!-- AI-PROTECTED -->
```

## Rules

- course, exam_type와 회차를 함께 확인한다. quiz 여러 회를 하나로 합치지 않는다. 회차 표기는 본문과 제목에 둔다.
- 여러 강의에서 같은 중간고사를 언급하면 기존 EXM에 근거를 누적한다.
- confirmed 상태는 확인 가능한 근거가 있어야 한다. scope_status는 확정 범위 섹션에만 적용되고 AI 예상에는 적용되지 않는다.
- 교수 강조·기출 빈도·AI 예측을 확정 출제 내용과 구분한다.
- 날짜가 지났다는 이유만으로 completed로 변경하지 않는다.
- FAC에 기록한 일정 변경은 같은 근거로 EXM도 갱신한다. 두 노트가 다르면 충돌로 표시하고 임의의 최신값을 선택하지 않는다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

새 ID는 EXM-YYYYMMDD-NN 형식으로 만들며 날짜는 노트 생성일이다. 저장소 전체에서 동일 Prefix·날짜의 번호 충돌을 확인한다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID를 유지한다.
