# Workflows

L1~L9의 실행 예시, 체크리스트, 도구별 절차를 보관한다.

## 이 폴더의 위치

- 운영 원칙과 L1~L9의 실행·판단 기준은 루트 [`SECOND-BRAIN.md`](../../SECOND-BRAIN.md)가 정한다. 이 폴더의 문서는 그 기준을 구체화하는 보조 문서다.
- 필드, 타입, 관계, 상태값의 규격은 [`_system/schemas/`](../schemas/README.md)가 정한다.
- 이 폴더의 문서는 별도의 정책을 만들지 않는다. 새 필드, 새 상태값, 새 type, 새 prefix, 다른 처리 순서를 여기서 도입하지 않는다. 로그 작업 코드와 대시보드 구성 규칙도 SECOND-BRAIN.md가 정하며 여기서 바꾸지 않는다.
- 워크플로 문서와 SECOND-BRAIN.md 또는 스키마가 충돌하면 워크플로 문서를 고친다. 충돌을 발견하면 조용히 한쪽을 따르지 않고 충돌 위치를 보고한다.
- 판단 기준을 알기 위해 이 폴더의 문서를 먼저 읽을 필요는 없다. SECOND-BRAIN.md와 참조된 스키마만으로 핵심 판단이 가능해야 한다.

## 문서 목록

| 문서 | 레이어 | 저장소 쓰기 |
|---|---|---|
| [`l1-lecture-ingestion.md`](l1-lecture-ingestion.md) | L1 Lecture ingestion | 예 |
| [`l2-resource-ingestion.md`](l2-resource-ingestion.md) | L2 Resource ingestion | 예 |
| [`l3-past-exam-ingestion.md`](l3-past-exam-ingestion.md) | L3 Past-exam ingestion | 예 |
| [`l4-knowledge-extraction.md`](l4-knowledge-extraction.md) | L4 Knowledge extraction | 예 |
| [`l5-fact-conflict-reconciliation.md`](l5-fact-conflict-reconciliation.md) | L5 Fact and conflict reconciliation | 예 |
| [`l6-recall.md`](l6-recall.md) | L6 Recall | 아니오 |
| [`l7-review.md`](l7-review.md) | L7 Review | 예 |
| [`l8-maintenance.md`](l8-maintenance.md) | L8 Maintain and integrity | 모드에 따라 다름 |
| [`l9-knowledge-promotion.md`](l9-knowledge-promotion.md) | L9 Knowledge promotion and merge | 예 |

각 문서의 구성은 같다. 시작 전 확인, 검색 방법, 실행 체크리스트, 사용자 확인 지점, 하지 않는 것, 완료 조건, 완료 보고 형식, 로그 기록, 실행 예시 순이다.

## 문서를 추가할 때

- 파일명은 레이어 번호로 시작한다. 예: `l1-lecture-ingestion.md`
- 문서 첫 줄에 대응하는 레이어와 SECOND-BRAIN.md의 해당 절 링크를 적는다.
- 내용은 실행 예시, 입력별 체크리스트, 도구·명령 사용법으로 제한한다.
- 규칙을 바꿔야 한다고 판단되면 여기 쓰지 말고 SECOND-BRAIN.md 또는 스키마 수정을 제안한다.

## 공통 검색 명령

아래 명령은 9개 문서가 공유한다. 각 문서는 이 절을 참조하고 자기 타입에 필요한 검색 키만 따로 적는다.

명령 예시는 [ripgrep](https://github.com/BurntSushi/ripgrep)(`rg`) 기준이다. `rg`가 없으면 `grep -rn`으로 바꿔 쓴다. 에이전트 도구를 쓰는 경우 파일 목록 조회는 Glob, 내용 검색은 Grep에 같은 패턴을 넣는다. 특정 플러그인이나 인덱서를 전제하지 않는다.

`study/`와 `wiki/`만 검색하고 `raw/`는 넣지 않는다. `raw/` 확장은 L6의 근거 확인과 L1~L3의 원본 처리에서만 한다.

**C1. 타입별 노트 목록과 핵심 frontmatter**

```bash
rg -n "^(id|title|status|course|date):" study/lectures -g "*.md"
```

폴더 이름만 바꾸면 모든 타입에 쓴다. 본문을 읽지 않고 frontmatter만 본다.

**C2. ID 중복 확인 (저장소 전체)**

```bash
rg -oN --no-filename "^id: .+" study wiki -g "*.md" | sort | uniq -d
```

출력이 있으면 중복이다. 새 ID를 확정하기 전에 항상 확인한다.

**C3. 같은 접두사·날짜의 일련번호 확인**

```bash
rg -oN --no-filename "^id: LEC-20260908-[0-9]+" study wiki -g "*.md" | sort
```

`LEC`과 날짜를 대상에 맞게 바꾼다. 비어 있으면 `-01`부터 시작한다.

**C4. 어떤 ID를 참조하는 노트 찾기 (역참조)**

```bash
rg -ln "CRS-20260908-01" study wiki -g "*.md"
```

관계를 끊거나 대시보드 갱신 대상을 모을 때 쓴다.

**C5. topic 어휘표 조회**

```bash
rg -n "^- " wiki/clusters/_topics.md
```

등록되지 않은 topic은 노트에 쓰지 않는다. 최초 등록 절차는 SECOND-BRAIN.md의 공통 운영 원칙 중 통제된 topics 절을 따른다.

**C6. Course 대시보드 조회 대상 모으기**

```bash
rg -ln "^course: CRS-20260908-01" study -g "*.md"
rg -ln "CRS-20260908-01" study wiki -g "*.md"
```

첫 줄이 주 과목 노트, 두 줄의 차집합이 `related`로만 연결된 공유 노트다. 구성 규칙은 SECOND-BRAIN.md의 Course 대시보드 절과 [`course.md`](../schemas/course.md)를 따른다.

**C7. 보호 영역 위치 확인**

```bash
rg -n "^## (My Notes|My Understanding|My Questions|Personal Reflection)" study wiki -g "*.md"
```

수정 전에 보호 영역의 시작 줄을 확인한다. 그 제목부터 다음 동급 또는 상위 제목 직전까지는 고치지 않는다.

## 로그 기록 공통 형식

한 줄 형식과 작업 코드 목록은 SECOND-BRAIN.md의 `_system/log.md`는 append-only다 절이 정본이다. 여기서 코드를 새로 만들지 않는다.

```
- YYYY-MM-DD HH:MM | L<n> | <작업 코드> | <대상 ID 또는 경로> | <done|partial|held|conflict> | <한 줄 메모>
```

각 문서의 로그 기록 절은 그 레이어에서 실제로 쓰는 코드만 예시로 보여준다.
