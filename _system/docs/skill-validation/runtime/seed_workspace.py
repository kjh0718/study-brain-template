"""Runtime Test용 격리 workspace를 만든다.

integration-test/vault/ fixture에서 **ingest 이전 상태만** 복사해 온다.
L1이 만들어야 할 노트는 일부러 빼 두므로, Skill을 따라 실행하면 실제로 일이 생긴다.

여기서 만드는 모든 파일은 **가상 테스트 데이터**다. 실제 학습 자료가 아니다.
저장소의 실제 raw/, study/, wiki/는 건드리지 않는다.

    python seed_workspace.py
"""
import hashlib, json, pathlib, re, shutil, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parents[1] / "integration-test/vault"
WS = HERE / "workspace"
MANIFEST = HERE / "seed-manifest.json"

# ingest 이전에 이미 있어야 하는 것만 가져온다.
SEED = [
    "raw/transcripts/2026-09-08-general-physics-2-01.md",   # L1 입력
    "raw/notices/2026-09-01-lms-midterm.md",                # 기존 공지
    "study/courses/general-physics-2-2026-2.md",            # 대상 CRS
    "study/exams/2026-midterm.md",                          # 기존 EXM (누적 대상)
    "study/course-facts/exam-date-v1.md",                   # 기존 FAC (충돌 대상)
    "wiki/concepts/momentum.md",                            # 기존 CON (연결 대상)
]

# L1/L2/L4/L5가 만들어야 하므로 seed하지 않는 것.
ABSENT = [
    "study/lectures/", "study/assignments/", "study/questions/",
    "study/resources/", "wiki/concepts/impulse.md", "raw/resources/",
]

if WS.exists():
    shutil.rmtree(WS)

for rel in SEED:
    src = FIXTURE / rel
    dst = WS / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

# CRS 대시보드는 비워 둔다. L1이 재구성해야 한다.
crs = WS / "study/courses/general-physics-2-2026-2.md"
t = crs.read_text(encoding="utf-8")
start = t.index("<!-- AUTO-MANAGED:start -->")
end = t.index("<!-- AUTO-MANAGED:end -->") + len("<!-- AUTO-MANAGED:end -->")
crs.write_text(t[:start] + "<!-- AUTO-MANAGED:start -->\n<!-- AUTO-MANAGED:end -->" + t[end:],
               encoding="utf-8")

def drop_refs(path, keep):
    """frontmatter의 sources 목록을 keep에 있는 항목만 남긴다.
    fixture의 'sources: ' 뒤 공백 유무에 영향받지 않도록 정규식으로 처리한다."""
    p = WS / path
    t = p.read_text(encoding="utf-8")
    m = re.search(r"^sources:[ \t]*\n((?:  - .+\n)+)", t, re.M)
    if not m:
        raise SystemExit(f"seed 실패: {path}의 sources 목록을 찾지 못했다")
    kept = [l for l in m.group(1).splitlines() if l.strip("- ").strip() in keep]
    if not kept:
        raise SystemExit(f"seed 실패: {path}에 남길 sources가 없다")
    p.write_text(t[:m.start()] + "sources:\n" + "\n".join(kept) + "\n" + t[m.end():],
                 encoding="utf-8")


# EXM은 이번 전사 근거를 아직 갖지 않은 상태로 되돌린다. L1/L5가 누적해야 한다.
drop_refs("study/exams/2026-midterm.md", {"FAC-general-physics-2-20260901-01"})

# 기존 FAC는 아직 유효한 상태로 둔다. fixture에서는 이미 superseded지만, 그대로 두면
# check-conflict의 supersede 전이를 검증할 수 없다. 대체는 L5가 수행해야 한다.
v1 = WS / "study/course-facts/exam-date-v1.md"
t = v1.read_text(encoding="utf-8")
t = t.replace("status: superseded", "status: active", 1)
t = re.sub(r"^## 충돌 / 확인 필요\n(?:.*\n)*?(?=^## )",
           "## 충돌 / 확인 필요\n\n없음. 현재 유효한 공지다.\n\n", t, count=1, flags=re.M)
t = re.sub(r"^- 2026-09-08 명시적 변경으로 superseded\n", "", t, count=1, flags=re.M)
v1.write_text(t, encoding="utf-8")

# CON-momentum은 이전 학기에 만들어진 기존 개념으로 둔다. 이 workspace에는 그 근거 노트가
# 없으므로 sources를 비우고 본문에 사실을 적는다. 없는 ID를 참조하지 않기 위해서다.
NOTE = (
    "## Sources\n\n"
    "이 개념은 이전 학기에 만들어졌다. 그때의 근거 노트는 이 runtime workspace에 넣지 않았으므로\n"
    "`sources`를 비워 두었다. 이번 실행에서 확인된 근거를 L4가 추가해야 한다.\n"
)
mom = WS / "wiki/concepts/momentum.md"
t = mom.read_text(encoding="utf-8")
t = re.sub(r"^sources:[ \t]*\n(?:  - .+\n)+", "sources: []\n", t, count=1, flags=re.M)
t = t.replace("## Sources\n", NOTE, 1)
mom.write_text(t, encoding="utf-8")


# topic 어휘표는 momentum만 등록된 상태. impulse는 L4가 등록해야 한다.
(WS / "wiki/clusters").mkdir(parents=True, exist_ok=True)
(WS / "wiki/clusters/_topics.md").write_text(
    "<!-- Runtime Test용 가상 데이터. 실제 학습 자료가 아니다. -->\n"
    "# Topic Vocabulary (runtime fixture)\n\n"
    "- momentum — 질량과 속도의 곱으로 정의되는 벡터량 (최초 근거: CON-momentum)"
    " 별칭: 운동량, linear momentum\n", encoding="utf-8")

# 빈 로그. 첫 기록부터 append-only.
(WS / "_system").mkdir(parents=True, exist_ok=True)
(WS / "_system/log.md").write_text(
    "<!-- Runtime Test용 가상 데이터. 실제 학습 자료가 아니다. -->\n", encoding="utf-8")

for d in ("inbox", "raw/past-exams", "wiki/patterns"):
    (WS / d).mkdir(parents=True, exist_ok=True)

# 읽기 전용 검증용 해시 manifest
man = {}
for f in sorted(WS.rglob("*")):
    if f.is_file():
        man[str(f.relative_to(WS)).replace("\\", "/")] = hashlib.sha256(
            f.read_bytes()).hexdigest()
MANIFEST.write_text(json.dumps(man, indent=2, sort_keys=True), encoding="utf-8")

print(f"seed 완료: {len(man)}개 파일 -> {WS}")
print("seed된 것:")
for rel in sorted(man):
    print(f"  {rel}")
print("\nL1~L5가 만들어야 하므로 비워 둔 것:")
for a in ABSENT:
    print(f"  {a}")
