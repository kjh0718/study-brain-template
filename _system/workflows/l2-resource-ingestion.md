# L2 — Resource ingestion 실행 문서

대응 레이어: **L2**. 판단 기준의 정본은 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)의 `L2 — Resource ingestion` 절이고, 데이터 규격은 [`resource.md`](../schemas/resource.md)다.

> 이 문서는 실행 보조 문서다. 규칙을 새로 만들지 않고 검색 명령, 체크리스트, 보고·로그 형식, 실행 예시만 담는다. 이 문서와 SECOND-BRAIN.md가 다르면 SECOND-BRAIN.md가 맞고 이 문서를 고친다.

## 한눈에 보기

| 항목 | 값 |
|---|---|
| 목적 | 자료 하나를 **한 번만** 등록해 여러 강의에서 재사용한다 |
| 입력 | 자료 PDF 파일 또는 접근 가능한 외부 참조. [L1](l1-lecture-ingestion.md)이 넘긴 미등록 자료 |
| 저장소 쓰기 | 예 |
| 호출할 수 있는 레이어 | L4 — **단독 실행일 때만** |
| 주 생성물 | RES 1개(또는 기존 RES 갱신) |

**L2는 어떤 경우에도 L1을 호출하지 않는다.** 과제·시험·운영 사실을 발견해도 L5를 호출하지 않고 자기 본문에 후보로만 적는다.

### 부모 L1이 있을 때와 단독 실행일 때의 차이

이 구분이 L2에서 가장 자주 틀리는 부분이다.

| 단계 | L1이 호출한 경우 | 사용자가 단독 실행한 경우 |
|---|---|---|
| 개념 후보 | 부모 L1에 돌려준다. **L4를 직접 부르지 않는다** | L2가 직접 L4를 호출한다 |
| 대시보드 | 대상 CRS 목록만 부모에 돌려준다 | L2가 직접 갱신한다 |
| CON 생성 | 어느 쪽이든 **L2가 직접 만들지 않는다** | 같다 |

## 0. 시작 전 확인

- [ ] 이 자료를 등록할 과목과 학기를 SECOND-BRAIN.md의 `공통 준비 절차 — 대상 Course 확보`로 확정할 수 있다. 공용 자료라는 이유로 `course` 없이 등록하지 않는다. 확정하지 못하면 입력을 옮기지 않고 `inbox/`에 둔 채 보류한다.
- [ ] 로컬 파일이면 PDF이고, 원본을 `raw/<term>/<course-slug>/resources/`에 보존할 수 있다.
- [ ] PPT/PPTX/HWP/DOCX/이미지(JPG/JPEG/PNG 등)는 직접 ingest하지 않는다. `inbox/`에 있으면 이동하거나 변환하지 않고 PDF 변환을 요청하며, PDF가 준비된 뒤 처리한다.
- [ ] 외부 URL만 있어도 등록할 수 있다. 이때 내려받지 않고 `source`에 그 URL을 적는다.
- [ ] 원본·참조에 접근하지 못했으면 등록만 하고 내용 분석은 보류한 채 `needs-review`로 둔다.

## 1. 검색 방법

공통 명령은 [`README.md`](README.md)에 있다.

**중복 RES 찾기 (가장 중요)** — 검색 키는 제목·작성자·판·내용이며, 가능하면 파일 해시까지 본다. **파일명만으로 판단하지 않는다.** canonical home이 다른 과목일 수 있으므로 과목 폴더로 좁히지 않고 **항상 `study/` 전체를 본다.**

```bash
rg -n "^(id|title|resource_type|authority|source|course|page_count):" study -g "**/resources/*.md"
```

**내용 동일성 확인** — 같은 자료가 다른 이름이나 다른 과목 폴더에 저장됐는지 본다. `raw/` 전체의 자료 PDF 목록을 뽑는다.

```bash
rg --files raw -g "**/resources/*.pdf"
```

PowerShell에서는 같은 목록으로 해시를 구한다.

