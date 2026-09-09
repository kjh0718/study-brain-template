# L4 — Knowledge extraction 실행 문서

대응 레이어: **L4**. 판단 기준의 정본은 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)의 `L4 — Knowledge extraction` 절이고, 데이터 규격은 [`concept.md`](../schemas/concept.md), [`question.md`](../schemas/question.md), [`cluster.md`](../schemas/cluster.md)다.

> 이 문서는 실행 보조 문서다. 규칙을 새로 만들지 않고 검색 명령, 체크리스트, 보고·로그 형식, 실행 예시만 담는다. 이 문서와 SECOND-BRAIN.md가 다르면 SECOND-BRAIN.md가 맞고 이 문서를 고친다.

## 한눈에 보기

| 항목 | 값 |
|---|---|
| 목적 | 개념(CON)과 질문(QST)만 담당한다 |
| 입력 | L1·L2·L3이 넘긴 후보. 또는 사용자의 직접 요청 |
| 저장소 쓰기 | 예 |
| 호출할 수 있는 레이어 | **없다.** L4는 다른 레이어를 호출하지 않는다 |
| 주 생성물 | CON, QST. 조건을 충족하면 CLU |

**과제·시험·운영 사실은 [L5](l5-fact-conflict-reconciliation.md)의 책임이다.** L4는 ASM·EXM·FAC를 만들거나 고치지 않는다.

## 0. 시작 전 확인

- [ ] 근거가 되는 노트(LEC, RES, PEX)가 **이미 존재한다.** 근거 노트 없이 개념만 만들지 않는다.
- [ ] 후보가 대상별로 모여 있다. 같은 CON을 근거 A로 한 번, B로 다시 한 번 열지 않고 A와 B를 함께 반영한다.

## 1. 검색 방법

공통 명령은 [`README.md`](README.md)에 있다.

**기존 CON 찾기 (가장 중요)** — 검색 키는 title + aliases + 본문 의미다. **표기가 달라도 같은 개념이면 하나로 연결한다.**

```bash
rg -n "^(id|title|status):" wiki/concepts -g "*.md"
rg -n -A3 "^aliases:" wiki/concepts -g "*.md"
```

한국어·영어·약칭이 섞이므로 표기별로 여러 번 찾는다.

```bash
rg -lni "운동량|momentum|linear momentum" wiki/concepts -g "*.md"
```

**열린 QST 찾기** — 같은 의미·같은 맥락의 질문이 이미 있는지 본다.

```bash
rg -n "^(id|title|status|question_type|course):" study/questions -g "*.md"
```

**topic 어휘표 조회** — C5.

```bash
rg -n "^- " wiki/clusters/_topics.md
```

**이 topic에 걸린 CLU 찾기**

```bash
rg -n "^(id|title|topics|members):" wiki/clusters -g "*.md"
```

읽는 범위는 근거 노트의 **해당 부분**, `wiki/concepts/`의 title과 aliases 목록, 열린 QST 목록, 어휘표까지다. 전체 본문 스캔은 하지 않는다.

## 2. 실행 체크리스트

- [ ] **1. 후보 정리.** 대상별로 묶는다.
- [ ] **2. 기존 CON 검색.** title, aliases, 본문 의미를 함께 본다.
- [ ] **3. 있으면 보강.** `sources`에 근거 노트 ID를 추가하고 설명을 덧붙인다. **새로 만들지 않는다.**
- [ ] **4. 없으면 생성 여부 판단.** 아래 승격 기준표를 쓴다.
- [ ] **5. 질문 처리.** 같은 의미·맥락의 열린 QST가 있으면 갱신하고, 없으면 생성한다.
- [ ] **6. 정방향 관계 기록.** CON·QST의 `sources`에 실제 근거 노트 ID를 넣는다. **이 방향이 관계의 정본이다.**
- [ ] **7. 역방향 관계 기록.** 아래 역방향 연결표의 수단만 쓴다.
- [ ] **8. topics 처리.** 어휘표에 없으면 최초 등록 절차를 먼저 수행한 뒤에 쓴다. 순서를 뒤집지 않는다.
- [ ] **9. CLU 갱신.** 이번 입력의 topics가 **실제로 영향을 주는** CLU만 갱신한다.
- [ ] **10. 로그 기록.**

### 새 CON 승격 기준

4단계에서 쓴다. 아래 중 **하나 이상을 충족하고 그 근거를 본문에 적을 수 있어야** 만든다.

