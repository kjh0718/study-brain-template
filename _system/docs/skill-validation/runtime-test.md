# Skill Runtime Test

Skill 파일의 **구조**가 아니라 **실제 실행 경로**를 검증한다.

```text
사용자 요청 → Claude Code Skill discovery → Skill 선택 → .claude 스텁
→ .agents canonical → SECOND-BRAIN.md → workflow → schema/template → 결과
```

구조 검사는 [`check_skills.py`](check_skills.py)가, 워크플로 결과의 일관성은
[`integration-test/`](../integration-test/README.md)가 본다. 이 문서는 그 사이를 잇는
**호출 경로가 실제로 동작하는지**를 본다.

> **여기서 만드는 모든 데이터는 가상 테스트 데이터다. 실제 학습 자료가 아니다.**
> 저장소의 실제 `raw/`, `study/`, `wiki/`는 이 테스트가 건드리지 않는다.

## 실행 환경

| | |
|---|---|
| 날짜 | 2026-09-09 (A~F) / 2026-09-12 (G~H 보강) |
| OS | Windows 11 (콘솔 기본 인코딩 cp949) |
| Python | 3.13.3 / PyYAML 6.0.3 |
| baseline | `44a34c9` feat: establish study brain core architecture |
| 대상 | Phase 6 Skill 8개 (미커밋) |

## 실행 방법

```bash
cd _system/docs/skill-validation/runtime
python seed_workspace.py     # ingest 이전 상태로 격리 workspace 생성
# (Skill을 호출해 workspace에서 실행)
python verify_runtime.py     # 결과 검증. FAIL 있으면 exit 1
```

`runtime/workspace/`는 [`integration-test/vault/`](../integration-test/README.md) fixture에서
**ingest 이전 상태만** 가져온다. L1~L5가 만들어야 할 노트는 일부러 비워 두므로 실제로 일이 생긴다.

| seed된 것 | 비워 둔 것 |
|---|---|
| 전사 원본, 기존 공지, CRS(대시보드 빈 상태), 기존 EXM(근거 1개), 기존 FAC(active), 기존 CON-momentum(sources 비움), topic 어휘표(momentum만), 빈 log | LEC, ASM, QST, RES, CON-impulse |

## 발견된 Skills

Claude Code가 실제로 인식한 Skill은 **정확히 8개**다. 중복도, project-brain 전용 Skill도 없다.

```text
capture  recall  maintain  ingest-lecture
ingest-resource  ingest-past-exam  review  check-conflict
```

### 스텁 → canonical 연결

Skill을 호출하면 Claude Code가 `.claude/skills/<name>/`을 base directory로 잡고 스텁을 로드한다.
스텁은 규칙을 담지 않고 정본을 가리킨다. 호출한 8개 Skill 모두 같은 방식으로 동작했다.

```text
Base directory: .claude/skills/recall
→ ".agents/skills/recall/SKILL.md를 읽고 그대로 수행한다"
→ 상대 경로 ../../../.agents/skills/recall/SKILL.md 해석 성공
```

경로 해석은 파일 시스템에서도 확인했다. `.claude/skills/capture/../../../.agents/skills/capture/SKILL.md`가
실재한다.

## 테스트 결과

| 테스트 | 결과 |
|---|---|
| 공통 스키마 적합성 | PASS |
| A capture 라우팅 | PASS |
| B recall / Evidence Recall 분기 | PASS |
| C maintain 읽기 전용 | PASS |
| D ingest-lecture | PASS |
| E check-conflict | PASS |
| F review | PASS |
| G ingest-resource 재등록 | PASS |
| H ingest-past-exam | PASS |

**A~H 모두 PASS / FAIL 0**

위 표는 공통 검사와 A~H를 9행으로 나눠 적었다. `verify_runtime.py`는 B와 F를 한 그룹으로 합쳐 검사하므로 `PASS: 8`로 출력한다. 같은 실행을 세는 기준만 다르며 FAIL은 0이다. 혼동을 줄이기 위해 문서에서는 개수 대신 범위로 적는다.

