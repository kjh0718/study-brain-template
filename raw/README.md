# Raw

학습 입력의 원본을 보존한다. 이 문서가 동적 학기·과목 폴더의 용도와 저장 위치를 안내한다.

## 구조

```text
raw/
└─ <term>/
   └─ <course-slug>/
      ├─ transcripts/
      ├─ resources/
      ├─ assignments/
      ├─ past-exams/
      └─ notices/
```

`<term>`과 `<course-slug>`는 연결된 CRS의 학기와 과목 폴더를 따른다. 필요한 동적 폴더는 실제 원본을 보존할 때 만들며, 그 안에 README를 만들지 않는다.

## 여기 두는 것

| 폴더 | 원본 |
|---|---|
| `transcripts/` | 수업 전사 원문 Markdown(`.md`). 원래 타임스탬프도 보존한다 |
| `resources/` | 강의자료·교재·일반 자료 원본. 표준 파일 입력은 PDF |
| `assignments/` | 과제 명세서·과제지·제출 요건 원본 |
| `past-exams/` | 기출·족보 원본 또는 복원본과 제공된 정답·해설. 표준 파일 입력은 PDF |
| `notices/` | 공지·운영 근거 원본 |

## 보존 규칙

- 종류와 과목(course)·학기(term)를 먼저 확정한 뒤 `raw/<term>/<course-slug>/<kind>/`에 보존한다. 미확정 입력은 이동하거나 변환하지 않고 `inbox/`에 그대로 둔다.
- 원본 내용을 수정·요약·교정·덮어쓰기하지 않고 파일을 삭제하지 않는다. 구조화 노트가 원본을 가리키며 반대 방향의 참조는 만들지 않는다.
- PPT/PPTX/HWP/DOCX/JPG/JPEG/PNG 등은 자동 변환하거나 이동하지 않는다. 사용자에게 PDF 준비를 요청하고 준비된 뒤 처리한다.
- `.txt`/`.srt`/`.vtt` 전사도 자동 변환하지 않는다. 전사의 표준 입력은 `.md`이며, 채팅에 직접 붙여넣은 전사는 원문 그대로 `.md`로 보존할 수 있다.
- `raw/documents/`는 폐지했다. 일반 자료는 `resources/`, 공지·운영 근거는 `notices/`, 과제 원본은 `assignments/`로 분류한다.
- 공유 RES·PEX의 원본은 최초 canonical home에 한 번만 보존한다. 기출 폴더의 `<term>`은 과거 시험 시행 학기가 아니라 canonical home CRS의 `term`이다.
- 과목 간 이동은 사용자가 승인한 [SECOND-BRAIN.md](../SECOND-BRAIN.md) 2.13의 migration에서만 가능하다. 이동 전후 내용(해시)을 유지하고 구조화 노트·출처 링크도 함께 갱신한다.

## 여기 두지 않는 것

- 미확정 입력과 표준 형식이 아닌 입력 → [inbox/](../inbox/README.md)
- 요약·분석·진행 상태 → [study/](../study/README.md), [wiki/](../wiki/index.md)
- 외부 URL만 있는 자료. 내려받지 않고 구조화 노트의 `source`에 URL을 적는다
- 과제 제출 결과물 자체

## 규격

원본에는 학습 노트 frontmatter를 강제하지 않는다. 원본을 가리키는 구조화 노트는 [Schemas](../_system/schemas/README.md)의 규격을 따른다.

## 관련 워크플로

세부 보존·입력 정책은 [SECOND-BRAIN.md](../SECOND-BRAIN.md), 종류별 실행 절차는 [Workflows](../_system/workflows/README.md)를 따른다.
