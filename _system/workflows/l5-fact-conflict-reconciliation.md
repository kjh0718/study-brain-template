# L5 — Fact and conflict reconciliation 실행 문서

대응 레이어: **L5**. 판단 기준의 정본은 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)의 `L5 — Fact and conflict reconciliation` 절이고, 데이터 규격은 [`assignment.md`](../schemas/assignment.md), [`exam.md`](../schemas/exam.md), [`course-fact.md`](../schemas/course-fact.md)다.

> 이 문서는 실행 보조 문서다. 규칙을 새로 만들지 않고 검색 명령, 체크리스트, 보고·로그 형식, 실행 예시만 담는다. 이 문서와 SECOND-BRAIN.md가 다르면 SECOND-BRAIN.md가 맞고 이 문서를 고친다.

## 한눈에 보기

| 항목 | 값 |
|---|---|
| 목적 | 과제(ASM), 시험(EXM), 운영 사실(FAC)의 생성과 충돌 조정 |
| 입력 | L1이 넘긴 공지·마감·시험 언급. 사용자 입력. LMS 공지 원본 |
| 저장소 쓰기 | 예 |
| 호출할 수 있는 레이어 | **없다.** 특히 **L5는 L1을 호출하지 않는다** |
| 주 생성물 | ASM, EXM, FAC |

개념·질문은 [L4](l4-knowledge-extraction.md)의 책임이다. L5는 CON·QST를 만들거나 고치지 않는다.

L5는 L1이 호출하거나 사용자가 직접 실행한다. **L2와 L3은 과제·시험·운영 사실을 발견해도 L5를 호출하지 않는다.**

## 0. 시작 전 확인

- [ ] 근거 노트 또는 원본 경로가 있다.
- [ ] 대상 CRS가 확정됐다. 없고 식별이 충분하면 SECOND-BRAIN.md의 `공통 준비 절차 — 대상 Course 확보`를 수행한다.
- [ ] 과목이 불명확하면 **처리하지 않고 보류한다.**

## 1. 검색 방법

공통 명령은 [`README.md`](README.md)에 있다.

**기존 ASM 찾기** — 검색 키는 course + 과제 번호·요구사항.

```bash
rg -n "^(id|title|course|due|due_status|status):" study/assignments -g "*.md"
```

**기존 EXM 찾기** — 검색 키는 course + `exam_type` + 회차. **Lecture마다 새 EXM을 만들지 않는다.**

```bash
rg -n "^(id|title|course|exam_type|date|date_status|scope_status|status):" study/exams -g "*.md"
```

**기존 FAC 찾기** — 검색 키는 course + `subject` + 세부 사실 + 적용 기간. `fact_type`만으로 중복을 판단하지 않는다.

```bash
rg -n "^(id|title|course|fact_type|subject|value|status|effective_from):" study/course-facts -g "*.md"
```

**supersede 사슬 확인** — 이 사실을 이미 대체한 FAC가 있는지 본다.

```bash
rg -n -A3 "^supersedes:" study/course-facts -g "*.md"
rg -ln "FAC-20260908-01" study/course-facts -g "*.md"
```

읽는 범위는 근거 노트의 해당 부분, 같은 course의 기존 ASM·EXM·FAC, 관련 원본까지다.

## 2. 실행 체크리스트

- [ ] **1. 항목 단위로 분해.** 마감 하나, 시험 하나가 각각 별개 항목이다.
- [ ] **2. 대상 타입 결정.** 과제 → ASM, 시험 → EXM, 그 밖의 운영 사실과 **변경** → FAC.
- [ ] **3. 기존 노트 검색.** 같은 항목이면 근거를 누적한다.
- [ ] **4. 충돌 판정.** 아래 판정표를 쓴다.
- [ ] **5. 모호한 표현 처리.** 아래 표현별 처리표를 쓴다.
- [ ] **6. `confirmed` 확인.** 값과 근거가 **모두** 있을 때만 쓴다. 날짜만 알면 날짜만 적고 시각을 임의로 넣지 않는다.
- [ ] **7. 대시보드.** 표시가 달라지는 CRS를 정리한다. 부모 L1이 있으면 목록만 돌려주고, 단독 실행이면 직접 갱신한다.
- [ ] **8. 로그 기록.**

### 4단계 충돌 판정표

| 판정 | 조건 | 처리 |
|---|---|---|
| **동일** | 같은 항목, 같은 값 | 기존 노트에 `sources`만 누적한다. 값은 바꾸지 않는다 |
| **명시적 변경** | 원문이 이전 내용을 **바꾼다고 말하고**, 발화 권한과 적용 범위가 확인됨 | 새 FAC 생성 → 이전 FAC `status: superseded` → 새 FAC `supersedes: [이전 ID]` → 같은 근거로 대상 ASM·EXM 갱신 |
| **불명확한 상충** | 어느 쪽이 유효한지 확인 불가 | **자동 덮어쓰기 금지.** 양쪽 근거를 모두 남기고 FAC를 `needs-review`로 둔다. 대상의 상태 필드도 `needs-review`로 바꾼다 |