### A — capture 라우팅

라우팅 표를 파싱해 4개 입력을 각각 매칭했다. 사람 판단이 아니라 표의 결정성을 기계로 확인한 것이다.

| 입력 | 매칭된 Skill |
|---|---|
| "일반물리학2 전체 전사본" | `ingest-lecture` (단독) |
| "교수님이 올린 Chapter 3 PPT" | `ingest-resource` (단독) |
| "2024년 중간고사 족보" | `ingest-past-exam` (단독) |
| "이거 넣어줘" (종류·과목 불명) | **매칭 0개 → 멈추고 질문** |

각 명확한 입력이 정확히 **한 개** Skill에만 매칭된다. 모호한 입력은 어디에도 매칭되지 않아
canonical의 "여기서 멈춘다. 원본만 보존하고 묻는다"로 떨어진다.

### B — recall / Evidence Recall

같은 Skill이 두 질문을 다르게 처리했다.

**Q1 "운동량을 지금까지 어떻게 배웠는지 정리해줘"** — 일반 Recall

`topics` frontmatter로 후보 5개를 좁힌 뒤 그 본문만 열었다. **`raw/`를 열지 않았다.**
`CON-momentum`에 정의와 `sources` 2건이 있어 근거 ID를 붙여 답할 수 있었다.

**Q2 "교수님이 과제 마감에 대해 정확히 뭐라고 했어?"** — Evidence Recall

`ASM.due`가 `null`이라 구조화 노트만으로 확정할 수 없다. 원본 확장 조건에 해당한다.

```text
ASM.sources → LEC-20260908-01 → LEC.source → raw/transcripts/2026-09-08-...md:29
> "HW3는 다음 주까지 제출하세요."  (01:02:15)
```

경로가 구조적으로 이어져 있어 `raw/`를 전수 검색하지 않고 도달했다.

### C — maintain 읽기 전용

"검사해줘"를 검사 모드로 판정하고 L8 검사 항목을 수행했다. 검사한 노트 11개, 발견 0건,
보호 영역 11개 확인, 로그 미기록.

**실행 전후 workspace 전체를 SHA-256으로 비교했다.**

```text
maintain 실행 전 15개 / 후 15개
변경된 파일: 없음
```

파일 하나도 바뀌지 않았다. 검사 모드가 실제로 읽기 전용이다.

### D — ingest-lecture

Scenario A 전사 fixture를 입력으로 L1을 끝까지 수행했다. 결과는 아래를 모두 만족한다.

- **Raw 우선 보존.** 원본 해시가 seed와 동일하다. 이미 있으므로 재복사하지 않았다.
- **Lecture 생성.** `LEC-20260908-01`. 필수 필드 전부, `status: processed`.
- **Professor Emphasis 분리.** 교수 발언 3건에 각각 원본 경로 + 타임스탬프.
- **AI Interpretation 분리.** `## AI 해석 / 검증 필요`에 `(AI 해석)` 표시. 두 절이 섞이지 않았다.
- **주차 추정 안 함.** 원문에 주차 언급이 없어 `week`를 넣지 않고 그 사실을 본문에 적었다.
- **Concept 연결.** 기존 `CON-momentum`을 **새로 만들지 않고 보강**했다. `CON-impulse`는 독립 근거
  2개(LEC, RES)를 확보해 신규 생성. "탄성 충돌"은 1회 등장이라 본문 후보로만 남겼다.
  결과적으로 Concept는 2개다.
- **topic 등록 순서.** `impulse`를 어휘표에 먼저 등록한 뒤 노트에서 사용했다.
- **Assignment.** `due: null`, `due_status: needs-review`, 원문 표현 보존.
- **Exam.** 기존 EXM에 근거를 누적. 새 EXM을 만들지 않았다.
- **Course Fact.** 시험 일정 언급이 추측 표현이라 `value: null`, `needs-review`, `supersedes: []`.
- **Questions.** 학생 질문 2건을 QST로 추출. 원문에 교수 답변이 있어 `answered`까지만 올리고
  `resolved`로 만들지 않았다.