```powershell
rg --files raw -g "**/resources/*.pdf" | ForEach-Object { Get-FileHash -Algorithm SHA256 -LiteralPath $_ } | Sort-Object Hash
```

다른 셸이면 목록의 파일마다 그 셸의 해시 도구(`sha256sum` 등)를 쓴다. 해시가 같으면 같은 파일이고, 해시가 달라도 개정판일 수 있으므로 제목·판·페이지 수를 함께 본다.

**RES ID 일련번호 확보** — C3에서 접두사를 `RES`로 바꾼다. 날짜 자리는 **등록일**이다(수업일이 아니다).

**이 자료를 이미 쓰는 LEC 찾기** — 공유 자료는 다른 과목의 LEC도 쓰므로 `study/` 전체를 본다.

```bash
rg -ln "RES-20260908-01" study -g "**/lectures/*.md"
```

읽는 범위는 자료 원본, `study/` 전체의 기존 RES frontmatter 목록(다른 과목 폴더 포함), 대상 CRS, 호출한 LEC까지다.

## 2. 실행 체크리스트

- [ ] **1. 원본 처리.** 로컬 PDF면 `raw/<term>/<course-slug>/resources/`에 보존한다. 같은 내용의 원본이 이미 `raw/` 아래(다른 과목 폴더 포함)에 있으면 다시 복사하지 않는다. 외부 URL만 있으면 **내려받지 않고** `source`에 URL을 적는다. 사용자가 사본 보관을 요청했을 때만 `raw/`에 저장한다.
- [ ] **2. 동일성 판단.** 위 검색으로 `study/` 전체의 기존 RES가 같은 자료인지 확인한다.
- [ ] **3. 생성 또는 갱신.** 기존 RES가 있으면 다른 과목 폴더에 있어도 그 노트를 갱신하고, 없으면 `study/<term>/<course-slug>/resources/`에 생성한다.
- [ ] **4. 구조 분석.** 확인된 장·절과 페이지만 기록한다. **목차로 진도를 추정하지 않는다.**
- [ ] **5. 과목 연결.** 새 RES의 `course`에는 이번에 등록하는 과목을 canonical home으로 넣는다. 다른 과목을 canonical home으로 가진 RES를 재사용하면 `course`와 저장 위치를 바꾸지 않고 `related`에 이번 과목의 CRS ID를 추가한다. **과목마다 복제하지 않는다.**
- [ ] **6. 강의 연결.** 호출한 LEC이 있으면 `Resource.lectures`와 `Lecture.resources[]`를 양쪽 다 고친다.
- [ ] **7. 개념 후보.** 부모 L1이 있으면 돌려주고, 단독 실행이면 [L4](l4-knowledge-extraction.md)를 호출한다. **어느 쪽이든 L2가 CON을 직접 만들지 않는다.**
- [ ] **8. 대시보드.** 표시가 달라지는 CRS를 모은다. 부모가 있으면 목록만 돌려주고, 단독이면 직접 갱신한다.
- [ ] **9. 로그 기록.**

### 본문 채우기

[`resource.md`](../schemas/resource.md)의 Body Structure를 따른다.

| 절 | 넣는 것 | 주의 |
|---|---|---|
| `## Overview` | 자료의 성격과 범위 | |
| `## Structure` | 확인된 장·절과 페이지 | 목차로 진도를 추정하지 않는다 |
| `## Key Concepts` | 개념 후보와 연결된 CON | RES에는 `concepts` 필드가 **없다.** 연결은 `related` + 이 절로 한다 |
| `## Material Emphasis` | 자료 자체의 강조(굵게, 별표, 요약 슬라이드) | 페이지를 함께 적는다 |
| `## Professor Emphasis` | 전사로 확인된 교수 발언 | 해당 LEC ID와 원문 위치로 연결한다. **자료 강조와 같은 절에 넣지 않는다** |
| `## Lecture Usage` | LEC별 사용 범위 **요약** | 기준 데이터는 `Lecture.resources[].pages`다. 여기서 다른 페이지를 독립적으로 기록하지 않는다 |
| `## Exam References` | 시험 관련 후보 | **후보일 뿐이다.** L5를 부르지 않는다 |
| `## Assignment References` | 과제 관련 후보 | 같다 |
| `## Version / Provenance` | 판·버전, 배포 경로, 작성자 | 배포처와 작성자가 다르면 둘 다 적는다 |
| `## My Notes` | — | **비운 채 둔다** |
| `## Source` | 원본 경로 또는 URL, 접근 여부 | 접근하지 못했으면 그 사실을 적는다 |

