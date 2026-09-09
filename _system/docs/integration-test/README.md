# Integration Test — Scenario A~K

> **여기 있는 모든 데이터는 통합 시험용 가상 fixture다. 실제 학습 자료가 아니다.**
> `vault/`와 `broken/`은 `build_fixtures.py`가 매번 새로 만든다. 통째로 지워도 된다.
> 저장소의 실제 `study/`, `wiki/`, `raw/`는 이 테스트가 건드리지 않는다.

## 무엇을 검증하는가

`SECOND-BRAIN.md` + `_system/schemas/` + `_system/templates/` + `_system/workflows/`가
실제 Study Brain 입력에서 **일관되게 동작하는지**를 본다. 자동화 구현 테스트가 아니다.

규칙의 정본 관계는 그대로 유지한다. 이 폴더는 규칙을 만들지 않고 검사만 한다.

| 계층 | 정본 |
|---|---|
| 데이터 필드·상태·관계·ID | [`_system/schemas/`](../../schemas/README.md) |
| 운영 판단 기준 | [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) |
| 실행 절차·명령·보고 형식 | [`_system/workflows/`](../../workflows/README.md) |
| 새 노트 생성 양식 | [`_system/templates/`](../../templates/README.md) |

## 실행

```bash
cd _system/docs/integration-test
python build_fixtures.py     # vault/ 와 broken/ 생성
python check_scenarios.py    # Scenario A~K 검사. FAIL 있으면 exit 1
```

Python 3와 PyYAML만 쓴다. 새 의존성을 추가하지 않았다.

## 파일

| 파일 | 역할 |
|---|---|
| `build_fixtures.py` | 가상 vault와 고의 오류 fixture를 생성 |
| `check_scenarios.py` | Scenario A~K + 공통 스키마 적합성 + L8 탐지 검사 |
| `vault/` | 가상 저장소. L1~L9를 문서대로 수행한 **기대 결과** |
| `broken/` | L8 검사용 고의 오류 노트. `vault/`와 분리해 정상 검사를 오염시키지 않는다 |
| `protected-snapshot.json` | 보호 영역의 SHA-256. 재처리 전후 비교용 |

`_system/docs/template-validation/`은 **템플릿 규격**을 보고, 이 폴더는 **워크플로 결과의 일관성**을 본다. 목적이 다르므로 둘 다 유지한다.

## 테스트 환경

| | |
|---|---|
| 날짜 | 2026-09-09 (최초 실행) / 2026-09-09 (EXM ID 수정 후 재실행) |
| OS | Windows 11 (콘솔 기본 인코딩 cp949) |
| Python | 3.13.3 |
| PyYAML | 6.0.3 |
| 대상 커밋 | `8f4c421` + 미커밋 작업 트리 |

## 사용 fixture

가상 과목 **일반물리학2**를 2026-1과 2026-2 두 학기에 수강한 상황을 만들었다.

- 전사 1건 (약 70분 분량, 타임스탬프 포함). 교수 강조·단순 설명·과제·애매한 마감·시험 언급·추정 표현·PPT 페이지·학생 질문 2건·다음 수업 공지를 모두 포함한다.
- Lecture 4건, Resource 1건(60p를 4개 Lecture가 페이지 범위별 사용), Concept 2건, Cluster 1건
- Assignment 4건 (Scenario D의 A~D 발언에 각각 대응)
- Course Fact 4건 (최초 공지 + Scenario E의 Case 1~3)
- Past Exam 3건 (같은 개념이 3회차 반복), Question 2건, Review 1건, Course 2건
- 보호 영역 25개 (`My Notes`, `My Understanding`, `My Questions`, `Personal Reflection`)
- 고의 오류 9건

## Scenario 결과

| Scenario | 결과 |
|---|---|
| 공통 스키마 적합성 | PASS |
| A Lecture Ingestion | PASS |
| B Resource N:N | PASS |
| C Concept Deduplication | PASS WITH NOTES |
| D Assignment 날짜 | PASS |
| E Course Fact Conflict | PASS |
| F Past Exam | PASS |
| G Protected Sections | PASS |
| H Evidence Recall | PASS |
| I ID 충돌 압박 | PASS WITH NOTES |
| J Re-ingestion / Idempotency | PASS |
| K Partial Failure / Recovery | PASS |
| L8 오류 탐지 | PASS |