**나중에 나온 발언이라는 이유만으로 자동 채택하지 않는다.** 이것이 L5의 핵심이다.

### 충돌 종류별 표시 필드

**한 필드로 세 가지를 뭉뚱그리지 않는다.**

| 충돌 종류 | 필드 | 허용 값 |
|---|---|---|
| 과제 마감 | `ASM.due_status` | `unknown`, `needs-review`, `confirmed` |
| 시험 일정 | `EXM.date_status` | 스키마의 허용 값 |
| 시험 범위 | `EXM.scope_status` | 스키마의 허용 값 |
| 운영 사실 전반 | `FAC.status` | `needs-review` |

### 5단계 모호한 표현 처리표

| 원문 표현 | `due` / `date` | 상태 필드 | 본문 |
|---|---|---|---|
| "다음 주까지" | `null` | `needs-review` | 원문 표현 그대로 기록 |
| "다음 수업 전까지" | `null` | `needs-review` | 같음 |
| "10월 중순쯤" | `null` | `needs-review` | 같음 |
| 마감 언급 자체가 없음 | `null` | `unknown` | 언급 없음이라고 기록 |
| "10월 17일 23:59" (시간대 확인됨) | 시간대 포함 ISO 8601 | `confirmed` | 근거 위치 기록 |
| "10월 17일" (시각 미확인) | `2026-10-17` | `confirmed` | 시각 미확인이라고 기록 |

`needs-review`와 `unknown`은 다르다. **모호한 언급이 있었으면 `needs-review`, 언급 자체가 없었으면 `unknown`이다.**

### 경계 사례

- **이전 FAC가 없는데 명시적 변경이 들어온 경우.** 과거 FAC를 지어내지 않는다. 새 FAC의 `supersedes`는 `[]`로 두고, 기존 EXM·ASM에 있던 값과 이번 근거를 새 FAC의 `## 변경 이력`에 적은 뒤 대상 EXM·ASM을 갱신한다.
- **과거 기출의 일정·범위를 현재 과목의 확정 운영 사실로 옮기지 않는다.** PEX의 일정은 출제 경향의 근거이지 이번 학기 공지가 아니다.
- **L2·L3이 남긴 운영 후보는 자동 처리하지 않는다.** 그 후보는 RES 본문의 `## Exam References`·`## Assignment References`, PEX 본문의 자료 식별 절에 있다. 사용자가 그 자료를 다시 다루거나 같은 과목의 L1·L5를 실행할 때 후보 목록을 제시하고 **처리할지 묻는다.** 묻지 않고 만들지 않는다.

## 3. 사용자 확인이 필요한 지점

| 상황 | 처리 |
|---|---|
| 명시적 변경인지 불명확 | 자동 supersede 금지. 양쪽 근거 보존 + `needs-review` |
| 발화 권한·적용 범위 불명 | FAC를 `needs-review`로 두고 **대상 ASM·EXM은 고치지 않는다** |
| 시간대를 모름 | 날짜만 기록하고 확인 필요로 남긴다 |
| 과목이 불명확 | 처리하지 않고 보류 |
| L2·L3이 남긴 운영 후보 | 후보 목록을 제시하고 처리 여부를 묻는다 |

항목 하나가 보류돼도 다른 항목과 L1의 강의 요약은 계속한다. **모호한 마감 하나 때문에 전체 처리를 중지하지 않는다.**

## 4. 하지 않는 것

- 모호한 표현을 임의의 `YYYY-MM-DD`로 바꾸지 않는다.
- 불명확한 상충에서 한쪽을 자동으로 고르지 않는다. 최신 발언이라는 이유도 근거가 아니다.
- **과거 FAC를 삭제하지 않는다.** `superseded`로 표시하고 사슬을 남긴다.
- 이미 `superseded`가 된 FAC를 되살리거나 고치지 않는다.
- Lecture마다 새 EXM을 만들지 않는다. 기존 EXM에 근거를 누적한다.
- quiz 여러 회를 하나의 EXM으로 합치지 않는다.
- CON·QST를 만들거나 고치지 않는다. 어떤 레이어도 호출하지 않는다.
- 교수의 시험 출제 명시, 일반 강조, 자료의 별표, 족보 빈도, AI 판단을 섞지 않는다. `EXM`의 `## 확정 범위`는 교수의 명시적 공지로만 채우고, AI 추정은 `## AI 예상 / 검증 필요`에만 넣는다.
- `supersedes`에 자기 자신이나 순환을 만들지 않는다.
- 보호 영역을 고치지 않는다.

## 5. 완료 조건

- [ ] 각 사실 항목이 노트 하나에 대응하고 근거가 연결됐다.
- [ ] 미확정 항목이 **해당 필드의** 미확정 값으로 명시됐다. 서로 다른 필드의 값을 섞어 쓰지 않았다.
- [ ] 명시적 변경일 때 이전 FAC가 있었으면 `supersedes`로 이어져 있고, 없었으면 `supersedes: []`이며 기존 값이 `## 변경 이력`에 적혀 있다.
- [ ] `supersedes`에 자기 참조나 순환이 없다.
- [ ] 로그를 기록했다.

## 6. 완료 보고 형식

