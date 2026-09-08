# Course Schema

Course(`CRS`)는 하나의 수업·과목·학습 단위를 설명하는 구조화 노트다. 강의별 내용은 `lecture`, 과제는 `assignment`, 시험은 `exam`으로 분리하고 이 노트에서는 과목 전체의 기준 정보와 연결 관계를 관리한다.

## Location

`study/courses/`

## Frontmatter

```yaml
---
schema: 1
type: course
id: CRS-20260908-01
title: 일반물리학 1
status: active
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
code: PHY101
term: 2026-2
instructor: 홍길동
---
```

## Required Fields

Course는 [Common Note Schema](./common.md)의 공통 필드를 모두 가진다.

| Field | Required | Description |
|---|---:|---|
| `schema` | yes | Schema version. 현재 `1`. |
| `type` | yes | 반드시 `course`. |
| `id` | yes | `CRS-` Prefix를 사용하는 영구 ID. |
| `title` | yes | 과목명. |
| `status` | yes | `planned`, `active`, `completed`, `archived` 중 하나. |
| `topics` | yes | 통제된 Topic ID 목록. |
| `related` | yes | 관련 구조화 노트 ID 목록. |
| `created` | yes | 최초 생성일. |
| `updated` | yes | 마지막 수정일. |
| `code` | no | 과목 코드. 모르면 생략한다. |
| `term` | no | 수강 학기 또는 기간. 모르면 생략한다. |
| `instructor` | no | 담당 교수·강사. 모르면 생략한다. |

## Status Values

- `planned`: 수강 예정이지만 아직 진행하지 않음
- `active`: 현재 진행 중
- `completed`: 수강 또는 학습을 마침
- `archived`: 더 이상 적극적으로 사용하지 않지만 기록으로 보존

## Body Template

```markdown
## Overview

과목의 목적과 학습 범위를 짧게 기록한다.

## Schedule

- 기간:
- 수업 시간:
- 장소 또는 링크:

## Learning Goals

-

## Key Concepts

-

## Related Notes

- Lectures:
- Assignments:
- Exams:
- Course facts:

## Sources

-

## Open Questions

-

## My Notes

<!-- AI-PROTECTED -->
```

## Rules

- Course 노트에는 과목 전체에 적용되는 정보만 둔다.
- 특정 수업의 상세 내용은 `LEC` 노트로 분리한다.
- 일정·평가·제출 조건처럼 근거가 필요한 정보는 가능한 경우 원본 Source를 연결한다.
- `related`에는 실제로 존재하는 구조화 노트의 ID만 넣는다.
- 상태값을 임의로 확장하지 않는다.

## Course Identity and Dashboard

- Course는 특정 학기·분반의 수강 단위다. 같은 과목을 다른 학기나 분반에서 수강하면 별도 CRS로 구분한다.
- 새 CRS-YYYYMMDD-NN의 날짜는 생성일이다. 동일 Prefix·날짜의 번호는 저장소 전체에서 충돌을 확인한다.
- term과 code는 문자열이다. 같은 학기의 분반·담당자·기관 구분은 본문에 확인된 범위로 남긴다.
- Dashboard에는 관련 노트 링크와 짧은 상태만 표시한다. 과제 마감, 시험 범위와 교수 발언의 정식 근거를 복제해 별도 사실처럼 관리하지 않는다.
- 관련 노트는 course 필드로 찾아 Dashboard에 반영한다. 모든 하위 노트를 related에 반복 등록할 필요는 없다.
- 여러 과목이 공유하는 노트는 course에 주 과목만 들어가고 추가 과목은 related에 들어간다. Dashboard 조회는 course가 이 CRS인 노트와 related에 이 CRS를 포함한 노트를 함께 찾는다. 두 경우를 구분해 표시하고, 공유 노트를 과목마다 복제하지 않는다.
- 예시의 과목명·강사명은 실제 데이터가 아니다. 템플릿을 개인 Brain으로 사용할 때 확인된 값으로 교체한다.
- 본문의 My Notes는 사용자 영역이다. common.md의 Protected User Sections 규칙을 적용한다.