**PASS 11 / PASS WITH NOTES 2 / FAIL 0**

최초 실행에서는 Scenario I가 FAIL이었다. EXM ID 정책을 승인받아 수정한 뒤 재실행한 결과다. 경과는 아래 "수정한 문제"에 남긴다.

### A — Lecture Ingestion

검사한 것과 결과.

- Raw 원본이 먼저 보존되고 `LEC.source`가 그것을 가리킨다. 원문 타임스탬프가 훼손되지 않았다.
- 교수 발언은 `## 교수님 강조`에, AI 추론은 `## AI 해석 / 검증 필요`에만 있다. 두 절이 섞이지 않았다.
- 교수가 강조하지 **않았지만** AI가 중요하다고 본 항목("완전 비탄성 충돌의 손실 최대 조건")이 교수 절에 올라가지 않았다.
- 교수 발언마다 원본 경로 + 타임스탬프가 붙어 있다.
- Assignment 생성됨. 애매한 마감을 날짜로 지어내지 않았다.
- EXM이 `sources` 3건을 누적한 형태다. Lecture마다 새 EXM을 만들지 않았다.
- Course Fact와 개념 지식이 분리됐다. 학생 질문 2건이 QST로 추출됐다.
- Review Question에 `(AI 생성)` 표시가 있다.
- PPT 페이지 범위 `21-38`이 기록됐다.
- **대시보드 결정성**: 자동 관리 영역의 20개 항목이 `course` 조회 결과와 정확히 일치하고, 타입 순서 → ID 오름차순 정렬 규칙을 만족한다. 두 번 계산해도 같은 텍스트가 나온다.

### B — Resource N:N

- 같은 자료의 RES가 **정확히 1개**다.
- LEC 4개가 같은 RES를 가리키고 각각 다른 페이지 범위(`1-20`, `21-38`, `39-48`, `49-60`)를 갖는다.
- `Resource.lectures`와 각 `Lecture.resources[].id`가 **완전히 일치**한다. drift 없음.
- Resource 본문 `## Lecture Usage`로 사용 관계를 재구성할 수 있고, 그 값이 정방향 기준 데이터와 같다.
- 같은 `source`를 가리키는 RES가 1개뿐이다. 재등록 시 새 RES가 생기지 않는 구조다.

### C — Concept Deduplication (PASS WITH NOTES)

- `운동량`, `momentum`, `linear momentum` 세 표현이 모두 `CON-momentum` **하나로만** 해석된다. CON이 3개로 갈라지지 않았다.
- alias 검색으로 기존 Concept를 먼저 찾을 수 있다.
- 모든 노트의 `topics`가 어휘표에 등록돼 있다.

**Note — Concept와 Topic은 다른 namespace다.** fixture에 `collision` topic을 넣되 대응하는 CON은 만들지 않아 1:1이 아님을 확인했다. CON은 `{impulse, momentum}`, topic은 `{collision, impulse, momentum}`이다.

이 테스트로 `common.md`의 결합 문장 하나를 발견해 고쳤다. 아래 "수정한 문제" 참조.

### D — Assignment 날짜

| Case | 원문 | `due` | `due_status` |
|---|---|---|---|
| A | "9월 18일까지 제출하세요" | `2026-09-18` | `confirmed` |
| B | "다음 주까지 제출하세요" | `null` | `needs-review` |
| C | "다음 수업 전에 내세요" | `null` | `needs-review` |
| D | "금요일쯤 제출하면 됩니다" | `null` | `needs-review` |

A만 날짜로 확정됐다. B·C·D는 날짜를 지어내지 않았고 원문 표현이 본문에 그대로 남아 있다.

### E — Course Fact Conflict

