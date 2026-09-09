"""A. 템플릿 자체 검사. 스키마와 대조만 하며 완성 노트 검증이 아니다."""
import pathlib, re, sys, yaml

# Windows 콘솔 기본 인코딩(cp949)에서는 em dash 등이 UnicodeEncodeError를 낸다.
# 검사 결과가 인코딩 때문에 끊기지 않도록 출력 스트림을 UTF-8로 맞춘다.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCH, TPL = ROOT/"_system/schemas", ROOT/"_system/templates"
OPTIONAL = {"course":{"code","term","instructor"}, "lecture":{"week"}, "resource":{"page_count"},
            "assignment":{"submission_method"}, "course-fact":{"effective_from"}}
EXPECT_STATUS = {"course":"planned","lecture":"draft","resource":"draft","concept":"draft",
                 "assignment":"open","exam":"planned","past-exam":"draft","course-fact":"needs-review",
                 "question":"open","review":"planned","cluster":"draft"}
PROTECTED = ["My Notes","My Understanding","My Questions","Personal Reflection"]
problems, ok = [], []

def parse(txt):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    return (yaml.safe_load(m.group(1)), m.group(2)) if m else (None, None)

for tf in sorted(TPL.glob("*.md")):
    if tf.name == "README.md": continue
    t = tf.stem
    sf = SCH/f"{t}.md"
    if not sf.exists(): problems.append(f"{tf.name}: 대응 스키마 없음"); continue
    stxt = sf.read_text(encoding="utf-8")
    sfm = yaml.safe_load(re.search(r"^```yaml\n(.*?)^```$", stxt, re.M|re.S).group(1).strip().strip("-"))
    schema_fields, required = set(sfm), set(sfm) - OPTIONAL.get(t, set())
    sbody = re.search(r"^```markdown\n(.*?)^```$", stxt, re.M|re.S).group(1)
    sheads = re.findall(r"^## (.+)$", sbody, re.M)
    ms = re.search(r"^## Status(?: Values)?\s*$", stxt, re.M)
    allowed = set(re.findall(r"^- `?([a-z-]+)`?:", re.split(r"^## ", stxt[ms.end():], maxsplit=1, flags=re.M)[0], re.M))

    raw = tf.read_text(encoding="utf-8")
    fm, body = parse(raw)
    if fm is None: problems.append(f"{tf.name}: frontmatter 파싱 실패"); continue
    ok.append(f"{tf.name}: YAML 파싱 OK")

    if fm.get("type") != t: problems.append(f"{tf.name}: type={fm.get('type')} != {t}")
    if fm.get("schema") != 1: problems.append(f"{tf.name}: schema != 1")
    st = fm.get("status")
    if st not in allowed: problems.append(f"{tf.name}: status '{st}' 허용 목록 밖 {sorted(allowed)}")
    elif st != EXPECT_STATUS[t]: problems.append(f"{tf.name}: 기본 상태 {st} != 지정값 {EXPECT_STATUS[t]}")
    missing = required - set(fm)
    if missing: problems.append(f"{tf.name}: 필수 필드 누락 {sorted(missing)}")
    extra = set(fm) - schema_fields
    if extra: problems.append(f"{tf.name}: 스키마에 없는 필드 {sorted(extra)}")
    opt_present = set(fm) & OPTIONAL.get(t, set())
    if opt_present: problems.append(f"{tf.name}: 선택 필드가 기본 frontmatter에 포함됨 {sorted(opt_present)}")

    # 자리표시자는 따옴표로 감싼 문자열이어야 한다
    fmraw = re.match(r"^---\n(.*?)\n---\n", raw, re.S).group(1)
    for line in fmraw.splitlines():
        if "{{" in line and not re.search(r':\s*"\{\{[a-z_]+\}\}"\s*$', line):
            problems.append(f"{tf.name}: 자리표시자가 따옴표 문자열이 아님 -> {line.strip()}")
    # 관계 목록은 []
    for k,v in fm.items():
        if isinstance(v, list) and v: problems.append(f"{tf.name}: {k}에 예시 값이 들어 있음 {v}")
    # 본문 섹션
    theads = re.findall(r"^## (.+)$", body, re.M)
    lost = [h for h in sheads if h not in theads]
    if lost: problems.append(f"{tf.name}: 본문 섹션 누락 {lost}")
    # 보호 영역
    prot = [h for h in PROTECTED if h in theads]
    if not prot: problems.append(f"{tf.name}: 보호 제목 없음")
    if "<!-- AI-PROTECTED -->" not in body: problems.append(f"{tf.name}: AI-PROTECTED 표식 없음")
    for h in prot:
        seg = re.split(r"^## ", body.split(f"## {h}\n",1)[1], maxsplit=1, flags=re.M)[0]
        stray = [l for l in seg.splitlines() if l.strip() and not l.strip().startswith("<!--")]
        if stray: problems.append(f"{tf.name}: 보호 영역 '{h}'에 안내/예시 문장 있음 {stray[:2]}")
    # 남은 자리표시자가 본문에 있으면 안 됨(주석 제외)
    for l in body.splitlines():
        if "{{" in l and not l.strip().startswith("<!--"):
            problems.append(f"{tf.name}: 본문에 자리표시자 -> {l.strip()[:60]}")
    ok.append(f"{tf.name}: 필수 {len(required)}개 / 상태 {st} / 섹션 {len(theads)}개 / 보호 {prot}")

if (TPL/"course.md").read_text(encoding="utf-8").count("AUTO-MANAGED") != 2:
    problems.append("course.md: AUTO-MANAGED 시작·끝 표식이 2개가 아님")
for f in ("concepts","questions"):
    if f in yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", (TPL/"resource.md").read_text(encoding="utf-8"), re.S).group(1)):
        problems.append(f"resource.md: 없는 필드 {f} 추가됨")

print("\n".join(ok))
print("\n===== A. 템플릿 자체 검사 PROBLEMS =====")
print("\n".join(problems) if problems else "none")
sys.exit(1 if problems else 0)
