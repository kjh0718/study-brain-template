# Claude Skills

Claude Code가 Study Brain Skill을 찾기 위한 **진입점**이다. 규격은 여기 없다.

## 왜 두 곳에 있는가

Skill의 정본은 [`.agents/skills/`](../../.agents/skills/README.md)다. 도구에 중립적이어야 하기 때문이다.

다만 Claude Code는 `.claude/skills/<name>/SKILL.md`만 스캔하고 `.agents/`를 따라가지 않는다. 그래서 이 경로에도 파일이 있어야 한다. 그 파일은 **정본을 가리키기만 한다.**

```text
.agents/skills/<name>/SKILL.md    정본. Purpose, Execution, Do not 등 전체
.claude/skills/<name>/SKILL.md    스텁. frontmatter + 정본 링크
```

긴 내용을 양쪽에 복제하지 않는다. Windows에서 깨지는 symlink도 쓰지 않는다.

## 스텁에 있는 것

- `name` — 폴더 이름과 같다
- `description` — Claude Code의 Skill 탐색이 이 값을 쓴다. **정본의 값과 같아야 한다**
- 정본으로 가는 링크
- `Input: $ARGUMENTS`

`description`만 양쪽에 있는 유일한 중복이다. 탐색에 필요해서 피할 수 없다. 두 값이 어긋나지 않는지는 [`check_skills.py`](../../_system/docs/skill-validation/check_skills.py)가 검사한다.

## Skill 목록

목록과 워크플로 매핑은 [`.agents/skills/README.md`](../../.agents/skills/README.md)에 있다. 여기서 반복하지 않는다.

## 고칠 때

**스텁을 고치지 않는다.** 정본을 고치고 `description`을 스텁에 맞춘 뒤 `check_skills.py`로 확인한다. 스텁에 판단 규칙이나 실행 절차를 쓰면 정본과 갈라진다.

## Hooks

[`.claude/hooks/`](../hooks/README.md)는 아직 비어 있다. 이번 단계에서 만들지 않았다.