- **Case 1** ("10월 17일로 변경합니다"): 이전 FAC가 `superseded`가 되고 **파일과 ID는 남았다.** 새 FAC가 `active`이고 `supersedes: [이전 ID]`를 갖는다.
- **저장소 전체에 `superseded_by` 필드가 하나도 없다.** 단방향 정책이 지켜졌다.
- **Case 2** ("시험이 10월 17일입니다"): 변경 선언이 없으므로 자동 overwrite하지 않았다. `needs-review`, `supersedes: []`, `value: null`.
- **Case 3** ("아마 10월 17일쯤"): 확정 Fact로 승격하지 않았다. EXM의 `date`도 고치지 않았다.
- 상충이 남아 있어 `EXM.date_status`가 `confirmed`가 아니다.
- `supersedes` 자기 참조·순환 없음.

### F — Past Exam

- 3회차 PEX 모두 같은 개념에 연결돼 반복성을 분석할 수 있다.
- 각 PEX에 표본 수 기록이 있고, **현재 시험 출제를 확정하는 서술이 없다.** 부인 표시가 모두 있다.
- 네 종류의 근거가 서로 다른 절에 분리돼 있다.

| 근거 | 위치 |
|---|---|
| 교수의 시험 출제 명시 | `EXM ## 교수님 시험 언급` |
| 기출 출제 빈도 | `EXM ## AI 예상 / 검증 필요` |
| 자료 강조 | `EXM ## AI 예상 / 검증 필요` (자료 강조임을 명시) |
| AI 해석 | `EXM ## AI 예상 / 검증 필요` |

`## 확정 범위`에는 기출·자료 강조·AI 해석이 섞이지 않았다.

### G — Protected Sections

보호 영역 25개의 SHA-256을 기록한 뒤, **L1 재처리를 실제로 시뮬레이션**했다. 문서가 허용하는 수정(`## 수업 요약` 갱신, `updated` 변경)만 가하고 다시 해시를 비교했다.

**25개 전부 바이트 단위로 동일하다.** 재처리가 실제로 적용됐음(요약 문구 변경)도 함께 확인해, 아무 일도 하지 않아서 통과한 것이 아님을 보장했다.

### H — Evidence Recall

- "교수님이 과제 마감에 대해 정확히 뭐라고 했어?" → 대상 ASM의 `due`가 `null`이라 **구조화 노트만으로 확정할 수 없다.** Evidence Recall이 필요한 상황이 맞다. `ASM.sources → LEC → LEC.source → raw/transcripts/`로 원문까지 도달할 수 있고, 그 원문에 실제 발언이 있다.
- "시험 범위가 확정된 근거가 뭐야?" → `scope_status`가 `confirmed`가 아니므로 근거 없이 확정으로 답할 수 없다.
- "운동량을 지금까지 어떻게 배웠는지 정리해줘" → `CON-momentum`에 정의와 `sources` 3건이 있어 **원문을 열지 않고** 근거 ID를 붙여 답할 수 있다. 일반 Recall로 충분하다.

경로가 구조적으로 보장되므로 매 질문마다 `raw/` 전체를 읽을 필요가 없다.

### I — ID 충돌 압박 (PASS WITH NOTES)

최초 실행에서 EXM이 충돌해 FAIL이었다. **EXM ID를 `<term>` 기반으로 바꾼 뒤 충돌 0건이다.**

같은 과목을 여러 학기에 수강하는 16개 상황을 계산해 검사했다.

```text
EXM-general-physics-2-2026-1-midterm
EXM-general-physics-2-2026-2-midterm
EXM-general-physics-2-2026-summer-midterm
EXM-general-physics-2-2027-1-midterm      재수강
EXM-general-physics-2-2026-1-quiz-03
EXM-general-physics-2-2026-2-quiz-03
EXM-general-physics-2-2026-1-final
```

안전이 확인된 Type: `EXM`(term 포함), `CRS`(term 포함), `ASM`·`FAC`·`QST`·`REV`(날짜에 연·월·일 포함), `PEX`(연도+학기 포함), `LEC`(수업일), `CON`·`CLU`(과목 비종속). 모든 생성 ID가 형식 계약도 만족한다.

**Note — `RES`가 두 학기에 같은 ID를 갖는 것은 충돌이 아니라 설계된 재사용이다.** 같은 자료는 RES 하나를 공유하고 추가 과목은 `related`에 들어간다. 이번 변경에서 RES 정책은 건드리지 않았다. 내용이 개정된 자료의 구분은 향후 resource schema의 revision/version 규칙으로 다룬다.

