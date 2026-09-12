"""Skill 계층의 구조 검사. Skill이 얇은 wrapper로 남아 있는지 확인한다.

검사 항목은 Phase 6 요구사항 A~F에 대응한다.

  A. 모든 Skill이 SECOND-BRAIN.md를 참조하는가
  B. 전문 Skill이 정확한 workflow를 참조하는가
  C. 존재하지 않는 workflow/schema/template 링크가 없는가
  D. 같은 운영 규칙이 여러 Skill에 대량 복제되지 않았는가
  E. Project Brain 전용 용어가 유입되지 않았는가
  F. 핵심 안전 규칙이 누락되지 않았는가

    python check_skills.py

종료 코드 0이면 문제 없음. 표준 라이브러리만 쓴다.
"""
import pathlib, re, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CANON = ROOT / ".agents/skills"
STUB = ROOT / ".claude/skills"

# Skill -> 반드시 참조해야 하는 워크플로. capture는 라우팅이라 특정 워크플로에 묶이지 않는다.
EXPECTED_WF = {
    "ingest-lecture": "l1-lecture-ingestion.md",
    "ingest-resource": "l2-resource-ingestion.md",
    "ingest-past-exam": "l3-past-exam-ingestion.md",
    "check-conflict": "l5-fact-conflict-reconciliation.md",
    "recall": "l6-recall.md",
    "review": "l7-review.md",
    "maintain": "l8-maintenance.md",
}
# Project Brain 전용 용어. Study Brain에 유입되면 안 된다.
FOREIGN = ["meeting", "회의", "issue candidate", "이슈 후보", "decision note",
           "build-from-vault", "issue tracker"]
# 각 Skill이 최소한 한 번은 짚어야 하는 안전 규칙 (전체 복제가 아니라 언급).
SAFETY = {
    "ingest-lecture": ["보호 영역", "데이터"],
    "ingest-resource": ["복제하지 않는다"],
    "ingest-past-exam": ["확정으로 쓰지 않는다"],
    "check-conflict": ["자동 덮어쓰기 금지", "superseded_by"],
    "recall": ["읽기 전용"],
    "review": ["Personal Reflection"],
    "maintain": ["검사 모드"],
    "capture": ["데이터"],
}
SECTIONS = ["## Purpose", "## When to use", "## Required reading", "## Inputs",
            "## Execution", "## Completion", "## Do not"]

problems, ok = [], []


def frontmatter(text, path):
    m = re.match(r"^---\nname: (.+?)\ndescription: (.+?)\n---\n(.*)$", text, re.S)
    if not m:
        problems.append(f"{path}: frontmatter(name/description) 파싱 실패")
        return None, None, ""
    return m.group(1).strip(), " ".join(m.group(2).split()), m.group(3)


canon = {}
for d in sorted(p for p in CANON.iterdir() if p.is_dir()):
    f = d / "SKILL.md"
    if not f.is_file():
        problems.append(f".agents/skills/{d.name}: SKILL.md 없음")
        continue
    text = f.read_text(encoding="utf-8")
    name, desc, body = frontmatter(text, f"canonical/{d.name}")
    canon[d.name] = {"name": name, "desc": desc, "body": body, "text": text, "path": f}

if not canon:
    problems.append("canonical Skill이 하나도 없다")