```text
L5 Fact reconciliation 완료

- 근거: LEC-20260908-01 (raw/transcripts/2026-09-08-physics-01.md)
- 분해한 항목: 3

[1] 과제 HW3 → ASM-20260908-01 (신규) / status: open
    원문: "다음 주까지 HW3 제출하세요"
    due: null / due_status: needs-review  ← 날짜 추정하지 않음

[2] 중간고사 언급 → EXM-20260415-01 (기존 갱신)
    새 EXM을 만들지 않고 sources에 LEC-20260908-01 추가
    date_status: confirmed (변경 없음) / scope_status: needs-review

[3] 시험 일정 변경 → 명시적 변경
    FAC-20260415-03 (10/15) → status: superseded
    FAC-20260908-01 (10/17) → status: active, supersedes: [FAC-20260415-03]
    EXM-20260415-01.date: 2026-10-15 → 2026-10-17
    근거: "10월 15일이 아니라 10월 17일로 변경합니다" (00:12:40)

- 대시보드: CRS-20260908-01 (부모 L1에 반환)
- 보류: [1] 마감 표현 모호. 정확한 날짜를 알려주면 확정한다
- 충돌: 없음 (명시적 변경으로 판정)
- 로그: 5줄
```

## 7. 로그 기록

```text
- 2026-09-08 18:44 | L5 | reconcile-fact | ASM-20260908-01 | held | HW3 마감 "다음 주까지" 모호. due null 유지
- 2026-09-08 18:44 | L5 | reconcile-fact | EXM-20260415-01 | done | 중간고사 근거 누적. 신규 생성 안 함
- 2026-09-08 18:45 | L5 | reconcile-fact | FAC-20260415-03 | done | 명시적 변경으로 superseded
- 2026-09-08 18:45 | L5 | create-note | FAC-20260908-01 | done | 중간고사 10/17. supersedes FAC-20260415-03
- 2026-09-08 18:46 | L5 | update-note | EXM-20260415-01 | done | date 10-15 -> 10-17
```

불명확한 상충으로 보류했으면 결과값을 `conflict`로 남긴다.

```text
- 2026-09-08 18:45 | L5 | reconcile-fact | EXM-20260415-01 | conflict | 10/15 vs 10/17 변경 여부 불명. 양쪽 근거 보존, date_status needs-review
```

## 8. 실행 예시

### 예시 A — 명시적 변경 (supersede 가능)

기존: `FAC-20260415-03` — 중간고사 10월 15일, `status: active`
전사: **"중간고사는 10월 15일이 아니라 10월 17일로 변경합니다"**

원문이 이전 내용을 바꾼다고 말했고, 교수 발언이며, 이번 학기 이 과목에 적용된다. → **명시적 변경**

```yaml
# FAC-20260415-03 (이전)
status: superseded

# FAC-20260908-01 (신규)
status: active
fact_type: schedule
subject: EXM-20260415-01
value: "중간고사 2026-10-17"
authority: professor
supersedes:
  - FAC-20260415-03
sources:
  - LEC-20260908-01
```

이어서 `EXM-20260415-01.date`를 `2026-10-17`로 갱신한다. **이전 FAC 파일을 지우지 않는다.**

### 예시 B — 불명확한 상충 (supersede 금지)

기존: `FAC-20260415-03` — 중간고사 10월 15일
전사: **"시험은 10월 17일쯤 볼 것 같아요"**

변경한다고 말하지 않았고, 표현도 확정적이지 않다. → **불명확한 상충**

```yaml
# FAC-20260415-03 — 그대로 둔다. superseded로 바꾸지 않는다.
status: needs-review

# EXM-20260415-01
date: 2026-10-15        # 기존 값을 지우지 않는다
date_status: needs-review
```

`FAC`의 `## 충돌 / 확인 필요`에 양쪽 근거를 적는다.

```markdown
## 충돌 / 확인 필요

- 기존: 2026-10-15 (FAC-20260415-03, LMS 공지)
- 신규: "10월 17일쯤" (LEC-20260908-01, 00:12:40) — 확정 표현 아님
- 어느 쪽이 유효한지 확인되지 않았다. 자동 채택하지 않았다.
```

사용자에게 어느 쪽이 맞는지 묻는다. 나중 발언이라는 이유로 10/17을 고르지 않는다.

### 예시 C — 이전 FAC가 없는 명시적 변경

`EXM-20260415-01.date`가 `2026-10-15`인데 그 값의 근거가 FAC로 기록돼 있지 않다. 이때 "10월 17일로 변경합니다"가 들어왔다.

- **`FAC-20260415-03`을 지어내지 않는다.**
- 새 `FAC-20260908-01`을 만들되 `supersedes: []`로 둔다.
- `## 변경 이력`에 적는다.

  ```markdown
  ## 변경 이력

  - 이전 값: 2026-10-15 (EXM-20260415-01에 기록돼 있었으나 대응 FAC 없음)
  - 변경 후: 2026-10-17
  - 근거: LEC-20260908-01, 00:12:40 교수 발언
  ```

- 그 뒤 `EXM-20260415-01.date`를 갱신한다.
