# Assignment Schema

ASM 노트는 과목의 과제 한 건과 요구사항·마감·제출 상태를 관리한다. 저장 위치는 `study/assignments/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: assignment
id: ASM-20260908-01
title: 물리학 HW03
status: open
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: CRS-20260908-01
assigned: null
due: null
due_status: needs-review
submission_method: "LMS"
sources: []
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `assignment`, id는 `ASM-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `course` | 예 | 소속 CRS ID |
| `assigned` | 예 | 확인된 부여일 YYYY-MM-DD 또는 null |
| `due` | 예 | 확인된 마감 날짜 또는 시간대가 포함된 일시 문자열. 미확인이면 null |
| `due_status` | 예 | unknown, needs-review, confirmed 중 하나 |
| `submission_method` | 아니오 | 확인된 제출 방식 문자열. 모르면 생략 |
| `sources` | 예 | 과제 근거 LEC·RES·FAC ID 목록 |

## Status

- open: 착수 전
- in-progress: 수행 중
- submitted: 제출 사실 확인
- completed: 필요한 후속 처리까지 완료
- cancelled: 취소 확인
- archived: 보존용

## Body Structure

```markdown
## 요구사항

## 마감 / 원문 표현

## 제출 방법

## 진행 체크리스트

## 제출 기록

## Sources

## 검증 필요

## My Notes

<!-- AI-PROTECTED -->
```

## Rules

- 같은 course와 과제 번호·요구사항을 확인해 중복을 방지한다. 새 공지는 기존 과제의 근거에 누적한다.
- '다음 주까지'처럼 기준이 불명확하면 due: null, due_status: needs-review와 원문을 남긴다. 마감 언급 자체가 없으면 unknown이다.
- confirmed는 due가 있고 이를 뒷받침하는 근거가 있을 때만 사용한다. 날짜만 알면 날짜만 기록하며 시간을 임의로 넣지 않는다.
- submitted는 실제 제출 증거 또는 사용자 확인이 있을 때만 설정한다. 체크리스트 완료를 제출로 간주하지 않는다.
- 과제 초안을 작성하는 권한과 LMS에 제출하는 권한은 별개다. 이 스키마는 제출 실행 권한을 부여하지 않는다.
- 상충하는 마감은 양쪽 근거를 보존한다. 해결 전 due_status를 needs-review로 두고 기존 값이 확정값처럼 보이지 않게 표시한다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

새 ID는 ASM-YYYYMMDD-NN 형식으로 만들며 날짜는 노트 생성일이다. 저장소 전체에서 동일 Prefix·날짜의 번호 충돌을 확인한다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID를 유지한다.