**회귀 방지**: `check_scenarios.py`가 `common.md`의 exam 권장 형태 행과 `exam.md`의 Identity 절을 직접 읽어, `<연도>` 형태로 되돌아가면 FAIL을 낸다.

### J — Re-ingestion / Idempotency

- 같은 `course` + `date`의 LEC 중복 없음. 새 ID가 생기지 않는다.
- 같은 제목의 Assignment 중복 없음.
- **모든 노트의 모든 관계 목록에 중복 항목이 없다.** 재실행 시 `sources`에 같은 ID를 다시 append하는 누수가 없다.
- Course 대시보드 20개 항목에 중복 없음.
- 같은 전사 원본이 복제되지 않았다(파일 1개).
- 로그에 완전히 동일한 줄이 없다. 실행 이력으로만 누적된다.

### K — Partial Failure / Recovery

"대시보드 갱신 직전 실패" 상황을 로그로 재현했다.

```
18:47 | L1 | finalize-run | LEC-20260908-01 | partial | 대시보드 갱신 직전 중단
10:02 | L1 | refresh-dashboard | CRS-... | done | 재개. 남은 단계만 수행
10:03 | L1 | finalize-run | LEC-20260908-01 | done | 재개 완료
```

- 로그 14줄이 모두 6칸 형식을 지키고, 작업 코드가 전부 승인 목록 안에 있으며, 결과값이 `done|partial|held|conflict` 중 하나다.
- `partial` 줄마다 같은 대상·레이어·코드의 후속 `done`이 있어 복구가 판정된다.
- **실행 실패가 학습 노트의 `status`로 표현되지 않았다.** `partial`은 로그에만 있다.
- 실패 이전 단계 결과(raw 원본, LEC, ASM)가 그대로 남아 훼손되지 않았다.

이 시나리오에서 L1 문서의 빈틈을 하나 발견해 보완했다. 아래 참조.

### L8 오류 탐지

고의 오류 9건을 모두 탐지했다.

| fixture | 심은 오류 | 탐지된 항목 |
|---|---|---|
| `bad-yaml.md` | invalid YAML | 항목1 |
| `bad-prefix.md` | type과 ID 접두사 불일치 | 항목3 |
| `bad-id-shape.md` | ID 형식 계약 위반(대문자·공백) | 항목3 |
| `bad-missing-ref.md` | 없는 ID 참조 | 항목4 |
| `bad-duplicate-concept.md` | 중복 개념 + 중복 topic slug | 항목7 + L9 후보 |
| `bad-status.md` | `lecture`에 `active` | 항목2 |
| `bad-orphan.md` | orphan 노트 | 항목4 |
| `bad-missing-source.md` | 로컬 source 파일 없음 | 항목6 |
| `bad-supersedes.md` | 끊어진 supersede 참조 | 항목9 |

`l8-maintenance.md`의 검사 항목 10개 중 8번(대시보드 일치)은 Scenario A에서 별도로 검증했고, 10번(보호 영역 존재)은 Scenario G에서 다뤘다.

## 발견한 문제

### 1. EXM ID가 같은 해의 다른 학기에서 충돌한다 (해결됨)

> **A안으로 승인받아 적용했다.** 정식 규칙은 이제 `EXM-<과목 slug>-<term>-<exam_type>`이다.
> 아래는 문제를 어떻게 찾았는지의 기록이다. 적용 내역은 "수정한 문제" 1번에 있다.


**충돌하는 Type**: `exam` (EXM) 하나뿐이다.

**실제 충돌 예**

```
2026-1 일반물리학2 중간고사 -> EXM-general-physics-2-2026-midterm
2026-2 일반물리학2 중간고사 -> EXM-general-physics-2-2026-midterm   충돌
```

같은 과목을 두 학기에 수강하면 두 시험이 같은 ID를 갖는다. 계절학기를 포함하면 한 해에 셋까지 겹칠 수 있다. 퀴즈도 마찬가지다(`...-2026-quiz-03`).

**틀린 가정**: "연도가 시험 회차를 특정한다"고 보았다. 한 해에 학기가 둘 이상이므로 성립하지 않는다. 같은 문서 안에서 `PEX`는 이미 연도 + **학기**를 쓰는데 `EXM`만 연도를 쓴다. 정책 내부의 비일관성이다.