| 기준 | 확인 방법 |
|---|---|
| 서로 다른 근거 노트 **둘 이상**에서 반복 등장 | `sources`에 들어갈 ID가 2개 이상인가 |
| 해당 수업에서 **핵심 개념으로 명시**됨 | 근거 노트의 교수 발언 절에 근거가 있는가 |
| 다른 개념 설명에 반복 인용될 **독립적 설명 가치**가 있음 | 정의를 따로 쓸 만한가 |

**단순 용어가 한 번 나온 것만으로는 만들지 않는다.** 근거 노트 본문에 후보로만 남긴다. 용어가 등장했다는 이유로 수십 개 CON을 만드는 것이 이 레이어의 대표적 실패다.

### 역방향 연결표

근거 노트마다 쓸 수 있는 수단이 다르다. **표에 없는 필드를 새로 만들지 않는다.**

이 표의 정본은 SECOND-BRAIN.md의 L4 7단계다. 실행 중에 보기 위해 옮겨 둔 것이므로, 두 표가 달라지면 SECOND-BRAIN.md가 맞고 여기를 고친다.

| 근거 노트 | 개념 연결 | 질문 연결 |
|---|---|---|
| LEC | `concepts` | `questions` |
| PEX | `concepts` | `related` + 본문 |
| RES | `related` + 본문 `## Key Concepts` | `related` + 본문 |
| 그 밖의 타입 | `related` + 본문 | `related` + 본문 |

- **RES에 `concepts`나 `questions`를 추가하지 않는다.** RES 스키마에 그 필드가 없다.
- 전용 필드로 표현한 관계를 `related`에 중복해 넣지 않는다.

### 본문 채우기

| 타입 | 절 | 주의 |
|---|---|---|
| CON | `## 정의` `## 직관` `## 공식 / 적용 조건` `## 예제` `## 흔한 오해` `## 연결 개념` `## Sources` `## 검증 필요` | 근거가 없으면 `draft` 또는 `needs-review`로 둔다 |
| CON | `## My Understanding` | **비운 채 둔다** |
| QST | `## 질문` `## 발생 맥락` `## 시도한 이해 / 풀이` `## 답변 후보` `## 해결 근거` `## 남은 확인` | 발생 맥락에 원본 위치를 적는다 |
| QST | `## My Questions` | **비운 채 둔다** |

`question_type`은 `conceptual`, `clarification`, `source-verification`, `problem-solving`, `other` 중 하나다.

## 3. 사용자 확인이 필요한 지점

| 상황 | 처리 |
|---|---|
| 개념의 경계가 불명확 | 만들지 않고 근거 노트 본문에 후보로 기록 |
| 새 topic 후보의 의미가 모호하거나 기존 어휘와 구분되지 않음 | **그 후보만** 등록 보류하고 확인. 개수를 이유로 보류하지 않는다 |
| 같은 이름인데 분야별 의미가 다름(예: 물리의 `field`와 DB의 `field`) | 범위를 구분할 수 없으면 기존 노트를 고치지 않고 보고 |
| 의미상 중복으로 보이는 CON 둘 | 자동 병합하지 않는다. 후보로 보고하고 [L9](l9-knowledge-promotion.md)로 넘긴다 |

## 4. 하지 않는 것

- **Concept를 과목별로 복제하지 않는다.** 일반물리학·공학수학·그래픽스에서 모두 벡터를 쓰면 같은 CON을 연결한다.
- 용어가 한 번 등장했다는 이유로 CON을 만들지 않는다.
- 근거 노트 없이 CON을 만들지 않는다.
- ASM·EXM·FAC를 만들거나 고치지 않는다. L5를 호출하지 않는다. 다른 어떤 레이어도 호출하지 않는다.
- 어휘표에 등록하기 전에 `topics`에 값을 쓰지 않는다.
- topic이 새로 생겼다는 이유만으로 CLU를 자동 생성하지 않는다.
- 보호 영역 안의 문장을 고치지 않는다. 거기 있는 질문을 QST로 정리하더라도 **원래 문장은 그대로 둔다.**
- **AI가 답변을 만들었다는 이유로 QST를 `resolved`로 바꾸지 않는다.** 해결 확인은 [L7](l7-review.md) 또는 사용자 확인에서 한다.
- 이미 연결된 근거를 다시 추가하지 않는다.
- 존재하지 않는 ID를 관계 필드에 적지 않는다.

## 5. 완료 조건

- [ ] 새 CON에 정의와 근거가 있다. 없으면 `draft` 또는 `needs-review`다.
- [ ] 새 QST에 `sources`가 있고 발생 맥락이 본문에 있다.
- [ ] 역방향 연결이 **그 타입에 실제로 존재하는 필드**만 사용했다.
- [ ] 사용한 topic이 모두 어휘표에 등록돼 있다. (C5)
- [ ] 관계 필드의 ID가 모두 실제로 존재한다. (C4)
- [ ] 로그를 기록했다.

