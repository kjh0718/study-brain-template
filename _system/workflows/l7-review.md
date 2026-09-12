# L7 — Review 실행 문서

대응 레이어: **L7**. 판단 기준의 정본은 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)의 `L7 — Review` 절이고, 데이터 규격은 [`review.md`](../schemas/review.md)다.

> 이 문서는 실행 보조 문서다. 규칙을 새로 만들지 않고 검색 명령, 체크리스트, 보고·로그 형식, 실행 예시만 담는다. 이 문서와 SECOND-BRAIN.md가 다르면 SECOND-BRAIN.md가 맞고 이 문서를 고친다.

## 한눈에 보기

| 항목 | 값 |
|---|---|
| 목적 | 복습 회차 **하나**를 계획하고 수행하고 기록한다 |
| 입력 | 복습 요청(daily, weekly, exam-prep, concept, custom) 또는 기존 REV 이어하기 |
| 저장소 쓰기 | 예 |
| 호출할 수 있는 레이어 | **없다.** 사용자 요청으로만 시작한다 |
| 주 생성물 | REV. 필요하면 QST |

L7이 만드는 질문 노트는 **L4를 호출하지 않고 L7이 직접 처리한다.** 다만 연결 필드는 [L4](l4-knowledge-extraction.md)의 역방향 연결표를 그대로 따른다.

`review_type`은 `daily`, `weekly`, `exam-prep`, `concept`, `custom` 중 하나다. `exam-prep`은 시험 **대비** 회차이며 시험 후 분석이 아니다.

## 0. 시작 전 확인

- [ ] 복습 대상 노트가 존재한다.
- [ ] **새 회차인지 기존 회차의 연속인지 확정할 수 있다.** 확정할 수 없으면 아무것도 만들거나 되돌리지 않고 회차 확인만 요청한다.

## 1. 검색 방법

공통 명령은 [`README.md`](README.md)에 있다.

**같은 회차 후보인 기존 REV 찾기** — 검색 키는 회차 + 날짜.

```bash
rg -n "^(id|title|course|review_type|status|scheduled_on|completed_on|next_review):" study/reviews -g "*.md"
```

**복습 대상 모으기** — `review_type`에 따라 다르다.

```bash
# daily / weekly: 기간 내 강의
rg -n "^(id|title|date|course):" study/lectures -g "*.md"

# concept: 대상 개념과 그 근거
rg -n "^(id|title|status):" wiki/concepts -g "*.md"

# exam-prep: 시험 범위 + 근거
rg -n "^(id|title|course|exam_type|date|scope_status):" study/exams -g "*.md"
```

**exam-prep 복습의 입력 모으기** — 아래를 함께 읽는다.

```text
LEC(교수님 강조 포함) + EXM + CON + PEX + ASM + 열린 QST
```

```bash
rg -ln "^course: CRS-20260908-01" study wiki -g "*.md"
rg -n "^(id|title|status|question_type):" study/questions -g "*.md"
```

**열린 질문만 추리기**

```bash
rg -ln "^status: (open|investigating|answered)" study/questions -g "*.md"
```

읽는 범위는 대상 LEC·CON·EXM·PEX·QST와 같은 회차 후보인 기존 REV까지다.

## 2. 실행 체크리스트

- [ ] **1. 회차 판정.** 아래 판정표를 쓴다. **가장 먼저 한다.**
- [ ] **2. `targets` 확정.** 실제 복습을 시작할 때는 **하나 이상**이어야 한다. 계획 초안에서는 `[]`를 허용한다.
- [ ] **3. 복습 질문 생성.** **AI가 생성했음을 표시한다.**
- [ ] **4. 사용자 응답 기록.** 응답이 없는 항목은 **미평가로 표시**하고 점수나 이해도를 추정하지 않는다.
- [ ] **5. 오개념·미해결 질문 정리.** QST 생성·갱신은 L7이 직접 한다. 해결 처리는 아래 표를 따른다.
- [ ] **6. 완료 처리.** 실제 수행 근거와 `completed_on`이 있을 때만 `completed`로 바꾼다.
- [ ] **7. `next_review` 기록.** 계획값이다.
- [ ] **8. 대시보드 갱신.** REV에 `course`가 있으면 그 CRS의 표시가 달라진다. 회차 상태가 바뀐 경우도 포함한다. 표시가 실제로 달라지는 CRS만 갱신한다. 판정과 정렬 규칙은 SECOND-BRAIN.md의 Course 대시보드 절을 따른다.
- [ ] **9. 로그 기록.**

