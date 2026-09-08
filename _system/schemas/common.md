# Common Note Schema

Study Brain의 모든 구조화 노트가 따르는 공통 규칙이다.

이 문서는 공통 필드와 식별 규칙만 정의한다. 각 Note Type의 구체적인 필드와 상태값은 해당 Type Schema에서 정의한다. 장기적으로 전체 운영 규칙은 루트의 `SECOND-BRAIN.md`가 단일 기준점이 되며, 이 문서는 스키마 영역의 공통 규칙을 설명한다.

## Core Types

| Prefix | Type | Location |
|---|---|---|
| CRS | course | `study/courses/` |
| LEC | lecture | `study/lectures/` |
| CON | concept | `wiki/concepts/` |
| ASM | assignment | `study/assignments/` |
| EXM | exam | `study/exams/` |
| PEX | past-exam | `study/past-exams/` |
| FAC | course-fact | `study/course-facts/` |
| QST | question | `study/questions/` |
| RES | resource | `study/resources/` |
| REV | review | `study/reviews/` |
| CLU | cluster | `wiki/clusters/` |

`wiki/patterns/`는 Core Type이 아니다. 여러 Source와 Note에서 반복되는 패턴이 충분한 근거를 얻었을 때 Knowledge Promotion Workflow를 통해 생성하는 파생 지식 영역이다.

## Required Frontmatter

모든 구조화 노트는 최소한 다음 필드를 가진다.

```yaml
---
schema: 1
type: lecture
id: LEC-20260908-01
title: 운동량과 충격량
status: processed
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
---
```

## Field Rules

### `schema`

현재 Study Brain schema version이다. Schema migration이 필요한 경우에만 변경한다.

### `type`

다음 11개 Core Type 중 하나만 사용한다.

`course`, `lecture`, `concept`, `assignment`, `exam`, `past-exam`, `course-fact`, `question`, `resource`, `review`, `cluster`

새 Type을 임의로 만들지 않는다.

### `id`

노트의 영구 식별자다.

- 생성 후 변경하지 않는다.
- 파일명이 변경되어도 ID는 유지한다.
- Type Prefix를 포함한다.
- 사람이 읽을 수 있는 ASCII-safe 값을 사용한다.
- 공백을 사용하지 않는다.
- 날짜와 일련값을 조합할 때는 같은 날짜 안에서 충돌하지 않게 한다.

예: `CRS-20260908-01`, `LEC-20260908-01`

### `title`

사람에게 보여줄 실제 제목이다. 한국어를 사용할 수 있다.

### `status`

노트 종류별로 허용된 상태값을 사용한다. 구체적인 상태값은 각 Type Schema에서 정의하며, AI가 임의의 새 상태값을 만들지 않는다.

### `topics`

통제된 Topic Vocabulary를 사용한다.

```yaml
topics:
  - momentum
  - classical-mechanics
```

새 topic을 만들기 전에 `wiki/clusters/_topics.md`를 확인한다. 의미가 같은 유사 topic을 중복 생성하지 않는다.

### `related`

다른 구조화 노트의 ID를 저장한다.

```yaml
related:
  - CON-20260908-01
  - LEC-20260908-01
```

파일 경로나 제목 대신 영구 ID를 사용한다.

### `created` and `updated`

ISO 8601 날짜 형식인 `YYYY-MM-DD`를 사용한다.

- `created`: 최초 생성일. 이후 변경하지 않는다.
- `updated`: 내용이 변경된 마지막 날짜.

## File Rules

- 구조화 노트 파일은 Markdown(`.md`)으로 저장한다.
- 파일명은 사람이 읽을 수 있는 kebab-case를 기본으로 한다.
- 파일명에 ID를 포함하는 경우에도 frontmatter의 `id`가 정식 식별자다.
- 폴더의 사용법은 해당 폴더의 `README.md`에 설명한다.
- 새 구조나 운영 규칙은 관련 문서와 루트 `SECOND-BRAIN.md`의 기준을 함께 갱신한다.

## Source and Note Boundary

`raw/`는 원본 자료와 변환 전 입력을 보존하는 영역이다. `study/`와 `wiki/`의 구조화 노트는 원본을 요약·정리한 결과이며, 필요할 때 원본 경로를 본문에 명시한다.

