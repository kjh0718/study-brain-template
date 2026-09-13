"""검증 스위트를 한 번에 돌리는 얇은 실행기.

    python _system/docs/run_all.py

검사 로직을 새로 만들지 않는다. 기존 스크립트를 정해진 순서로 부르고
종료 코드와 요약 한 줄을 모아 표로 낸다. 각 스크립트를 직접 실행하는
방법은 그대로 유효하며, 이 파일은 그 방법을 대체하지 않는다.

fixture 생성기(`build_fixtures.py`, `build_filled.py`, `seed_workspace.py`)는
부르지 않는다. 추적 중인 fixture를 다시 만들면 검사 대상이 바뀐다.

하나가 실패해도 나머지를 계속 돌리고 마지막에 non-zero로 끝낸다.
FAIL이 하나라도 있으면 종료 코드 1이다.

    --fail-fast   첫 FAIL에서 멈춘다
    --strict      SKIP도 실패로 본다
    --list        무엇을 도는지만 보여 주고 끝낸다

표준 라이브러리만 쓴다.
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent      # _system/docs
ROOT = HERE.parents[1]                              # 저장소 루트

# 요약을 뽑을 위치. section이면 그 제목 다음 첫 비어 있지 않은 줄, pattern이면 정규식 매치.
SUITES = [
    {
        "name": "template 자체 검사",
        "dir": "template-validation",
        "script": "check_templates.py",
        "needs": ["_system/templates", "_system/schemas"],
        "section": "===== A. 템플릿 자체 검사 PROBLEMS =====",
    },
    {
        "name": "가상 노트 검사",
        "dir": "template-validation",
        "script": "check_filled_notes.py",
        "needs": ["_system/docs/template-validation/filled"],
        "section": "===== B. 가상 노트 검사 PROBLEMS =====",
    },
    {
        "name": "통합 시험 A~K",
        "dir": "integration-test",
        "script": "check_scenarios.py",
        "needs": ["_system/docs/integration-test/vault",
                  "_system/docs/integration-test/broken"],
        "pattern": r"PASS: \d+ / PASS WITH NOTES: \d+",
    },
    {
        "name": "Skill 구조 검사",
        "dir": "skill-validation",
        "script": "check_skills.py",
        "needs": [".agents/skills", ".claude/skills"],
        "section": "===== PROBLEMS =====",
    },
    {
        "name": "Skill 런타임 A~I",
        "dir": "skill-validation/runtime",
        "script": "verify_runtime.py",
        # workspace는 .gitignore 대상이라 새로 clone하면 없다. seed_workspace.py가 만든다.
        "needs": ["_system/docs/skill-validation/runtime/workspace"],
        "hint": "python _system/docs/skill-validation/runtime/seed_workspace.py 로 workspace를 만든 뒤"
                " Skill을 호출해야 검사할 결과가 생긴다.",
        "pattern": r"PASS: \d+",
    },
    {
        "name": "Hook 검사",
        "dir": "hook-validation",
        "script": "test_session_context.py",
        "needs": ["_system/hooks/session_context.py"],
        "pattern": r"PASS \d+ / FAIL \d+",
    },
]


def summarize(suite, out):
    """스크립트 출력에서 한 줄 요약을 뽑는다. 못 뽑으면 마지막 비어 있지 않은 줄."""
    lines = out.splitlines()
    if "pattern" in suite:
        for line in reversed(lines):
            m = re.search(suite["pattern"], line)
            if m:
                return m.group(0)
    if "section" in suite:
        try:
            i = lines.index(suite["section"])
        except ValueError:
            i = -1
        if i >= 0:
            rest = [l.strip() for l in lines[i + 1:] if l.strip()]
            if not rest:
                return "문제 없음"
            if rest[0] == "none":
                return "문제 없음"
            return f"문제 {len(rest)}건: {rest[0][:60]}"
    for line in reversed(lines):
        if line.strip():
            return line.strip()[:70]
    return "(출력 없음)"


def missing(suite):
    return [p for p in suite["needs"] if not (ROOT / p).exists()]


def main():
    ap = argparse.ArgumentParser(add_help=True, description="Study Brain 검증 스위트 일괄 실행")
    ap.add_argument("--fail-fast", action="store_true", help="첫 FAIL에서 멈춘다")
    ap.add_argument("--strict", action="store_true", help="SKIP도 실패로 본다")
    ap.add_argument("--list", action="store_true", dest="list_only", help="목록만 보여 준다")
    args = ap.parse_args()

    if args.list_only:
        print("실행 순서")
        for i, s in enumerate(SUITES, 1):
            print(f"  {i}. {s['name']:<18} _system/docs/{s['dir']}/{s['script']}")
        print("\nfixture 생성기는 부르지 않는다: build_fixtures.py, build_filled.py, seed_workspace.py")
        return 0

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    results, stopped = [], False

    print("=" * 72)
    print("Study Brain 검증 일괄 실행")
    print("=" * 72)

    for suite in SUITES:
        label = suite["name"]
        if stopped:
            results.append((label, "SKIP", "--fail-fast로 중단", 0.0))
            continue
        gone = missing(suite)
        if gone:
            note = f"없음: {gone[0]}"
            if "hint" in suite:
                note += f" — {suite['hint']}"
            results.append((label, "SKIP", note, 0.0))
            print(f"\n[SKIP] {label}")
            print(f"       {note}")
            continue

        cwd = HERE / suite["dir"]
        t0 = time.perf_counter()
        p = subprocess.run([sys.executable, suite["script"]], cwd=cwd, env=env,
                           stdin=subprocess.DEVNULL, capture_output=True)
        dt = time.perf_counter() - t0
        out = p.stdout.decode("utf-8", "replace")
        err = p.stderr.decode("utf-8", "replace").strip()
        status = "PASS" if p.returncode == 0 else "FAIL"
        note = summarize(suite, out)
        if status == "FAIL" and err:
            note = f"{note} | stderr: {err.splitlines()[-1][:60]}"
        results.append((label, status, note, dt))
        print(f"\n[{status}] {label}  ({dt:.1f}s, exit {p.returncode})")
        print(f"       {note}")
        if status == "FAIL":
            if err:
                print("       --- stderr ---")
                for line in err.splitlines()[-12:]:
                    print(f"       {line}")
            if args.fail_fast:
                stopped = True

    print("\n" + "=" * 72)
    print(f"{'스위트':<20} {'결과':<6} 요약")
    print("-" * 72)
    for label, status, note, _ in results:
        print(f"{label:<20} {status:<6} {note}")
    print("=" * 72)

    n_fail = sum(1 for _, s, _, _ in results if s == "FAIL")
    n_skip = sum(1 for _, s, _, _ in results if s == "SKIP")
    n_pass = sum(1 for _, s, _, _ in results if s == "PASS")
    total = sum(d for _, _, _, d in results)
    print(f"PASS {n_pass} / FAIL {n_fail} / SKIP {n_skip}   ({total:.1f}s)")
    if n_fail:
        print("판정: 실패. FAIL을 먼저 해결한다.")
    elif n_skip:
        # SKIP이 있으면 '전체 통과'가 아니다. 돌지 않은 스위트가 있다는 뜻이다.
        print(f"판정: 부분 통과. {n_skip}개 스위트를 돌리지 못했다. 전체 검증을 마친 상태가 아니다.")
        print("      SKIP을 실패로 보려면 --strict.")
    else:
        print("판정: 전체 통과.")
    return 1 if n_fail or (n_skip and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