### 1단계 회차 판정표

| 상황 | 처리 |
|---|---|
| 같은 계획을 이어서 수행 | 기존 REV를 갱신한다 |
| 다른 날짜에 새로 복습 | 새 REV를 만든다. **이전 REV는 그대로 둔다** |
| 완료 처리가 잘못됐거나 같은 회차의 미완 부분을 다시 수행 | 재개. `status: in-progress`, `completed_on: null`로 되돌린다. **이전 완료일과 결과는 본문에 남긴다** |
| 어느 쪽인지 불명확 | **새 REV를 만들지도, 기존 REV를 되돌리지도 않는다.** 기존 기록과 `completed_on`을 그대로 둔 채 회차만 확인 요청 |

네 번째가 중요하다. 같은 요청을 다시 보냈다는 이유로 새 회차가 생기지 않게 한다.

### 5단계 질문 해결 처리

**질문 종류에 따라 해결 조건이 다르다.**

| `question_type` | 해결 조건 |
|---|---|
| `conceptual`, `clarification`, `problem-solving` | 사용자가 이해를 확인하면 `resolved`. `resolved_on`과 확인 내용을 적는다 |
| `source-verification` | **사용자 확인만으로 해결하지 않는다.** 확인 가능한 근거를 `answer_sources` 또는 본문의 원문 위치로 기록한 뒤에 해결한다 |

### 본문 채우기

[`review.md`](../schemas/review.md)의 Body Structure를 따른다.

| 절 | 넣는 것 | 주의 |
|---|---|---|
| `## 복습 목표 / 대상` | 이번 회차의 범위 | `targets`와 일치시킨다 |
| `## Recall` | 기억을 꺼내는 문항 | **AI 생성 표시** |
| `## Understanding` | 이해를 확인하는 문항 | 같음 |
| `## Application` | 적용·응용 문항 | 같음 |
| `## 응답 / 관찰 결과` | 사용자 응답과 관찰 | 응답 없으면 `미평가` |
| `## 오개념 / 미해결 질문` | 확인된 오개념과 QST 링크 | |
| `## 다음 행동` | 다음에 할 것 | `next_review`가 계획값임을 적는다 |
| `## Personal Reflection` | — | **비운 채 둔다** |

`exam-prep` 복습이면 문항 절에 다음을 구분해 담는다. 범위 핵심, 교수 강조, 암기와 이해의 구분, 미해결 질문, 반복 확인된 기출 유형, 주의할 오개념.

## 3. 사용자 확인이 필요한 지점

| 상황 | 처리 |
|---|---|
| 회차를 확정할 수 없음 | REV를 만들지도 고치지도 않고 회차 확인만 요청 |
| 사용자 응답이 없음 | `in-progress` 유지. `completed`로 올리지 않는다 |
| 대상이 하나도 없음 | **시작하지 않는다** |
| `source-verification` 질문의 근거를 못 찾음 | `resolved`로 올리지 않는다 |

## 4. 하지 않는 것

- **질문을 만든 것만으로 완료 처리하지 않는다.** 이것이 L7의 대표적 실패다.
- 사용자 응답이 없는 항목에 점수나 이해도를 추정해 넣지 않는다.
- 실제 수행 근거 없이 `completed`로 바꾸지 않는다.
- 같은 요청을 다시 받았다는 이유로 새 회차를 만들지 않는다.
- 완료된 REV를 `archived`로 바꿀 때 `completed_on`과 결과 기록을 지우지 않는다.
- LEC·CON의 내용을 고치지 않는다. L7은 학습 상태를 기록하지 지식을 다시 쓰지 않는다.
- `## Personal Reflection`을 쓰거나 고치지 않는다.
- 복습 문항마다 QST나 REV를 자동 생성하지 않는다.
- 과거 기출 빈도를 근거로 "이번 시험에 나온다"라고 쓰지 않는다.
- 다른 레이어를 호출하지 않는다. L4도 호출하지 않는다.
- `next_review`를 적었다고 해서 알림이 설정됐다고 말하지 않는다. **계획값일 뿐이다.**

## 5. 완료 조건

- [ ] 상태와 날짜 필드가 실제 수행과 일치한다.
- [ ] 미응답 항목이 미평가로 표시돼 있다.
- [ ] `targets`의 ID가 모두 실제로 존재한다. (C4)
- [ ] AI가 생성한 문항이 그렇게 표시돼 있다.
- [ ] 로그를 기록했다.