**해결 후보**

| 안 | 형태 | 평가 |
|---|---|---|
| **A. term 사용** | `EXM-<과목>-<term>-<exam_type>` | PEX와 같은 방식. 형식 계약 그대로 만족. 가장 단순 |
| B. CRS 토큰 포함 | `EXM-<CRS id 일부>-<exam_type>` | 유일하지만 길고 CRS가 바뀌면 의미가 흐려진다 |
| C. 날짜+일련번호 | `EXM-<날짜>-<NN>` | 의미 기반의 장점을 잃고 병렬 생성 충돌이 생긴다 |
| D. 일련번호 접미사 | `...-2026-midterm-02` | 충돌을 사후 회피할 뿐 결정적이지 않다 |

**추천: A안.** `EXM-general-physics-2-2026-2-midterm`. 검사로 확인한 결과 2026-1 / 2026-2 / 2026-여름 / 2027-1 재수강 / 학기별 퀴즈 6개 상황에서 충돌이 사라지고 ID 형식 계약도 그대로 만족한다.

고칠 곳은 `_system/schemas/common.md`의 Type별 권장 형태 한 줄과 `_system/schemas/exam.md`의 Identity 절이다. 형식 계약(정규식)은 바뀌지 않고 기존 노트도 재발급이 필요 없다.

적용 결과는 아래 "수정한 문제" 1번을 본다.

### 2. `wiki/patterns/` 승격을 이번 테스트가 다루지 않았다 (범위 밖)

Scenario F에서 3회차 반복을 확인했지만 L9 승격은 사용자가 명시적으로 요청해야 시작하므로 fixture로 만들지 않았다. L9의 생성 조건 4가지는 문서상으로만 검증됐다.

### 3. 통합 시험이 문서 준수 여부를 검사한다 (한계)

이 테스트는 **문서대로 만든 결과물이 규칙과 일관되는지**를 본다. 에이전트가 실제로 그 문서를 읽고 같은 결과를 내는지는 검증하지 않는다. 그것은 Skills 구현 이후에 가능하다.

## 수정한 문제

### 1. EXM ID를 `<term>` 기반으로 변경 (승인 후 적용)

정식 규칙을 바꿨다.

```text
이전: EXM-<과목 slug>-<연도>-<exam_type>     EXM-general-physics-2-2026-midterm
이후: EXM-<과목 slug>-<term>-<exam_type>     EXM-general-physics-2-2026-2-midterm
```

`<term>`은 대상 CRS의 `term` 값을 그대로 쓴다. 연도만 넣지 않는다.

고친 곳.

| 파일 | 내용 |
|---|---|
| `_system/schemas/common.md` | Type별 권장 형태 표의 exam 행 |
| `_system/schemas/exam.md` | Identity 절. 연도만 쓰면 안 되는 이유와 계절학기·퀴즈 예시 추가 |
| `_system/templates/exam.md` | 상단 주석에 권장 ID 형태 안내 추가 |
| `_system/docs/plan/03-DATA-MODEL.md` | ID 예시 |
| `build_fixtures.py`, `check_scenarios.py` | fixture ID와 압박 테스트 입력 |

**형식 계약(정규식)은 바뀌지 않았다.** `EXM-YYYYMMDD-NN` 같은 기존 ID도 계약을 만족하므로 재발급하지 않는다. 워크플로 문서의 예시 ID(`EXM-20260415-01` 등)도 그대로 두었다.

**RES 정책은 건드리지 않았다.** 이번 변경 범위는 EXM ID뿐이다.

`check_scenarios.py`에 회귀 방지 검사를 넣었다. `common.md`의 exam 행과 `exam.md`의 Identity 절을 직접 읽어 `<연도>` 형태로 되돌아가면 FAIL이 난다.

### 2. `common.md` — Concept slug와 topic 어휘의 과도한 결합

**고치기 전**

> `<topic slug>`와 `<개념 slug>`는 `wiki/clusters/_topics.md`의 어휘와 어긋나지 않게 한다.

이 문장은 모든 CON slug가 등록된 topic이어야 한다는 뜻으로 읽힌다. 하지만 `cluster.md`는 이미 "CLU ID와 topic slug는 서로 다른 식별자"라고 적고 있어 문서끼리 어긋났다.