- **Resource 관계.** `Lecture.resources[].pages = "21-38"`과 `Resource.lectures` 양방향 일치.
  원본 파일을 받지 못해 RES는 `needs-review`로 두고 그 사실을 본문에 적었다.
- **Course dashboard.** 자동 관리 영역이 `course` 조회 결과와 정확히 일치.
- **log.** 15줄. 형식 6칸, 작업 코드 전부 승인 목록 안, 결과값 유효.

#### 기존 fixture와의 비교

byte-identical은 아니다. 그럴 필요도 없다. **schema와 핵심 관계는 같다.**

| | integration-test fixture | runtime 결과 | 비고 |
|---|---|---|---|
| LEC ID | `LEC-20260908-01` | 같음 | |
| CON 개수 | 2 | 2 | 기존 보강 1 + 신규 1 |
| ASM `due` / `due_status` | `null` / `needs-review` | 같음 | |
| EXM 개수 | 1 | 1 | 누적, 신규 생성 없음 |
| RES 양방향 | 일치 | 일치 | |
| `week` | 3 | 없음 | **runtime이 더 보수적.** 원문에 근거가 없어 넣지 않았다 |
| RES `status` | `active` | `needs-review` (L1 직후) | **runtime이 더 보수적.** 원본 미확보. 이후 G에서 원본을 받아 `active`로 올렸다 |
| QST `status` | `open` | `answered` | 원문에 교수 답변이 있어 근거를 반영. 둘 다 `resolved`는 아님 |
| PEX 연결 | 3건 | 없음 | runtime workspace에 기출을 넣지 않았다 |

차이 3건은 모두 **입력이 다르거나 runtime이 더 보수적으로 판단한 경우**다. 규칙 위반이 아니다.

### E — check-conflict

두 종류의 충돌을 모두 다뤘다.

**변경 선언 없는 언급** ("중간고사는 아마 10월 중순쯤") — L1이 넘긴 항목

```yaml
status: needs-review
value: null
supersedes: []
```

확정 Fact로 만들지 않았고 기존 FAC를 건드리지 않았으며 EXM의 `date`도 고치지 않았다.

**명시적 변경** ("중간고사 날짜를 10월 17일로 변경합니다")

```yaml
# FAC-general-physics-2-20260901-01 (이전)
status: superseded          # 파일과 ID는 그대로 남음

# FAC-general-physics-2-20260910-01 (신규)
status: active
value: "중간고사 2026-10-17"
supersedes: [FAC-general-physics-2-20260901-01]
```

이어서 `EXM.date`를 `2026-10-17`, `date_status`를 `confirmed`로 갱신했다.
**저장소 전체에 `superseded_by` 필드가 없다.** 단방향 정책이 지켜졌다.

### F — review

두 요청이 서로 다른 `review_type`으로 갈렸다.

| 요청 | `review_type` | `status` | `completed_on` |
|---|---|---|---|
| "이번 주 복습 만들어줘" | `weekly` | `in-progress` | `null` |
| "중간고사 대비 복습 만들어줘" | **`exam-prep`** | `in-progress` | `null` |

- 구 값 `exam`으로 회귀하지 않았다. `review.md`의 허용 값에서 읽었다.
- 문항 10개를 만들었지만 **완료 처리하지 않았다.** 사용자 응답이 없어 `## 응답 / 관찰 결과`는
  전부 `미평가`다. 점수나 이해도를 지어내지 않았다.
- 모든 문항에 `(AI 생성)` 표시가 있다.
- `exam-prep` 회차에서 교수의 출제 명시와 출제 **제외** 명시를 구분해 담고,
  시험 출제를 예측하는 서술을 넣지 않았다.

### G — ingest-resource 재등록

L1이 만든 RES는 원본 파일을 받지 못해 `needs-review`였다. 며칠 뒤 원본 PDF를 확보한 상황을
입력으로 주고 직접 호출했다.

canonical의 첫 단계는 **중복 검색**이다. 검색 결과 같은 자료의 RES가 이미 있었다.

