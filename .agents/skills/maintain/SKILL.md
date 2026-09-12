---
name: maintain
description: Study Brain의 무결성을 검사하고 승인된 범위만 정리한다 (정리해). Use when the user asks to audit or tidy the vault — checks required fields, status values, ID contract, relation integrity, bidirectional Lecture/Resource links, source paths, topic vocabulary, course dashboards, and supersede chains. Inspect-only by default; never fixes without an explicit scope. Triggers include 정리해, 검사해, 확인해줘, maintain, and vault audit requests.
---

# maintain

## Purpose

L8의 진입점. 검사와 수정을 분리한다. **기본은 검사 모드다.**

## When to use

사용자가 저장소를 점검하거나 정리해 달라고 할 때.

## Required reading

1. [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) — 처음부터 끝까지
2. [`l8-maintenance.md`](../../../_system/workflows/l8-maintenance.md)
3. 검사 대상 타입의 [`_system/schemas/`](../../../_system/schemas/README.md) — 허용 값은 스키마에서 읽는다

## Inputs

`$ARGUMENTS` — 검사 범위 또는 수정 대상. 비어 있으면 저장소 전체를 **검사 모드로** 수행한다.

## Execution

1. `SECOND-BRAIN.md`를 읽는다.
2. `l8-maintenance.md`를 읽는다.
3. **모드를 먼저 정한다.** "검사해줘"는 검사 모드, "정리해줘"는 수정 모드다. 판정 기준은 `l8-maintenance.md`가 정한다.
4. **수정 모드인데 대상 범위가 없으면 검사 모드로 수행하고** 수정 후보 목록을 낸다. 범위를 추정해 고치지 않는다.
5. 검사 항목 10개를 수행한다. 명령은 `l8-maintenance.md`에 있다.
6. 수정 모드면 `SECOND-BRAIN.md`의 안전 순서표에서 낮은 단계부터 고치고 로그를 남긴다.

## Completion / reporting

`l8-maintenance.md`의 보고 형식을 쓴다. 검사 모드는 파일·위치·항목·심각도를 담은 보고서만 내고 **로그를 쓰지 않는다.** 수정 모드는 수정한 항목과 남은 항목을 모두 보고한다.

## Do not

- **검사 모드에서 파일을 고치거나 로그를 쓰지 않는다.**
- 승인 범위를 추정해 고치지 않는다.
- 중복 노트를 자동 병합하지 않는다. 파일 삭제와 ID 회수를 하지 않는다.
- 없는 보호 영역을 자동으로 삽입하지 않는다.
- 상충하는 사실 중 한쪽을 골라 정리하지 않는다. L5로 넘긴다.
- 스키마에 없는 필드나 상태값을 만들어 무결성을 맞추지 않는다.
- 허용 상태값을 이 문서에 베껴 두지 않는다. 스키마에서 읽는다.

## Example

> 브레인 한번 확인해줘.

검사 모드다. 보고서만 낸다. 이어서 "1번이랑 4번 고쳐줘"라고 하면 그 둘만 수정 모드로 처리한다.

<!-- study-brain-template -->
