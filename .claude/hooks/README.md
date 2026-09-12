# Claude Hooks

Claude Code의 등록은 [`.claude/settings.json`](../settings.json)에 있다. `SessionStart`에서 공통 core를 exec form으로 부르며 timeout은 5초다. Windows에서 실제 세션 시작으로 확인했다.

공통 구현은 [`_system/hooks/`](../../_system/hooks/README.md)에 있다. 이 디렉터리에는 현재 별도 Hook implementation을 두지 않는다.
