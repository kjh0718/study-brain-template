# Resource Schema

자료 하나를 등록해 여러 강의에서 재사용하는 RES 노트의 규격이다. 공통 필드는 저장소의 `_system/schemas/common.md`를 따른다. 저장 위치는 `study/resources/`다.

## Frontmatter

아래는 가상 예시다. source와 참조 ID는 실제 자료로 교체한다.

```yaml
---
schema: 1
type: resource
id: RES-20260908-01
title: Chapter 3 - Momentum and Collisions
status: active
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
course: CRS-20260908-01
resource_type: slides
authority: professor
source: raw/resources/chapter03.pdf
page_count: 67
lectures: []
---
```

## Fields

| 필드 | 필수 | 규칙 |
|---|---|---|
| 공통 9개 필드 | 예 | common.md를 따른다. type은 resource, id는 RES-로 시작한다. |
| status | 예 | draft, needs-review, active, archived 중 하나 |
| course | 예 | 주 사용 과목 CRS ID. 공용 자료로 과목이 없으면 null |
| resource_type | 예 | slides, textbook, handout, paper, article, practice, lab, video, dataset, other |
| authority | 예 | professor, official-lms, textbook, student-provided, external, ai-generated, unknown |
| source | 예 | 실제 원본의 루트 기준 경로 또는 접근 가능한 외부 참조 |
| page_count | 아니오 | 확인된 양의 정수. 페이지 개념이 없거나 미확인이면 생략 |
| lectures | 예 | 실제 존재하는 LEC ID 목록. 없으면 [] |

related는 추가 과목 CRS나 다른 자료 등 전용 필드 밖의 관계에 사용한다. 같은 교재가 여러 과목에서 사용돼도 RES를 중복 생성하지 않는다. 전용 필드에 있는 ID를 related에 반복하지 않는다.

course에는 주 사용 과목 하나만 들어간다. 추가 과목은 related에 CRS ID로 기록하며, 이때 그 과목의 Dashboard 조회 대상에도 포함된다. course 필드만으로 조회하면 공유 자료가 누락되므로 조회는 course와 related를 함께 확인한다. 자세한 조회 규칙은 course.md의 Course Identity and Dashboard를 따른다.

authority는 자료의 출처 분류이며 사실의 정확도나 충돌 해결 우선순위를 자동으로 보장하지 않는다. LMS에 올라온 교수 자료는 작성자가 확인되면 professor로 두고 배포 경로를 본문에 기록한다. 작성자·출처를 알 수 없으면 unknown과 needs-review를 사용한다.

## Status

- draft: 원본 참조만 등록하고 구조 분석 전이다.
- needs-review: 출처·버전·내용 확인이 필요하거나 원본에 접근하지 못했다.
- active: 현재 입력 범위의 등록과 정리를 마쳤다.
- archived: 보존용 자료다. 과거 강의의 연결은 유지한다.

## Identity and Versions

- RES-YYYYMMDD-NN 형식을 사용하며 날짜는 등록일이다. 저장소 전체 RES ID에서 중복을 확인한다.
- 파일명만으로 동일 자료라고 판단하지 않는다. 제목, 작성자, 판·버전, 원본 내용 또는 가능한 경우 파일 해시를 비교한다.
- 같은 자료의 재입력·경로 이동은 기존 ID를 유지한다.
- 내용과 페이지가 달라진 개정판은 새 RES로 구분하고 related와 본문에서 이전 판과 연결한다. 과거 Lecture의 페이지 참조를 새 판으로 자동 교체하지 않는다.
- 바이너리의 저장 방식과 Git LFS 사용 여부는 이 스키마가 강제하지 않는다. 최소 .gitignore 정책을 유지한다.

## Lecture Relationship

Lecture.resources[].id와 Resource.lectures는 같은 연결을 양쪽에서 표현한다. 연결·해제 시 양쪽을 함께 확인한다.

사용 페이지의 기준 데이터는 Lecture.resources[].pages다. Resource 본문의 Lecture Usage는 그 정보를 요약한 보기이며 독립적으로 다른 페이지를 기록하지 않는다.

자료 1개를 여러 날 사용해도 RES는 하나를 유지하고 각 Lecture에 그날 확인된 사용 범위를 기록한다. 자료의 목차만으로 수업 진도를 추정하지 않는다.

## Body Structure

```markdown
## Overview

## Structure

## Key Concepts

## Material Emphasis

## Professor Emphasis

## Lecture Usage

## Exam References

## Assignment References

## Version / Provenance

## My Notes

<!-- AI-PROTECTED -->

## Source
```

## Evidence Rules

- Structure에는 확인된 장·절과 페이지를 기록한다.
- Material Emphasis는 자료 자체의 강조이며, Professor Emphasis는 Lecture 원문으로 확인된 발언이다. 둘을 구분한다.
- 교수 발언이나 시험 언급은 해당 Lecture 및 원문 위치로 연결한다.
- 새 Concept를 대량 생성하지 않는다. 기존 Concept를 먼저 찾고 독립적인 지식 가치가 있는 후보만 승격 대상으로 남긴다.
- 과거 시험 자료의 분석 노트는 PEX다. 같은 원본을 RES와 PEX로 무조건 이중 등록하지 않는다.
- 사용자 작성 영역은 Lecture Schema의 보호 범위 규칙과 동일하게 보존한다.
- 외부 링크가 있다는 이유만으로 원본을 열어 검증했다고 기록하지 않는다.

## Workflow Boundary

이 파일은 자료 등록 규격이다. 실제 처리는 향후 SECOND-BRAIN.md의 L2에서 원본 확인, 중복 검색, 구조 분석, 강의 연결과 로그 기록을 정의한다.