- **새 RES를 만들지 않았다.** `RES-general-physics-2-ch03-slides` ID를 그대로 유지했다.
- 원본을 `raw/resources/`에 보존하고 `source`를 전사 참조에서 실제 파일 경로로 교체했다.
- `page_count: 60` 추가, `status`를 `needs-review` → `active`로 올렸다.
- `## Structure`를 확인된 구성으로 채웠다. 목차로 진도를 추정하지 않았다.
- `## Material Emphasis`(자료 강조)와 `## Professor Emphasis`(교수 발언)를 분리 유지했다.
- `Lecture.resources[]` ↔ `Resource.lectures` 양방향이 그대로 유지됐다.
- RES `status`가 바뀌어 대시보드 표시가 달라지므로 CRS를 갱신했다.
- `concepts`/`questions` 필드를 만들지 않았다. RES 스키마에 없다.

### H — ingest-past-exam

"선배한테 받은 2024-2 중간고사 복원본. 정답도 있는데 누가 푼 건지 모르겠다"를 입력으로 호출했다.

- `provenance: reconstructed`, `authority: student-provided`로 판정했다.
- 문항 번호가 복원본 기준이며 원본 번호와 같은지 확인되지 않았다고 명시했다.
- **제공된 정답과 AI 풀이를 다른 절에 두었다.** AI 계산이 제공된 정답과 일치했지만
  공식 정답으로 확인된 것이 아니므로 `analyzed`로 올리지 않고 `needs-review`를 유지했다.
- `## 출제 경향의 근거`에 **표본 1회차**를 적고 현재 시험 출제를 확정하지 않았다.
- **EXM을 건드리지 않았다.** `## 확정 범위`에 기출이 유입되지 않았다.
- PEX에 `course`가 있어 대시보드를 갱신했다 — 이 과정에서 아래 워크플로 결함을 발견했다.

## 직접 호출과 자동 선택

**직접 호출**: **8개 Skill 전부**를 실제로 호출했다. 전부 스텁이 로드되고 정본을 가리켰다.
`capture`, `ingest-lecture`, `maintain`, `recall`, `check-conflict`, `review`,
`ingest-resource`, `ingest-past-exam`.

**자동 선택**: Claude Code의 Skill 탐색이 8개를 전부 노출하는 것은 확인했고, 각 `description`에
한국어·영어 트리거 문구가 들어 있다. 다만 **자동 선택이 올바른지는 이 테스트로 증명할 수 없다.**
선택하는 주체가 테스트를 수행하는 주체와 같아서 편향이 있다. 대신 라우팅 표의 결정성(테스트 A)을
기계로 검증했다. 독립적인 자동 선택 검증은 별도 세션에서 해야 한다.

## read / write 여부

| Skill | 저장소 쓰기 | 확인 방법 |
|---|---|---|
| `capture` | 분류만. 직접 쓰지 않음 | 라우팅 표 |
| `recall` | **없음** | Q1/Q2 모두 조회만 |
| `maintain` (검사 모드) | **없음** | 전후 해시 15개 전부 동일 |
| `ingest-lecture` | 노트 7개 생성 + 4개 갱신 | log 15줄 |
| `check-conflict` | 노트 2개 생성 + 3개 갱신 | log 6줄 |
| `review` | 노트 2개 생성 | log 4줄 |
| `ingest-resource` | 원본 보존 + 기존 RES 갱신 (**신규 생성 없음**) | log 3줄 |
| `ingest-past-exam` | 노트 1개 생성 + 대시보드 | log 4줄 |

## 발견된 문제

### 1. seed 스크립트 결함 3건 (수정함)

Runtime 결과가 아니라 **테스트 하네스**의 문제다.

- fixture의 `sources: ` 뒤 트레일링 공백 때문에 문자열 치환이 적용되지 않아 EXM이 이미 이번 근거를
  가진 상태로 seed됐다. 정규식으로 바꿨다.
- `CON-momentum`이 이 workspace에 없는 PEX를 참조해 seed 시점부터 끊어진 링크였다.
  `sources: []`로 두고 본문에 사유를 적도록 바꿨다.