**고친 뒤**: ID slug와 topic 어휘가 다른 namespace임을 명시했다. `topics` 필드 값만 어휘표에 등록돼 있으면 되고, CON·CLU slug가 topic일 필요도, topic마다 CON·CLU가 있어야 할 필요도 없다.

설계 변경이 아니라 이미 있던 설계 의도를 분명히 한 것이다. 데이터·ID·필드는 바뀌지 않았다.

### 3. `l1-lecture-ingestion.md` — 재개 지점 매핑 부재

Scenario K에서 드러났다. 기존 문서는 "끊긴 단계부터 이어간다"고만 하고 **로그의 어느 코드가 체크리스트의 어느 단계에 대응하는지** 알려주지 않았다. 실행 문서의 빈틈이므로 `## 7. 로그 기록`에 재개 지점 표를 추가했다. 로그 코드 → 끝난 단계 → 재개 지점 → 파일로 확인할 것을 매핑했다. 판단 기준은 그대로 `SECOND-BRAIN.md`에 있다.

### 4. `_topics.md` registry 파싱 위험

`wiki/clusters/_topics.md`는 slug 규칙과 중복 방지 규칙을 불릿으로 설명한다. 그 불릿이 registry 항목과 같은 `- ` 형태라서, 순진하게 `^- `로 뽑는 도구는 **규칙 설명 12줄을 등록된 topic으로 오인**한다.

실제로 `l8-maintenance.md`의 검사 항목 7 명령이 그 형태였다. 두 곳을 고쳤다.

- `wiki/clusters/_topics.md`에 `<!-- REGISTRY:start -->` / `<!-- REGISTRY:end -->` 경계를 넣고, 항목은 그 사이에만 둔다고 명시했다.
- `l8-maintenance.md`의 명령을 SECOND-BRAIN 2.7이 정한 항목 형태(`- <slug> — <정의>`)를 요구하도록 바꿨다.

확인 결과 실제 어휘표를 문서화된 형태로 파싱하면 항목 0개(등록 전이므로 정상), 순진한 파싱으로는 12줄이 잡힌다.

### 5. 검사 스크립트의 오탐 (테스트 도구)

Scenario F가 처음에 FAIL로 나왔으나 fixture가 아니라 검사기 문제였다. `확정` 부분 문자열이 "현재 시험 출제를 **확정하는 근거가 아니다**"라는 부인 문장에 걸렸다. 긍정 예측만 잡도록 고치고, 부인 표시가 **있어야** 통과하도록 조건을 강화했다.

## 보류한 설계 문제

| 문제 | 왜 보류했나 |
|---|---|
| `_system/log.md`가 비어 있음 | append-only 정책상 첫 실제 write에서 첫 줄이 생기는 것이 맞다 |
| `wiki/patterns/` 승격 fixture | L9는 사용자 요청으로만 시작한다 |
| Git 동기화 시험 (plan 09) | 두 대의 기기가 필요해 이 환경에서 재현할 수 없다 |

## 현재 V1 readiness

plan `09-TEST-PLAN.md`의 V1 완료 기준 대비.

| 기준 | 상태 |
|---|---|
| L1 / L2 / L3 정상 | 충족 (Scenario A, B, F) |
| conflict test 정상 | 충족 (Scenario E) |
| protected section 정상 | 충족 (Scenario G, 25개 바이트 동일) |
| evidence recall 정상 | 충족 (Scenario H) |
| duplicate concept / topic 억제 | 충족 (Scenario C, L8) |
| Desktop / Laptop Git sync 정상 | **미검증.** 기기 2대 필요 |

**판정: 설계와 실행 문서가 V1 기준을 만족한다.** 열린 FAIL이 없다. 다만 Git 동기화와 실제 에이전트 실행은 여전히 검증되지 않았다.

## 다음 권장 작업

1. Phase 6 Skills. 이 테스트의 fixture를 스킬 동작의 기대 출력으로 재사용할 수 있다
2. `l8-maintenance.md` 검사 10개의 자동화. `check_scenarios.py`의 탐지 로직이 출발점이 된다
3. Git 동기화 시험 (기기 2대 확보 후)
