# 고의 오류 fixture

<!-- 통합 시험용 가상 데이터. 실제 학습 자료가 아니다. -->

L8 무결성 검사가 각 오류를 잡는지 확인하기 위한 파일이다. **정상 노트가 아니다.**
`vault/`와 분리해 두어 정상 검사 결과를 오염시키지 않는다.

| 파일 | 심은 오류 | L8 검사 항목 |
|---|---|---|
| `bad-yaml.md` | invalid YAML | 1 |
| `bad-prefix.md` | type과 ID 접두사 불일치 | 3 |
| `bad-id-shape.md` | ID 형식 계약 위반(대문자·공백) | 3 |
| `bad-missing-ref.md` | 없는 ID 참조 | 4 |
| `bad-duplicate-resource.md` | 한 LEC에 같은 RES가 두 항목 | 5 |
| `bad-duplicate-concept.md` | 중복 개념 + 중복 topic slug | 7, L9 후보 |
| `bad-status.md` | 허용되지 않는 status | 2 |
| `bad-orphan.md` | orphan 노트 | 4 |
| `bad-missing-source.md` | 로컬 source 파일 없음 | 6 |
| `bad-supersedes.md` | 끊어진 supersede 참조 | 9 |

## 저장 경로 오류 (`storage/`)

저장 위치 자체가 검사 대상이라 `storage/` 아래에 vault와 같은 루트 구조로 둔다. `course`는 `vault/`의
CRS를 가리킨다. 각 파일은 저장 규칙 하나만 어기고 나머지는 스키마상 정상이다.

| 파일 | 심은 오류 | L8 검사 항목 |
|---|---|---|
| `storage/study/2026-1/general-physics-2/lectures/bad-storage-path.md` | `course`는 2026-2 CRS인데 2026-1 폴더에 있다 (저장 경로 불일치) | 11 |
| `storage/study/2026-2/general-physics-2/resources/bad-raw-source.md` | `source` 파일은 있지만 canonical home이 아닌 과목의 raw 폴더다 (원본 경로 불일치) | 11 |
| `storage/study/2026-2/general-physics-2/questions/bad-course-null.md` | course-scoped 노트의 `course: null` (course 필수) | 11 |