- 기존 FAC가 fixture에서 이미 `superseded`라 supersede 전이를 검증할 수 없었다.
  seed에서 `active`로 되돌리도록 바꿨다.

셋 다 고친 뒤 재실행했고, 지금 `seed_workspace.py`는 처음부터 올바른 상태를 만든다.

### 2. L3·L7·L9 워크플로에 대시보드 갱신 단계가 없다 (수정함)

**Runtime Test가 찾아낸 실제 워크플로 결함이다.**

`ingest-past-exam`을 실행하다 발견했다. PEX는 `course` 필드를 가지므로 Course 대시보드 표시가
달라진다. 그런데 `l3-past-exam-ingestion.md`의 실행 체크리스트에 대시보드 갱신 단계가 없었다.

확인해 보니 세 레이어가 같은 결함을 갖고 있었다.

| 워크플로 | 대시보드 언급 | `course`를 가진 노트를 만드는가 |
|---|---|---|
| L1 | 4곳 | 예 |
| L2 | 3곳 | 예 |
| L5 | 2곳 | 예 |
| **L3** | **0곳** | 예 (PEX) |
| **L7** | **0곳** | 예 (REV) |
| **L9** | **0곳** | 예 (중복 정리로 `archived` 전환) |

`SECOND-BRAIN.md` 2.9는 이미 "사용자가 그 레이어를 단독 실행했으면 그 레이어가 갱신까지
마무리한다"고 정하고 있다. 즉 **정본은 요구하는데 실행 문서가 그 단계를 빠뜨린 것**이다.
정책 변경이 아니라 문서가 정본에 맞지 않은 경우여서, 세 문서에 갱신 단계를 각각 추가했다.

`verify_runtime.py`에 회귀 방지 검사를 넣었다. 세 워크플로에서 대시보드 언급이 사라지면 FAIL이다.

### 3. 자동 선택 검증 불가 (한계)

위 "직접 호출과 자동 선택" 참조. 설계 결함이 아니라 테스트 방법의 한계다.

### 4. Skill spec 결함 없음

호출한 8개 Skill 모두 지시대로 따라갈 수 있었다. 링크 오류, 잘못된 매핑, 스텁 포인터 오류,
트리거 오타를 발견하지 못했다. workflow·schema를 고쳐야 할 일도 없었다.

## 수정한 문제

- `seed_workspace.py`의 결함 3건 (위 1번)
- L3·L7·L9 워크플로의 대시보드 갱신 단계 누락 (위 2번)

Skill과 schema는 고치지 않았다.

## 남은 문제

| 문제 | 상태 |
|---|---|
| 자동 Skill 선택의 독립 검증 | 별도 세션 필요 |
| L4 / L9 Skill 부재 | 요청 범위 밖. 다음 단계 후보 |
| Hooks | 이번 범위 밖 |

## 검증기 자체 검증

`verify_runtime.py`는 결함 주입으로 확인했다. 아래를 각각 심었을 때 모두 exit 1로 탐지하고
복원하면 exit 0으로 돌아온다.

| 심은 결함 | 탐지 |
|---|---|
| 모호한 마감을 날짜로 확정 | 예 |
| 추측 표현을 확정 Fact로 | 예 |
| 변경 선언 없이 supersede 적용 | 예 |
| 교수 발언 절에 AI 해석 섞기 | 예 |
| raw 원본 변조 | 예 |
| EXM 근거 누적 취소 | 예 |
| 대시보드 한 줄 누락 | 예 |
| 미등록 topic 사용 | 예 |
| 이전 FAC를 active로 방치 | 예 |
| `supersedes` 비우기 | 예 |
| EXM date 미반영 | 예 |
| `superseded_by` 필드 추가 | 예 |
| 응답 없는데 completed | 예 |
| 구 값 `exam`으로 회귀 | 예 |
| 시험 출제 예측 삽입 | 예 |
| AI 생성 표시 제거 | 예 |

16건 전부 탐지했다.
