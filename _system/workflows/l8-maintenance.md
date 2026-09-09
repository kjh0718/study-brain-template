# L8 — Maintain and integrity 실행 문서

대응 레이어: **L8**. 판단 기준의 정본은 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)의 `L8 — Maintain and integrity` 절이다.

> 이 문서는 실행 보조 문서다. 규칙을 새로 만들지 않고 검색 명령, 체크리스트, 보고·로그 형식, 실행 예시만 담는다. 이 문서와 SECOND-BRAIN.md가 다르면 SECOND-BRAIN.md가 맞고 이 문서를 고친다.

## 한눈에 보기

| 항목 | 값 |
|---|---|
| 목적 | 무결성을 검사하고, 승인된 범위 안에서만 고친다 |
| 입력 | 사용자 요청. 수정 모드는 **대상 범위가 함께** 있어야 한다 |
| 저장소 쓰기 | 모드에 따라 다름 |
| 호출할 수 있는 레이어 | 없다. 사용자 요청으로만 시작한다 |

### 두 모드를 먼저 구분한다

| 사용자 말 | 모드 | 파일 수정 | 로그 |
|---|---|---|---|
| "검사해줘", "확인해줘" | **검사 모드** | 하지 않는다 | **쓰지 않는다** |
| "정리해줘", "수정해줘" | **수정 모드** | 승인 범위 안에서만 | 쓴다 |

**수정 모드인데 범위가 명시되지 않았으면 검사 모드로 수행하고 수정 후보 목록을 보고한다. 범위를 추정해 고치지 않는다.**

### 검사 범위 제외

다음은 학습 노트 규격 검사 대상이 아니다.

- `wiki/patterns/` — Core Type이 아니다. 근거 ID 실재 여부와, 반례를 확인한 범위·적용 범위가 적혀 있는지만 본다.
- `README.md`, 스키마 문서, `HOME.md`, `SECOND-BRAIN.md`, `_system/log.md`, `wiki/clusters/_topics.md`, `raw/` 원본

## 1. 검사 명령

공통 명령은 [`README.md`](README.md)에 있다. 아래는 검사 항목 10개에 대응한다.

**허용 값은 스키마에서 읽는다.** 이 문서에 상태값을 베껴 두지 않는다. 베껴 두면 스키마가 바뀔 때 어긋난다.

```bash
awk '/^## Status/,/^## [A-Z]/' _system/schemas/lecture.md
```

**1. 필수 필드의 존재와 타입**

공통 9개(`schema`, `type`, `id`, `title`, `status`, `topics`, `related`, `created`, `updated`)와 각 타입 스키마의 필수 필드를 함께 본다.

```bash
# 공통 필드가 빠진 파일 찾기 (예: status)
rg -L "^status:" study wiki -g "*.md" --glob '!**/README.md'
```

`rg -L`은 패턴이 **없는** 파일을 출력한다. 필드 이름만 바꿔 9번 돌린다.

**2. `status`가 허용 목록 안에 있는지**

```bash
rg -oN --no-filename "^status: .+" study/lectures -g "*.md" | sort -u
```

출력을 위 `awk` 결과와 대조한다. 폴더마다 반복한다.

**3. ID 형식, 접두사, 저장소 전체 중복** — C2.

```bash
rg -oN --no-filename "^id: .+" study wiki -g "*.md" | sort | uniq -d
# 접두사와 저장 위치가 맞는지
rg -n "^id: (?!LEC-)" study/lectures -g "*.md" -P
```

**4. 관계 무결성** — 참조된 ID가 실재하는지, 자기 참조가 없는지, 전용 필드와 `related`가 중복되지 않는지.

```bash
# 존재하는 모든 ID
rg -oN --no-filename "^id: \K.+" study wiki -g "*.md" | sort -u > /tmp/ids.txt
# 참조된 모든 ID
rg -oN --no-filename "\b(CRS|LEC|CON|ASM|EXM|PEX|FAC|QST|RES|REV|CLU)-[A-Za-z0-9-]+" study wiki -g "*.md" | sort -u > /tmp/refs.txt
# 실재하지 않는 참조
comm -13 /tmp/ids.txt /tmp/refs.txt
```

임시 파일은 저장소 밖에 둔다. `study/`나 `wiki/`에 만들지 않는다.

**5. `Lecture.resources`와 `Resource.lectures`의 양방향 일치**

```bash
rg -n -A3 "^resources:" study/lectures -g "*.md"
rg -n -A5 "^lectures:" study/resources -g "*.md"
```

한쪽에만 있는 연결이 있으면 불일치다.

**6. `source`와 `sources`의 용도 구분**

```bash
# 로컬 경로인 source의 파일 존재 확인
rg -oN --no-filename "^source: \K(?!http).+" study -g "*.md" -P | while read -r p; do
  [ -e "$p" ] || echo "MISSING: $p"
done
```

`source`가 외부 URL이면 **존재 검사 대신** 형식과 접근 기록 여부만 본다. 접근하지 못한 외부 참조를 파일 누락으로 보고하지 않는다. `sources`는 노트 ID 목록이므로 경로 검사 대상이 아니다.