## 3. 사용자 확인이 필요한 지점

| 상황 | 처리 |
|---|---|
| 과목이나 학기가 불명확 | RES를 만들지 않는다. 입력을 옮기지 않고 `inbox/`에 둔 채 확인 요청 |
| PPT/PPTX/HWP/DOCX/이미지 입력 | 이동하거나 변환하지 않고 `inbox/`에 둔 채 PDF 변환 요청 |
| 원본·참조에 접근 불가 | `status: needs-review`. 확인된 참조만 `source`에. **내용 분석을 하지 않는다** |
| 기존 RES를 다른 과목으로 옮겨야 할 것 같음 | 재실행에서 옮기지 않는다. SECOND-BRAIN.md 2.13의 migration 대상으로 보고한다 |
| 개정판인지 같은 자료인지 불확실 | 새 RES를 만들지 않고 보고한다 |
| 작성자·출처 불명 | `authority: unknown` + `needs-review` |
| 같은 원본을 RES와 PEX 중 어디에 넣을지 불명확 | 이중 등록하지 않고 확인한다. 과거 시험 자료의 분석은 [L3](l3-past-exam-ingestion.md)이 담당한다 |

## 4. 하지 않는 것

- **같은 자료를 수업마다 새 RES로 만들지 않는다.** 자료 1개를 여러 날 써도 RES는 하나다.
- 과목마다 자료를 복제하지 않는다. 추가 과목은 `related`에 넣는다.
- 재사용하는 RES의 `course`와 저장 위치를 바꾸지 않는다.
- 과목이 바뀌었다는 이유로 기존 RES의 `source`만 고치거나 원본을 다른 과목 폴더로 옮기지 않는다. 같은 과목 폴더 안에서 원본 경로만 바뀐 경우에만 `source`를 고친다.
- PDF가 아닌 파일(PPT/PPTX/HWP/DOCX/이미지)을 직접 ingest하거나 변환하지 않는다.
- 외부 URL 자료를 임의로 내려받아 `raw/`에 넣지 않는다.
- 외부 링크가 있다는 이유만으로 원본을 검증했다고 기록하지 않는다.
- 목차만으로 수업 진도나 사용 페이지를 추정하지 않는다.
- 자료의 별표·반복 출현만으로 시험 출제를 확정하지 않는다.
- `Resource`에 `concepts`나 `questions` 필드를 추가하지 않는다.
- 과거 LEC의 페이지 참조를 새 판으로 자동 교체하지 않는다.
- 자료가 참조하는 또 다른 자료를 연쇄 수집하지 않는다.
- L1이나 L5를 호출하지 않는다.

## 5. 완료 조건

- [ ] `source`가 로컬 경로면 canonical home CRS의 `raw/<term>/<course-slug>/resources/` 아래에 그 파일이 실제로 있다. 외부 URL이면 형식이 유효하고 접근 여부가 `## Source`에 적혀 있다.
- [ ] `resource_type`과 `authority`가 [`resource.md`](../schemas/resource.md)의 허용 값 안에 있다.
- [ ] `lectures`의 ID가 모두 존재하고 반대편 `Lecture.resources`와 일치한다.
- [ ] 전용 필드에 넣은 ID를 `related`에 중복해 넣지 않았다.
- [ ] 로그를 기록했다.

## 6. 완료 보고 형식