## 6. 완료 보고 형식

```text
L4 Knowledge extraction 완료

- 입력 후보: 개념 6, 질문 3 (근거: LEC-20260908-01, RES-20260908-01)
- 기존 CON 연결: 4
  - CON-20260415-01 운동량 ← LEC-20260908-01 (aliases에 momentum 있어 동일 판정)
  - CON-20260415-02 에너지 보존 ← LEC-20260908-01
- 신규 CON: 1
  - CON-20260908-01 충격량 (근거 2개: LEC-20260908-01, RES-20260908-01)
- 후보 보류: 2
  - "역학적 계" — 1회 등장, 경계 불명확 → LEC 본문에 후보로만 기록
- 신규 QST: 3 (conceptual 2, source-verification 1)
- 갱신 QST: 0
- topic 신규 등록: 1 (impulse)
- CLU 갱신: CLU-20260415-01 고전역학 (members +2)
- CLU 신규: 없음
- 역방향 연결: LEC.concepts +5, LEC.questions +3, RES는 related + 본문 Key Concepts
- 로그: 5줄
```

## 7. 로그 기록

```text
- 2026-09-08 18:41 | L4 | register-topic | impulse | done | 충격량. 최초 근거 LEC-20260908-01
- 2026-09-08 18:42 | L4 | create-note | CON-20260908-01 | done | 충격량. 근거 2개
- 2026-09-08 18:42 | L4 | update-note | CON-20260415-01 | done | sources에 LEC-20260908-01 추가
- 2026-09-08 18:43 | L4 | create-note | QST-20260908-01 | done | 운동량 보존 조건 확인
- 2026-09-08 18:43 | L4 | sync-relations | LEC-20260908-01 | done | concepts 5, questions 3 역방향 기록
```

## 8. 실행 예시

### 예시 A — 표기가 다른 같은 개념

전사에 `운동량`, 슬라이드에 `momentum`, 기출에 `linear momentum`이 나왔다.

1. `wiki/concepts/`에서 세 표기를 모두 검색한다.
2. `CON-20260415-01` (title: 운동량, aliases: `[momentum, linear momentum]`)이 나온다.
3. **CON 3개를 만들지 않는다.** 기존 하나에 연결한다.
4. `sources`에 `LEC-20260908-01`, `RES-20260908-01`, `PEX-20260909-01`을 모두 추가한다. 근거가 다르므로 셋 다 남는다.
5. 새 표기가 aliases에 없으면 aliases에 추가한다.
6. topic은 어휘표의 기존 `momentum` 하나를 쓴다. `linear-momentum`을 새로 만들지 않는다.

### 예시 B — 만들지 않는 경우

전사에 `역학적 계`라는 말이 한 번 나왔다.

- 근거 노트가 1개뿐이고, 교수가 핵심 개념으로 명시하지 않았고, 독립적 설명 가치도 확인되지 않는다. → 승격 기준 세 가지 모두 미충족.
- CON을 만들지 않고 `LEC`의 `## Concepts` 절에 후보로만 적는다.

  ```markdown
  ## Concepts

  - [[CON-20260415-01]] 운동량
  - [[CON-20260908-01]] 충격량
  - 후보: 역학적 계 (1회 등장, 경계 불명확)
  ```

- 후보에는 ID를 붙이지 않는다. 존재하지 않는 ID를 미리 적지 않는다.
- 나중에 다른 수업에서 다시 나오면 그때 근거 2개로 승격을 판단한다.

### 예시 C — 보호 영역 안의 질문

사용자가 `LEC-20260908-01`의 `## My Notes`에 이렇게 적어 뒀다.

```markdown
## My Notes

충돌에서 운동에너지가 왜 안 지켜지는지 아직 모르겠음
```

- 이 문장을 근거로 `QST`를 만드는 것은 가능하다.
- **원래 문장은 지우거나 고치거나 요약으로 바꾸지 않는다.** `## My Notes`는 그대로 둔다.
- 새 QST의 `## 발생 맥락`에 `LEC-20260908-01의 사용자 메모에서 확인`이라고 적고 `sources`에 그 LEC ID를 넣는다.
- QST의 `## My Questions`는 비운 채 둔다. 사용자 영역이지 옮겨 담는 곳이 아니다.
- AI가 답을 적었더라도 `status`는 `answered`까지다. `resolved`로 올리지 않는다.