**7. `topics`가 어휘표에 등록돼 있는지**

어휘표에는 규칙 설명 불릿과 registry 항목이 함께 있다. `^- `로만 뽑으면 규칙 설명을 topic으로 오인하므로, SECOND-BRAIN.md가 정한 항목 형태(`- <slug> — <정의> ...`)를 그대로 요구한다.

```bash
rg -oN --no-filename "^- \K[a-z0-9-]+(?= — )" wiki/clusters/_topics.md | sort -u > /tmp/vocab.txt
rg -N --no-filename -A20 "^topics:" study wiki -g "*.md" | rg -oN "^\s+- \K[a-z0-9-]+$" | sort -u > /tmp/used.txt
comm -13 /tmp/vocab.txt /tmp/used.txt
```

**8. Course 대시보드가 조회 결과와 일치하는지** — C6으로 조회 결과를 다시 만들어 자동 관리 영역과 텍스트로 비교한다. 구성·정렬 규칙은 SECOND-BRAIN.md의 `2.9`가 정본이다.

**9. `FAC.supersedes`의 자기 참조와 순환**

```bash
rg -n -A5 "^supersedes:" study/course-facts -g "*.md"
```

각 FAC의 `id`가 자기 `supersedes`에 있으면 자기 참조다. 사슬을 따라가다 시작점으로 돌아오면 순환이다.

**10. 보호 영역의 존재 여부** — C7. **없더라도 자동으로 삽입하지 않는다.** 보고만 한다.

### 기존 검증 스크립트

[`../docs/template-validation/`](../docs/template-validation/README.md)에 템플릿과 가상 노트를 검사하는 스크립트가 있다. 대상이 `_system/templates/`와 생성된 `filled/`이므로 실제 학습 노트 검사와는 범위가 다르다. L8을 대신하지 않는다.

## 2. 실행 체크리스트

**검사 모드**

- [ ] 1. 범위를 수집한다. 범위가 없으면 `study/`, `wiki/`, `_system/schemas/` 전체와 노트가 참조하는 `raw/` 경로의 존재 여부까지다.
- [ ] 2. 위 10개 항목을 검사한다.
- [ ] 3. 보고서를 출력한다. 파일, 위치, 항목, 심각도를 적는다.
- [ ] 4. **로그를 쓰지 않는다.**

**수정 모드**

- [ ] 1. 승인 범위를 확인한다. 없으면 검사 모드로 전환한다.
- [ ] 2. SECOND-BRAIN.md의 안전 순서표에서 **낮은 단계부터** 고친다.
- [ ] 3. 항목별로 수정한다.
- [ ] 4. 로그를 기록한다.
- [ ] 5. 수정한 항목과 **남은 항목을 모두** 보고한다.

## 3. 사용자 확인이 필요한 지점

수정 모드에서도 **보고만 하는** 항목이 있다. 자동 수정으로 정보가 사라질 수 있기 때문이다.

| 항목 | 처리 |
|---|---|
| 중복 노트 병합 | 보고만. [L9](l9-knowledge-promotion.md) 또는 사용자 판단으로 넘긴다 |
| 상충하는 사실 | 보고만. [L5](l5-fact-conflict-reconciliation.md)로 넘긴다 |
| 보호 영역 관련 항목 | 보고만. 없는 보호 영역을 삽입하지 않는다 |
| 범위가 명시되지 않은 수정 요청 | 검사 모드로 수행하고 후보 목록 제시 |

## 4. 하지 않는 것

- **검사 모드에서 파일을 고치거나 로그를 쓰지 않는다.**
- 승인 범위를 추정해 고치지 않는다.
- 없는 보호 영역을 자동으로 삽입하지 않는다.
- 중복 노트를 자동 병합하지 않는다. 파일을 지우거나 ID를 회수하지 않는다.
- 상충하는 사실 중 한쪽을 임의로 골라 정리하지 않는다.
- 스키마에 없는 필드나 상태값을 만들어 무결성을 맞추지 않는다. 스키마를 먼저 고치도록 제안한다.
- 접근하지 못한 외부 참조를 파일 누락으로 보고하지 않는다.
- `wiki/patterns/`에 학습 노트 frontmatter를 요구하지 않는다.
- 검사 대상이 아닌 문서(README, 스키마, 로그, 어휘표, `raw/`)를 규격 위반으로 보고하지 않는다.
- "빈 폴더 정리" 같은 이유로 원본이나 노트를 옮기지 않는다.
- 이미 고친 항목을 다시 고치지 않는다.

## 5. 완료 조건

- [ ] 검사 모드: 보고서를 제출했다. 저장소를 바꾸지 않았다.
- [ ] 수정 모드: 수정한 항목과 남은 항목을 **모두** 보고했다. 로그를 기록했다.

## 6. 완료 보고 형식

### 검사 모드

심각도는 `high`(데이터 정확성 훼손), `medium`(관계·표시 불일치), `low`(표기·정리)로 적는다.

