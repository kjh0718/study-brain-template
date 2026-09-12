---
name: ingest-resource
description: 학습 자료를 한 번만 등록해 여러 강의에서 재사용한다 (자료 등록). Use when the input is a slide deck, textbook chapter, handout, paper, or an external link — searches for an existing Resource by title, author, edition, and content before creating a new one, then links it to lectures with per-lecture page ranges. Triggers include PPT, PDF, 교재, 프린트, 강의자료, resource, and "이 자료 등록해줘".
---

# ingest-resource

## Purpose

L2의 진입점. 자료 하나를 **한 번만** 등록해 여러 강의에서 재사용한다.

## When to use

입력이 학습 자료일 때. [ingest-lecture](../ingest-lecture/SKILL.md)가 미등록 자료를 발견했을 때도 호출된다.

## Required reading

1. [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) — 처음부터 끝까지
2. [`l2-resource-ingestion.md`](../../../_system/workflows/l2-resource-ingestion.md)
3. [`resource.md`](../../../_system/schemas/resource.md), 새 노트를 만들면 [`_system/templates/resource.md`](../../../_system/templates/resource.md)

## Inputs

`$ARGUMENTS` — 자료 파일 경로 또는 접근 가능한 참조. L1이 넘긴 미등록 자료. 비어 있으면 묻는다.

## Execution

1. `SECOND-BRAIN.md`를 읽는다.
2. `l2-resource-ingestion.md`를 읽고 그 체크리스트를 수행한다.
3. **중복 검색을 먼저 한다.** 파일명만으로 판단하지 않고 제목·작성자·판·내용, 가능하면 파일 해시를 비교한다. 기존 RES가 있으면 갱신한다.
4. 부모 L1이 있는지 확인한다. 호출 방식이 달라진다.

   | 단계 | L1이 호출 | 단독 실행 |
   |---|---|---|
   | 개념 후보 | 부모에 반환 | L4 직접 호출 |
   | 대시보드 | 목록만 반환 | 직접 갱신 |

5. 강의와 연결할 때 `Lecture.resources[]`와 `Resource.lectures` **양쪽을 함께** 고친다.

## Completion / reporting

`l2-resource-ingestion.md`의 완료 보고 형식을 쓴다. 동일성 판단 근거와 연결한 Lecture·페이지 범위를 밝힌다.

## Do not

- **같은 자료를 수업마다 새 RES로 만들지 않는다.** 자료 1개를 여러 날 써도 RES는 하나다.
- 과목마다 자료를 복제하지 않는다. 추가 과목은 `related`에 넣는다.
- 외부 URL 자료를 임의로 내려받지 않는다.
- 목차만으로 수업 진도나 사용 페이지를 추정하지 않는다.
- 자료의 별표·반복 출현만으로 시험 출제를 확정하지 않는다.
- `Resource`에 `concepts`나 `questions` 필드를 만들지 않는다. 스키마에 없다.
- L1이나 L5를 호출하지 않는다. 과제·시험 후보는 본문에 기록만 한다.
- 개정판인지 같은 자료인지 확실하지 않으면 새 RES를 만들지 않는다.

## Example

> 이 3장 슬라이드 등록해줘. 오늘 21~38페이지 봤어.

<!-- study-brain-template -->