구조화 노트에 없는 사실을 원본처럼 가장하지 않는다. 불확실한 내용은 본문에서 불확실성이나 검증 필요성을 표시한다.

## Shared Value and Relationship Rules

- 공통 필드의 schema는 정수 1, type·id·title·status는 비어 있지 않은 문자열이다. topics와 related는 중복 없는 문자열 목록이다.
- topics, related 및 각 타입의 관계 목록은 값이 없으면 []다. null 허용 여부는 해당 필드 표를 따른다. 선택 필드는 모르면 생략한다.
- 새 ID의 접두사는 대문자 Core Type Prefix다. 이후 의미 기반 식별자를 사용할 때는 ASCII 소문자 kebab-case를 사용한다. 기존 ID는 유지한다.
- PREFIX-YYYYMMDD-NN 형식의 날짜는 기본적으로 노트 생성일이다. Lecture만 예외로 수업일을 사용하며, 수업일이 미확인이면 생성일을 쓰고 date는 null로 남긴다. 예외의 세부 규칙은 lecture.md를 따른다.
- 같은 Prefix와 날짜의 일련번호는 저장소 전체에서 충돌을 확인한다. 제목·파일명·날짜가 바뀌어도 기존 ID는 유지한다.
- sources와 answer_sources는 구조화 노트 ID 목록이다. source는 원본 경로 또는 외부 참조다. 둘을 혼용하지 않는다.
- sources에서 참조하는 노트가 없고 직접 원문만 있는 경우 Sources 본문에 원본 경로와 위치를 기록한다. 목록을 채우기 위해 가짜 ID를 만들지 않는다.
- 근거가 필요하다는 조건은 Sources 본문의 직접 원본 근거로도 충족할 수 있다. 제목만 있는 링크나 확인하지 않은 URL은 검증된 근거가 아니다.
- 관련 노트 ID는 전용 관계 필드에 먼저 기록한다. related에는 그 밖의 연결만 둔다.
- 모든 관계가 역방향 필드를 요구하지는 않는다. Lecture.resources와 Resource.lectures만 현재 명시적으로 양방향 유지한다.
- 날짜는 YYYY-MM-DD다. 시간이 확인된 경우 일시 필드에 시간대 포함 ISO 8601 문자열을 쓴다. 예: "2026-09-15T23:59:00+09:00". 시간대를 모르면 임의로 넣지 않고 확인 필요로 기록한다.
- 원문 경로는 저장소 루트 기준 / 구분자를 기본으로 한다. Markdown 링크는 실제 파일 위치를 기준으로 작성한다. ID 자체를 파일 경로처럼 링크하지 않는다.

## Shared Authority Values

authority를 사용하는 스키마는 다음 값만 사용한다.

professor, official-lms, textbook, student-provided, external, ai-generated, unknown

교수 제공 수업자료는 작성자가 확인되면 professor, 학생 필기·복원본은 student-provided로 분류한다. 배포처와 작성자가 다르면 본문에 둘 다 기록한다. 강의자료 여부는 resource_type으로 구분한다.

이 분류는 출처를 설명하며 자동 신뢰도 순위가 아니다. 사실의 적용 시점·범위·명시적 변경 여부를 함께 검토한다. AI 생성 설명을 교수 발언이나 공식 자료로 표시하지 않는다.

## Protected User Sections

My Notes, My Understanding, My Questions, Personal Reflection 제목 아래는 사용자 영역이다. 해당 제목부터 다음 동급 또는 상위 제목 직전까지 보존한다. AI-PROTECTED 주석은 표식이며 주석이 없어도 같은 제목은 보호한다.

사용자가 명시적으로 그 영역의 수정을 요청한 경우에만 변경한다. 파일 전체를 다시 생성하거나 노트를 병합하는 경우에도 이 보호 범위가 유지돼야 한다.

## Scope

이 스키마 규칙은 구조화된 학습 노트에 적용한다. README, 스키마 문서, HOME, SECOND-BRAIN, 로그, topic 어휘표와 raw 원본에는 학습 노트 frontmatter를 강제하지 않는다.

SECOND-BRAIN.md가 작성되면 운영 원칙과 문서 우선순위의 단일 기준점이 된다. 각 스키마는 세부 데이터 규격을 제공하며, 충돌을 발견하면 표시하고 일관되게 수정한다.