```text
L8 무결성 검사 보고 (검사 모드 — 저장소를 바꾸지 않았다)

범위: study/, wiki/, 참조된 raw/ 경로
검사한 노트: 42

[high] 3건
1. 관계 무결성 — study/lectures/2026-09-10-physics.md:14
   concepts에 CON-20260910-99가 있으나 그런 노트가 없다
2. supersede 순환 — study/course-facts/exam-date-v2.md:27
   FAC-20260908-01 → FAC-20260415-03 → FAC-20260908-01
3. source 누락 — study/resources/ch05-slides.md:12
   source: raw/resources/ch05.pdf 파일이 없다 (로컬 경로)

[medium] 2건
4. 양방향 불일치 — LEC-20260915-01.resources에 RES-20260908-01이 있으나
   RES-20260908-01.lectures에 그 LEC이 없다
5. 대시보드 불일치 — study/courses/physics2.md
   조회 결과 9행, 자동 관리 영역 7행. LEC 2건 누락

[low] 1건
6. 미등록 topic — study/lectures/2026-09-15-physics.md
   topics에 collision이 있으나 _topics.md에 없다

[보고만 하는 항목] 2건
7. 중복 의심 — CON-20260415-01(운동량)과 CON-20260910-02(momentum)
   → 자동 병합하지 않았다. L9 요청 시 처리 가능
8. 보호 영역 없음 — study/lectures/2026-09-10-physics.md에 ## My Notes 없음
   → 자동 삽입하지 않았다

[검사 대상 제외] wiki/patterns/ 1개, README 21개, raw/ 원본
```

### 수정 모드

```text
L8 정리 완료 (수정 모드)

승인 범위: study/lectures/
안전 순서: 낮은 단계부터 수행

[수정함] 2건
1. LEC-20260915-01.resources의 RES-20260908-01 → RES-20260908-01.lectures에 역방향 추가
2. topic collision 어휘표 등록 후 LEC-20260915-01.topics 유지

[범위 밖이라 손대지 않음] 3건
3. study/course-facts/의 supersede 순환 → 승인 범위 밖
4. study/resources/ch05-slides.md의 source 누락 → 승인 범위 밖

[수정 모드에서도 보고만 함] 2건
5. CON 중복 의심 → L9 요청 필요
6. 보호 영역 없음 → 자동 삽입하지 않음

남은 항목: 5건
로그: 3줄
```

## 7. 로그 기록

**검사 모드는 로그를 쓰지 않는다.** 충돌이나 무결성 위반을 발견해도 보고서에만 적는다.

수정 모드만 기록한다.

```text
- 2026-09-20 14:10 | L8 | sync-relations | RES-20260908-01 | done | LEC-20260915-01 역방향 누락 복구
- 2026-09-20 14:12 | L8 | register-topic | collision | done | LEC-20260915-01에서 사용 중이던 미등록 topic
- 2026-09-20 14:15 | L8 | finalize-run | study/lectures/ | partial | 승인 범위 밖 3건, 보고만 2건 남음
```

## 8. 실행 예시

### 예시 — 일부러 오류를 넣고 검사하기

템플릿을 검증할 때는 다음 여섯 가지를 의도적으로 만들고 검사가 전부 잡는지 본다.

| 넣을 오류 | 잡는 검사 항목 |
|---|---|
| YAML 문법 오류(닫히지 않은 따옴표) | 1 |
| 없는 ID 참조 (`CON-99999999-99`) | 4 |
| 중복 topic slug (`momentum`과 `linear-momentum`) | 7 |
| 어디에서도 참조되지 않는 orphan 노트 | 4 |
| 허용되지 않는 `status` 값 (`lecture`에 `active`) | 2 |
| 끊어진 supersede 사슬 (`supersedes`가 없는 ID를 가리킴) | 9 |

`lecture`에 `active`를 넣는 것은 실제로 있었던 혼동이다. [`lecture.md`](../schemas/lecture.md)의 Status 절이 `active`를 초기 예시값으로만 언급하고 허용 값에서 뺐다. 검사 2가 이것을 잡아야 한다.

### 검사 모드에서 수정 요청으로 넘어가는 흐름

```text
사용자: 브레인 한번 확인해줘
→ 검사 모드. 보고서만 낸다. 로그도 쓰지 않는다.

사용자: 1번이랑 4번 고쳐줘
→ 수정 모드. 승인 범위가 "1번, 4번"으로 명시됐다.
→ 그 둘만 고친다. 보고서의 나머지는 손대지 않는다.

사용자: 다 정리해줘
→ "다"가 범위인지 불명확하다. 검사 모드로 다시 수행하고
   수정 후보 목록을 제시한 뒤 어느 것을 승인할지 묻는다.
   보고서 전체를 임의로 실행하지 않는다.
```

**L8이 후보를 보고한 것은 실행 승인이 아니다.** 특히 중복 병합과 패턴 승격은 사용자가 L9를 명시적으로 요청해야 시작한다.
