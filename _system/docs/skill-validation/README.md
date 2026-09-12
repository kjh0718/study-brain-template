# Skill Validation

Skill 계층이 **얇은 wrapper로 남아 있는지** 검사한다. Skill이 규칙을 자기 안에 복제하기 시작하면 정본과 갈라지므로, 그것을 기계적으로 막는 것이 목적이다.

```bash
cd _system/docs/skill-validation
python check_skills.py
```

표준 라이브러리만 쓴다. 새 의존성을 추가하지 않았다.

## 검사 항목

| | 내용 |
|---|---|
| A | 모든 Skill이 `SECOND-BRAIN.md`를 참조하는가 |
| B | 전문 Skill이 대응 워크플로를 참조하는가 |
| C | 끊어진 workflow·schema·template 링크가 없는가 |
| D | 같은 운영 규칙이 여러 Skill에 대량 복제되지 않았는가 |
| E | Project Brain 전용 용어(meeting, 회의, issue candidate 등)가 유입되지 않았는가 |
| F | 핵심 안전 규칙이 누락되지 않았는가 |

함께 검사하는 것.

- 폴더 이름과 frontmatter `name`이 같은가
- 구성 절(Purpose / When to use / Required reading / Inputs / Execution / Completion / Do not)이 모두 있는가
- 정본과 스텁의 목록이 일치하는가
- **스텁의 `description`이 정본과 같은가.** 어긋나면 Claude Code의 Skill 탐색이 정본과 다른 설명으로 동작한다
- 스텁이 정본을 가리키는가

## 분량 상한

| 대상 | 상한 | 이유 |
|---|---|---|
| 정본 `SKILL.md` | 90줄 | 넘으면 워크플로를 복사했을 가능성이 높다 |
| 스텁 `SKILL.md` | 20줄 | 스텁은 포인터로 유지한다 |
| Skill 간 40자 이상 동일한 줄 | 2줄까지 | 3줄부터는 규칙 복제로 본다 |

표 행과 번호 목록은 중복 판정에서 제외한다. 형식이 같아서 우연히 겹치기 쉽기 때문이다.

## 검사기 자체 검증

이 검사기는 결함 주입으로 확인했다. 아래 6가지를 각각 심었을 때 모두 탐지하고, 복원하면 다시 통과한다.

- `SECOND-BRAIN.md` 참조 제거 → A
- 워크플로 참조 제거 → B
- schema 링크 파손 → C
- 본문 3줄 복제 → D
- 외래 용어 주입 → E
- 안전 규칙 문구 제거 → F
- 스텁 `description` 변조 → 탐색 불일치

## 다른 검증과의 관계

| 폴더 | 보는 것 |
|---|---|
| [`template-validation/`](../template-validation/README.md) | 템플릿과 스키마의 정합성 |
| [`integration-test/`](../integration-test/README.md) | 워크플로 결과의 일관성 (Scenario A~K) |
| 이 폴더 | Skill 계층의 구조 |

셋은 목적이 다르므로 모두 유지한다. Skill을 고친 뒤에는 이 검사와 함께 나머지 둘도 통과해야 한다. **Skill이 기존 시스템 동작을 바꾸면 안 된다.**
