# Cluster Schema

CLU 노트는 공통 주제로 연결되는 노트를 탐색하기 위한 지도로 묶는다. 저장 위치는 `wiki/clusters/`다. [공통 규칙](common.md)을 함께 적용한다.

## Frontmatter

가상 예시이며 실제 학습 노트가 아니다. ID와 값은 확인된 자료로 교체한다. 빈 근거·대상 목록은 초기 구조 설명용이며 아래 상태 조건을 만족하기 전에는 완료 상태로 사용하지 않는다.

```yaml
---
schema: 1
type: cluster
id: CLU-20260908-01
title: 고전역학 개념 지도
status: draft
topics: []
related: []
created: 2026-09-08
updated: 2026-09-08
members: []
---
```

## Fields

공통 9개 필드는 모두 필수다. type은 `cluster`, id는 `CLU-`로 시작한다.

| 필드 | 필수 | 규칙 |
|---|---|---|
| `members` | 예 | 실제 존재하는 구조화 노트 ID 목록 |

## Status

- draft: 구성 중
- active: 탐색 가능한 지도
- archived: 보존용

## Body Structure

```markdown
## 범위 / 포함 기준

## 핵심 개념

## 학습 순서 / 연결

## 관련 강의 / 자료

## 열린 질문

## My Notes

<!-- AI-PROTECTED -->
```

## Rules

- topics는 wiki/clusters/_topics.md에 등록된 어휘만 사용한다. CLU ID와 topic slug는 서로 다른 식별자다.
- 회원 노트의 본문을 통째로 복사하지 않고 링크와 포함 이유를 기록한다.
- members는 자기 자신과 중복을 포함하지 않는다. 초기 버전에서는 CLU를 members에 중첩하지 않고 다른 Cluster는 related로 연결한다.
- 실제 구성원이 없으면 draft로 둔다. active에는 하나 이상의 유효한 member가 있어야 한다.
- 입력의 topics가 영향을 주는 Cluster만 우선 갱신한다. 전체 스캔은 유지보수 작업으로 분리한다.
- Cluster는 탐색 지도다. 새로운 통찰이나 출제 패턴을 검증 없이 선언하지 않는다. wiki/patterns/는 Core Type에 추가하지 않는다.
- 전용 관계 필드에 기록한 ID는 related에 중복하지 않는다. 실제로 존재하지 않는 후보는 본문에 둔다.
- 날짜·출처·답변을 임의로 확정하지 않는다. 원문 위치와 확인하지 못한 부분을 명시한다.
- 사용자 작성 영역은 공통 보호 규칙을 따른다. 파일 재생성으로 사용자 내용을 덮어쓰지 않는다.

## Identity

권장 형태는 `CLU-<topic slug>`다. 예: `CLU-classical-mechanics`. Cluster는 주제 하나에 대응하므로 의미 기반 ID를 쓴다. topic slug와 CLU ID는 서로 다른 식별자이며, 같은 문자열을 쓰더라도 어휘표의 topic이 곧 Cluster인 것은 아니다.

형식 계약과 Type별 권장 형태는 [common.md](common.md)의 `id` 절이 정본이다. 노트 제목·날짜·파일명이 바뀌어도 기존 ID는 유지하며, 권장 형태로 바꾸려고 기존 ID를 재발급하지 않는다.
