# Course Fact Schema

FAC 노트는 과목 운영의 근거 있는 사실 한 건을 기록하고 변경 이력을 보존한다. 저장 위치는 `study/course-facts/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: course-fact
id: FAC-20260908-01
title: 중간고사 일정 변경
status: needs-review
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: CRS-20260908-01
fact_type: schedule
subject: CRS-20260908-01
value: null
authority: unknown
sources: []
effective_from: 2026-09-08
supersedes: []
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `course-fact`, id는 `FAC-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `course` | 예 | 소속 CRS ID |
| `fact_type` | 예 | schedule, assessment, submission, attendance, location, material, policy, other |
| `subject` | 예 | 사실의 대상인 CRS·ASM·EXM 등 ID |
| `value` | 예 | 사실 내용 문자열. 미확인이면 null |
| `authority` | 예 | 공통 출처 분류값 |
| `sources` | 예 | 근거 LEC·RES 등 ID 목록 |
| `effective_from` | 아니오 | 확인된 적용 시작일 YYYY-MM-DD. 미확인이면 생략 |
| `supersedes` | 예 | 이 사실이 대체하는 이전 FAC ID 목록 |

## Status

- needs-review: 확인·충돌 해결 필요
- active: 현재 유효한 사실
- superseded: 후속 사실로 대체
- retracted: 근거와 함께 철회
- archived: 보존용

## Body Structure

```markdown
## 사실 / 적용 범위

## 근거 원문

## 이전 정보와의 비교

## 충돌 / 확인 필요

## 변경 이력

## Sources

## My Notes

<!-- AI-PROTECTED -->
```

## Rules

- fact_type만으로 중복 여부를 판단하지 않는다. course, subject, 세부 사실 항목과 적용 기간을 비교한다.
- active는 value와 근거가 확인됐을 때만 사용한다. 출처 분류만으로 유효성을 확정하지 않는다.
- 명시적 변경과 권한·적용 범위가 확인되면 새 FAC를 만들고 이전 FAC를 superseded로 변경한다. 새 FAC.supersedes에 이전 ID를 기록한다.
- 불명확한 상충은 두 근거를 남겨 needs-review로 둔다. 조용히 덮어쓰거나 최신 발언이라는 이유로 자동 승리시키지 않는다.
- supersedes는 자기 자신·순환 참조를 허용하지 않는다. 이전 사실과 원문을 삭제하지 않는다.
- subject가 EXM 또는 ASM이면 해당 일정·조건에도 같은 근거를 반영한다. 반복 복사된 설명을 독립적 확정 근거로 취급하지 않는다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

새 ID는 FAC-YYYYMMDD-NN 형식으로 만들며 날짜는 노트 생성일이다. 저장소 전체에서 동일 Prefix·날짜의 번호 충돌을 확인한다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID를 유지한다.
