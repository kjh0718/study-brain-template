# Study Brain Template — 설계 문서 묶음

이 폴더는 `study-brain-template`을 구현하기 전에 확정한 목표, 구조, 데이터 모델, 운영 규칙, Git 전략, 구현 순서와 테스트 기준을 문서화한다.

이 프로젝트의 목표는 기존 `second-brain-template`을 단순 fork하는 것이 아니다. 기존 Project Brain의 강점과 다른 AI-native Second Brain의 좋은 패턴을 조합해 **대학 수업·강의 전사·교수 자료·과제·시험·족보·개념·복습**에 특화된 독립적인 Study Brain Template을 만드는 것이다.

## 문서
- `01-PROJECT-VISION.md` — 프로젝트 목적, 사용자 경험, 성공 기준
- `02-ARCHITECTURE.md` — 폴더 구조와 정보 계층
- `03-DATA-MODEL.md` — 11개 Core Type과 관계
- `04-SOURCE-AND-TRUST-POLICY.md` — Raw, authority, provenance, conflict
- `05-WORKFLOWS.md` — L1~L9
- `06-AI-OPERATING-RULES.md` — AI 자동화/확인/보호 정책
- `07-GIT-AND-SYNC-STRATEGY.md` — Template/Private repo와 데스크탑·노트북 동기화
- `08-IMPLEMENTATION-ROADMAP.md` — 구현 순서
- `09-TEST-PLAN.md` — 검증 시나리오
- `10-DECISIONS.md` — 확정 결정/보류 사항

> 핵심 철학: Raw evidence를 보존하고, Study-specific structure로 정리한 뒤, 과목을 넘어 재사용 가능한 지식을 Wiki로 승격한다. AI는 출처·권위·충돌·사용자 작성 영역을 엄격히 구분한다.
