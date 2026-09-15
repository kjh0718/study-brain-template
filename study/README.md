# Study

과목·학기 맥락에 묶인 구조화 노트를 담는다. 이 문서가 동적 과목 폴더의 용도와 저장 위치를 안내한다.

## 구조

```text
study/
└─ <term>/
   └─ <course-slug>/
      ├─ course.md
      ├─ lectures/
      ├─ resources/
      ├─ assignments/
      ├─ exams/
      ├─ past-exams/
      ├─ course-facts/
      ├─ questions/
      └─ reviews/
```

`<term>`은 연결된 CRS의 `term`, `<course-slug>`는 과목을 처음 만들 때 정한 폴더 식별자다. 필요한 동적 폴더는 실제 노트를 저장할 때 만든다.

## 여기 두는 것

| 위치 | Type | 역할 |
|---|---|---|
| `course.md` | CRS | 과목·학기 기준 정보와 관련 노트 대시보드 |
| `lectures/` | LEC | 실제 수업 세션의 요약, 교수 발언, 개념·질문·자료 연결 |
| `resources/` | RES | 자료 구조와 출처, 강의별 사용 범위 요약 |
| `assignments/` | ASM | 과제 요구사항, 마감 근거, 제출 상태 |
| `exams/` | EXM | 해당 과목의 시험 일정과 근거로 확인된 범위 |
| `past-exams/` | PEX | 기출·족보의 문항별 분석과 정답 출처 구분 |
| `course-facts/` | FAC | 과목 운영 사실, 근거와 변경 이력 |
| `questions/` | QST | 미해결 질문, 발생 맥락과 해결 근거 |
| `reviews/` | REV | 복습 회차, 실제 사용자 응답과 학습 상태 |

## 저장 규칙

- CRS는 `study/<term>/<course-slug>/course.md`에 둔다.
- course-scoped 노트(LEC, RES, ASM, EXM, PEX, FAC, QST, REV)는 `course`가 가리키는 CRS의 폴더 아래 해당 종류 폴더에 둔다. `course: null`은 금지한다.
- 과목 또는 학기(term)가 미확정이면 CRS와 구조화 노트를 만들지 않고 입력을 `inbox/`에 그대로 둔다.
- 공유 RES·PEX는 최초 등록 과목인 canonical home 한 곳에만 저장한다. 다른 과목은 `related`에 CRS ID로 연결하며, 중복은 `study/` 전체에서 확인한다.
- 동적 `<term>/<course-slug>/<kind>` 폴더에는 README를 만들지 않는다.
- 과목 재배정은 일반 ingest가 아니다. 사용자 요청에 따라 [SECOND-BRAIN.md](../SECOND-BRAIN.md) 2.13의 migration 절차로만 수행한다.

## 여기 두지 않는 것

- 원본 전사·자료·기출·과제·공지 → [raw/](../raw/README.md)
- 과목을 넘어 재사용하는 CON·CLU → 전역 [wiki/](../wiki/index.md)
- 과목·학기가 미확정인 입력 → [inbox/](../inbox/README.md)

## 규격

저장 경로와 세부 필드 규칙의 정본은 [Schemas](../_system/schemas/README.md)다. 먼저 [common.md의 Storage Paths](../_system/schemas/common.md#storage-paths)를 따른다.

## 관련 워크플로

실행 절차는 [Workflows](../_system/workflows/README.md)를 참조한다. 운영 판단과 과목 재배정 기준은 [SECOND-BRAIN.md](../SECOND-BRAIN.md)가 정한다.
