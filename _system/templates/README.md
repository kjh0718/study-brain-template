# Templates

11개 Core Type의 새 노트 작성 양식을 보관한다.

## 템플릿과 학습 노트의 차이

템플릿은 **양식**이고 학습 노트는 **완성된 데이터**다. 값을 채우지 않은 템플릿 파일은 유효한 학습 노트가 아니다. 자리표시자가 남아 있는 파일을 `study/`나 `wiki/`에 두지 않는다.

규칙의 근거는 [`_system/schemas/`](../schemas/README.md)이고, 처리 절차는 루트 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)다. 이 폴더는 그 규칙에 맞춘 작성 양식만 제공하며 규칙을 다시 정의하지 않는다.

특정 플러그인을 전제하지 않는다. Templater 같은 자동 실행 문법을 쓰지 않으므로, 사람이 직접 복사해 채우거나 에이전트가 값을 넣어 쓸 수 있다.

## 템플릿 목록

| 템플릿 | 새 노트 저장 위치 | 규격 |
|---|---|---|
| `course.md` | `study/courses/` | [course](../schemas/course.md) |
| `lecture.md` | `study/lectures/` | [lecture](../schemas/lecture.md) |
| `resource.md` | `study/resources/` | [resource](../schemas/resource.md) |
| `concept.md` | `wiki/concepts/` | [concept](../schemas/concept.md) |
| `assignment.md` | `study/assignments/` | [assignment](../schemas/assignment.md) |
| `exam.md` | `study/exams/` | [exam](../schemas/exam.md) |
| `past-exam.md` | `study/past-exams/` | [past-exam](../schemas/past-exam.md) |
| `course-fact.md` | `study/course-facts/` | [course-fact](../schemas/course-fact.md) |
| `question.md` | `study/questions/` | [question](../schemas/question.md) |
| `review.md` | `study/reviews/` | [review](../schemas/review.md) |
| `cluster.md` | `wiki/clusters/` | [cluster](../schemas/cluster.md) |

공통 필드 규칙은 [common](../schemas/common.md)을 함께 읽는다.

## 자리표시자

`{{...}}` 형태이며 모두 치환해야 한다. 하나라도 남으면 완성된 노트가 아니다.

| 자리표시자 | 넣을 값 |
|---|---|
| `{{id}}` | 해당 타입 접두사를 쓴 영구 ID. 예: `LEC-20260908-01` |
| `{{title}}` | 사람이 읽을 제목 |
| `{{created}}` / `{{updated}}` | `YYYY-MM-DD` |
| `{{course_id}}` | 실제 존재하는 `CRS-` ID |
| `{{subject_id}}` | 사실의 대상 노트 ID |
| `{{date}}` | 실제 날짜 `YYYY-MM-DD` |
| `{{source}}` | 로컬 원본의 저장소 루트 기준 경로, 또는 접근 가능한 외부 URL |
| `{{exam_type}}` `{{resource_type}}` `{{authority}}` `{{provenance}}` `{{fact_type}}` `{{question_type}}` `{{review_type}}` | 각 템플릿 상단 주석에 적힌 허용 값 중 하나 |

자리표시자는 YAML 문자열로 두기 위해 따옴표로 감싸 두었다. 치환한 뒤 날짜와 숫자는 따옴표를 빼도 되고 그대로 두어도 된다.

본문의 `<!-- ... -->` 주석은 작성 안내다. 값을 채운 뒤 남겨 두어도 되고 지워도 된다. 완성된 노트에는 `{{`로 시작하는 문자열이 하나도 남아 있지 않아야 한다.

## 기본 상태값

새 노트의 시작값이며, 타입마다 실제로 허용되는 값이다.

`course=planned` `lecture=draft` `resource=draft` `concept=draft` `assignment=open` `exam=planned` `past-exam=draft` `course-fact=needs-review` `question=open` `review=planned` `cluster=draft`

**기존 노트를 갱신할 때 이 기본값으로 상태를 덮어쓰지 않는다.**

## 필수 정보가 없을 때

- 스키마가 `null`을 허용하는 필드는 `null`을 그대로 둔다. 템플릿에는 이미 그렇게 들어 있다.
- `null`을 허용하지 않는 필수 필드를 채울 수 없으면 그 노트를 완성본으로 만들지 않는다. 원본은 `raw/`에 보존하고 `inbox/`에 보류 메모를 남긴다.
- 값을 지어내지 않는다. 모르는 항목은 각 타입의 검증 필요 계열 절에 무엇을 확인해야 하는지 적는다.
- 관계 목록은 `[]`로 시작한다. 아직 없는 노트의 ID를 미리 적지 않는다.

## 선택 필드

기본 frontmatter에서 빠져 있다. 값을 확인했을 때만 추가한다.

- `course.md`: `code`, `term`, `instructor`
- `lecture.md`: `week`
- `resource.md`: `page_count`
- `assignment.md`: `submission_method`
- `course-fact.md`: `effective_from`

해당 타입에 없는 필드는 만들지 않는다. 예를 들어 Resource에는 `concepts`나 `questions`가 없으므로 개념·질문 연결은 `related`와 본문 절을 쓴다.

## 사용자 보호 영역

각 템플릿 끝에 그 타입의 보호 제목과 `<!-- AI-PROTECTED -->` 표식이 있다. `My Notes`, `My Understanding`, `My Questions`, `Personal Reflection`이 여기 해당한다.

- 표식만 두고 비워 둔다. 안내 문장이나 예시를 넣지 않는다.
- 그 제목부터 다음 동급 제목 직전까지가 보호 범위다.
- AI는 이 구간을 고치거나 옮기지 않는다.

`course.md`의 `## Related Notes`에는 `<!-- AUTO-MANAGED:start -->`와 `<!-- AUTO-MANAGED:end -->`가 있다. 이 구간은 자동 관리 영역이며 사람이 직접 쓴 내용을 두지 않는다.

## 기존 노트에는 쓰지 않는다

템플릿은 **새 노트를 만들 때만** 쓴다. 이미 값이 들어 있거나 사용자 보호 영역에 내용이 있는 노트를 템플릿으로 통째로 다시 만들지 않는다. 기존 노트는 필요한 부분만 고친다.