```text
L2 Resource ingest 완료

- Resource: RES-20260908-01 (신규) / status: active
- 제목: 제3장 운동량과 충돌
- resource_type: slides / authority: professor
- source: raw/<term>/<course-slug>/resources/physics2-ch03.pdf (보존)
- 동일성 판단: study/ 전체에 기존 RES 없음 (제목·작성자·해시 비교)
- canonical home: CRS-20260908-01 (study/<term>/<course-slug>/resources/) / 공유 과목(related): 없음
- 강의 연결: LEC-20260908-01 pages 21-38 (양방향)
- 개념 후보: 3건 → 부모 L1에 반환 (단독 실행이면 L4 호출)
- 시험·과제 후보: 시험 1건 본문 기록만 (L5 호출 안 함)
- 대시보드: 부모 L1에 CRS-20260908-01 반환
- 보류: 없음
- 로그: 3줄
```

## 7. 로그 기록

```text
- 2026-09-08 18:36 | L2 | preserve-source | raw/<term>/<course-slug>/resources/physics2-ch03.pdf | done | 교수 배포 슬라이드 원본
- 2026-09-08 18:38 | L2 | create-note | RES-20260908-01 | done | 제3장 슬라이드 신규 등록
- 2026-09-08 18:40 | L2 | sync-relations | RES-20260908-01 + LEC-20260908-01 | done | pages 21-38 양방향
```

외부 URL만 등록해 원본을 보존하지 않았으면 `preserve-source` 줄을 쓰지 않고, `create-note` 메모에 외부 참조임을 적는다.

## 8. 실행 예시

### 예시 A — 하나의 PDF를 네 번의 수업에서 쓰는 경우

09/08 수업에서 `physics2-ch03.pdf` 21~38쪽을 썼고, 09/10에 39~52쪽, 09/15에 53~67쪽을 썼다.

```text
RES-20260908-01  (파일 하나, 노트 하나)
├─ LEC-20260908-01 → pages "21-38"
├─ LEC-20260910-01 → pages "39-52"
└─ LEC-20260915-01 → pages "53-67"
```

- 09/10 수업의 L1은 이 자료를 다시 등록하지 않는다. 검색으로 `RES-20260908-01`을 찾아 재사용하고, `Lecture.resources`에 그날 확인된 범위만 적는다.
- `Resource.lectures`에는 LEC ID 셋이 쌓인다. `RES.id`의 날짜(`20260908`)는 **최초 등록일**이며 09/10 수업에 쓴다고 해서 바뀌지 않는다.
- `## Lecture Usage`는 위 표를 요약해 보여줄 뿐이다. 여기서만 다른 페이지를 적으면 기준 데이터와 어긋난다.
- **같은 PDF를 RES 4개로 만들면 실패다.**

### 예시 B — 개정판이 들어온 경우

10월에 `physics2-ch03-v2.pdf`가 배포됐고 페이지 구성이 달라졌다.

- 해시가 다르고 페이지 수도 다르다 → 같은 자료가 아니다. 새 `RES-20261005-01`을 만들고 `related`와 `## Version / Provenance`에서 이전 판과 연결한다.
- **09월 LEC들의 `pages`를 새 판 기준으로 바꾸지 않는다.** 그 수업에서 실제로 본 것은 이전 판이다.
- 표지만 바뀌고 내용이 같으면 새 RES를 만들지 않고 기존 노트의 `## Version / Provenance`에 적는다. 어느 쪽인지 확실하지 않으면 만들지 않고 보고한다.

### 예시 C — 외부 URL만 있는 경우

교수가 LMS에 외부 논문 링크만 올렸다.

- 내려받지 않는다. `source: https://...`, `authority: external`.
- 링크를 열어 내용을 확인하지 못했으면 `status: needs-review`로 두고 `## Source`에 접근하지 못했다고 적는다. `## Structure`는 비운다.
- 링크가 있다는 사실만으로 `## Key Concepts`를 채우지 않는다.