for skill, c in canon.items():
    tag = f".agents/skills/{skill}"
    if c["name"] != skill:
        problems.append(f"{tag}: 폴더 이름과 frontmatter name 불일치 ({c['name']})")

    # A. SECOND-BRAIN.md 참조
    if "SECOND-BRAIN.md" not in c["text"]:
        problems.append(f"[A] {tag}: SECOND-BRAIN.md를 참조하지 않는다")

    # B. 워크플로 참조
    wf = EXPECTED_WF.get(skill)
    if wf and wf not in c["text"]:
        problems.append(f"[B] {tag}: 대응 워크플로 {wf}를 참조하지 않는다")
    for other, ofile in EXPECTED_WF.items():
        if other != skill and ofile in c["text"] and skill != "capture":
            # 다른 레이어를 호출하는 것은 정상이므로 링크 자체는 허용하고 알림만 남긴다.
            ok.append(f"{tag}: 다른 레이어 {other} 참조 (호출 관계)")

    # 구성 절 존재
    miss = [s for s in SECTIONS if s not in c["text"]]
    if miss:
        problems.append(f"{tag}: 필수 절 누락 {miss}")

    # E. 외래 용어
    low = c["text"].lower()
    hit = [w for w in FOREIGN if w.lower() in low]
    if hit:
        problems.append(f"[E] {tag}: Project Brain 전용 용어 유입 {hit}")

    # F. 안전 규칙 언급
    for phrase in SAFETY.get(skill, []):
        if phrase not in c["text"]:
            problems.append(f"[F] {tag}: 안전 규칙 '{phrase}' 언급 없음")

    # 얇기: 정본이 지나치게 길면 워크플로를 복사했을 가능성이 높다
    n = len(c["text"].splitlines())
    if n > 90:
        problems.append(f"[D] {tag}: {n}줄. 워크플로를 복사했는지 확인 (상한 90)")
    else:
        ok.append(f"{tag}: {n}줄")

# C. 링크 실재 확인
for skill, c in canon.items():
    for link in re.findall(r"\]\(([^)]+)\)", c["text"]):
        link = link.split("#")[0].strip()
        if not link or link.startswith(("http", "mailto:")):
            continue
        if not (c["path"].parent / link).exists():
            problems.append(f"[C] .agents/skills/{skill}: 끊어진 링크 {link}")

# 스텁 검사
stub_names = {p.name for p in STUB.iterdir() if p.is_dir()}
if stub_names != set(canon):
    problems.append(f"스텁/정본 목록 불일치. 정본만 {sorted(set(canon) - stub_names)} / "
                    f"스텁만 {sorted(stub_names - set(canon))}")

for skill in sorted(stub_names & set(canon)):
    f = STUB / skill / "SKILL.md"
    tag = f".claude/skills/{skill}"
    if not f.is_file():
        problems.append(f"{tag}: SKILL.md 없음")
        continue
    text = f.read_text(encoding="utf-8")
    name, desc, body = frontmatter(text, f"stub/{skill}")
    if name != skill:
        problems.append(f"{tag}: name 불일치 ({name})")
    if desc != canon[skill]["desc"]:
        problems.append(f"{tag}: description이 정본과 다르다 (Skill 탐색이 어긋난다)")
    if f".agents/skills/{skill}/SKILL.md" not in text:
        problems.append(f"{tag}: 정본을 가리키지 않는다")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        link = link.split("#")[0].strip()
        if link and not link.startswith(("http", "mailto:")) and not (f.parent / link).exists():
            problems.append(f"{tag}: 끊어진 링크 {link}")
    # D. 스텁이 두꺼워지면 정본과 갈라진다
    n = len(text.splitlines())
    if n > 20:
        problems.append(f"[D] {tag}: {n}줄. 스텁은 포인터로 유지한다 (상한 20)")
    else:
        ok.append(f"{tag}: {n}줄 (스텁)")

# D. Skill 간 장문 중복
bodies = {s: [l.strip() for l in c["body"].splitlines() if len(l.strip()) >= 40]
          for s, c in canon.items()}
names = sorted(bodies)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        shared = set(bodies[a]) & set(bodies[b])
        shared = {s for s in shared if not s.startswith(("|", "1.", "2.", "3."))}
        if len(shared) > 2:
            problems.append(f"[D] {a} <-> {b}: 40자 이상 동일한 줄 {len(shared)}개")

print("=" * 64)
print("Skill 구조 검사")
print("=" * 64)
print(f"\ncanonical {len(canon)}개 / stub {len(stub_names)}개\n")
for line in ok:
    print(f"  {line}")
print("\n===== PROBLEMS =====")
print("\n".join(problems) if problems else "none")
sys.exit(1 if problems else 0)