## 6. 완료 보고 형식

```text
L7 Review 완료

- Review: REV-20260913-01 (신규) / review_type: weekly
- 회차 판정: 신규 회차 (2026-09-13. 직전 회차 REV-20260906-01은 completed 유지)
- targets: LEC-20260908-01, LEC-20260910-01, CON-20260415-01, CON-20260908-01
- 생성 문항: Recall 5, Understanding 3, Application 2 (모두 AI 생성 표시)
- 사용자 응답: 7 / 10
- 미평가: 3 (Application 2, Understanding 1) — 점수 추정하지 않음
- 오개념: 1 (충돌에서 운동에너지 보존으로 오해)
- QST 처리:
  - QST-20260913-01 신규 (conceptual)
  - QST-20260908-02 → resolved (사용자가 이해 확인, resolved_on 2026-09-13)
  - QST-20260908-03 → open 유지 (source-verification. 원문 근거 미확보로 해결하지 않음)
- status: in-progress (미응답 3건 남음)
- completed_on: null
- next_review: 2026-09-20 (계획값. 알림 자동화 아님)
- 로그: 4줄
```

## 7. 로그 기록

```text
- 2026-09-13 20:05 | L7 | create-note | REV-20260913-01 | done | 주간 복습. targets 4
- 2026-09-13 20:40 | L7 | record-review | REV-20260913-01 | partial | 응답 7/10. 미평가 3. in-progress 유지
- 2026-09-13 20:42 | L7 | update-note | QST-20260908-02 | done | 사용자 이해 확인으로 resolved
- 2026-09-13 20:43 | L7 | create-note | QST-20260913-01 | done | 충돌 시 운동에너지 오개념
```

`record-review`는 복습 회차의 수행·응답·완료를 기록할 때 쓴다. 회차를 재개했으면 메모에 이전 `completed_on`을 적는다.

## 8. 실행 예시

### 예시 A — 완료로 올리면 안 되는 경우

> 이번 주 복습 문제 만들어줘

1. 회차 판정: 이번 주 REV 없음 → 신규 `REV-20260913-01`.
2. `targets` 확정, 문항 10개 생성.
3. **여기서 멈춘다.** 사용자가 아직 아무 답도 하지 않았다.

```yaml
status: in-progress   # planned에서 시작해 문항이 준비되면 in-progress
completed_on: null
```

`## 응답 / 관찰 결과`에는 `미평가`만 적는다. **문항을 만들었다는 이유로 `completed`로 올리지 않는다.**

### 예시 B — 회차가 불명확한 경우

`REV-20260913-01`이 `completed`, `completed_on: 2026-09-13`인데 사용자가 다시 말한다.

> 주간 복습 하자

- 같은 회차를 보완하려는 것인지, 새 주의 복습인지 알 수 없다.
- **새 REV를 만들지 않는다. `completed_on`을 `null`로 되돌리지도 않는다.**
- 이렇게 묻는다.

  ```text
  9/13 주간 복습(REV-20260913-01)이 completed로 기록돼 있다.
  - 그 회차의 남은 부분을 이어서 하려는 것인가 (재개)
  - 이번 주 새 회차를 시작하려는 것인가 (신규)
  확인 전까지 아무것도 만들거나 되돌리지 않았다.
  ```

### 예시 C — 두 종류의 질문을 다르게 처리

복습 중 두 질문이 나왔다.

**QST-A** (`conceptual`) — "충돌에서 운동에너지가 왜 보존되지 않는가"

사용자가 설명을 듣고 이해했다고 답했다.

```yaml
status: resolved
resolved_on: 2026-09-13
```

`## 해결 근거`에 사용자가 확인한 내용을 적는다.

**QST-B** (`source-verification`) — "교수님이 3장 전체를 시험 범위라고 했는가"

사용자가 "맞을 거야"라고 답했다.

```yaml
status: open      # resolved로 올리지 않는다
answer_sources: []
```

`## 남은 확인`에 적는다.

```markdown
## 남은 확인

사용자 기억으로는 3장 전체이나 원문 근거를 찾지 못했다.
raw/transcripts/의 해당 수업 전사에서 시험 범위 발언을 확인해야 한다.
사용자 확인만으로 해결하지 않았다.
```

**사실을 확인하는 질문은 사용자의 기억만으로 닫지 않는다.**
