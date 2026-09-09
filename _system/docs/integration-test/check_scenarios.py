"""Scenario A~K 통합 시험. vault/ fixture에 대해 규칙 준수를 기계적으로 검사한다.

규칙의 정본은 다음과 같고 이 스크립트는 그것을 검사할 뿐 새 정책을 만들지 않는다.
  - 데이터 필드/상태/관계  -> _system/schemas/
  - 운영 판단 기준         -> SECOND-BRAIN.md
  - 실행 절차/보고 형식    -> _system/workflows/

    python build_fixtures.py && python check_scenarios.py

종료 코드 0이면 FAIL 없음.
"""
import hashlib, json, pathlib, re, sys, yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCH = ROOT / "_system/schemas"
V = HERE / "vault"
BROKEN = HERE / "broken"
SNAP = HERE / "protected-snapshot.json"

ID_CONTRACT = re.compile(
    r"^(?:CRS|LEC|CON|ASM|EXM|PEX|FAC|QST|RES|REV|CLU)-[a-z0-9]+(?:-[a-z0-9]+)*$")
PREFIX = {"course": "CRS", "lecture": "LEC", "concept": "CON", "assignment": "ASM",
          "exam": "EXM", "past-exam": "PEX", "course-fact": "FAC", "question": "QST",
          "resource": "RES", "review": "REV", "cluster": "CLU"}
OPTIONAL = {"course": {"code", "term", "instructor"}, "lecture": {"week"},
            "resource": {"page_count"}, "assignment": {"submission_method"},
            "course-fact": {"effective_from"}}
PROTECTED = ("My Notes", "My Understanding", "My Questions", "Personal Reflection")

results = {}          # scenario -> (verdict, [detail lines])


def record(name, fails, notes_):
    verdict = "FAIL" if fails else ("PASS WITH NOTES" if notes_ else "PASS")
    results[name] = (verdict, fails + notes_)


# ---------------------------------------------------------------- 로드
spec = {}
for f in SCH.glob("*.md"):
    if f.name in ("README.md", "common.md"):
        continue
    t = f.stem
    txt = f.read_text(encoding="utf-8")
    ex = yaml.safe_load(re.search(r"^```yaml\n(.*?)^```$", txt, re.M | re.S).group(1).strip().strip("-"))
    ms = re.search(r"^## Status(?: Values)?\s*$", txt, re.M)
    st = set(re.findall(r"^- `?([a-z-]+)`?:",
                        re.split(r"^## ", txt[ms.end():], maxsplit=1, flags=re.M)[0], re.M))
    spec[t] = {"fields": set(ex), "required": set(ex) - OPTIONAL.get(t, set()), "status": st}

notes = {}      # id -> dict(path, fm, body)
parse_fail = []
for f in sorted(V.rglob("*.md")):
    rel = f.relative_to(V)
    if rel.parts[0] in ("raw", "_system") or f.name == "_topics.md":
        continue
    raw = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        parse_fail.append(f"{rel}: frontmatter 없음")
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as e:
        parse_fail.append(f"{rel}: YAML 오류 {e}")
        continue
    notes[fm["id"]] = {"path": f, "rel": rel, "fm": fm, "body": m.group(2)}

IDS = set(notes)


def by_type(t):
    return {i: n for i, n in notes.items() if n["fm"]["type"] == t}


def section(body, title):
    """## <title> 절의 본문을 반환한다. 다음 동급 제목 직전까지."""
    m = re.search(rf"^## {re.escape(title)}\s*$", body, re.M)
    if not m:
        return None
    rest = body[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


# ================================================================ 공통: 스키마 적합성
fails, warn = list(parse_fail), []
for nid, n in notes.items():
    fm, rel, t = n["fm"], n["rel"], n["fm"]["type"]
    s = spec[t]
    miss = s["required"] - set(fm)
    if miss:
        fails.append(f"{rel}: 필수 필드 누락 {sorted(miss)}")
    ext = set(fm) - s["fields"]
    if ext:
        fails.append(f"{rel}: 스키마에 없는 필드 {sorted(ext)}")
    if fm["status"] not in s["status"]:
        fails.append(f"{rel}: status '{fm['status']}' 불허 (허용 {sorted(s['status'])})")
    if not nid.startswith(PREFIX[t] + "-"):
        fails.append(f"{rel}: ID 접두사 불일치 {nid}")
    if not ID_CONTRACT.match(nid):
        fails.append(f"{rel}: ID 형식 계약 위반 {nid}")
    for k in ("related", "concepts", "questions", "assignments", "exams", "course_facts",
              "sources", "answer_sources", "targets", "members", "lectures", "supersedes"):
        for r in (fm.get(k) or []):
            r = r["id"] if isinstance(r, dict) else r
            if isinstance(r, str) and re.match(r"^[A-Z]{3}-", r):
                if r not in IDS:
                    fails.append(f"{rel}: {k}의 {r} 대상 노트 없음")
                if r == nid:
                    fails.append(f"{rel}: {k}에 자기 자신")
    for k in ("course", "subject"):
        v = fm.get(k)
        if isinstance(v, str) and re.match(r"^[A-Z]{3}-", v) and v not in IDS:
            fails.append(f"{rel}: {k}의 {v} 대상 노트 없음")
    src = fm.get("source")
    if isinstance(src, str) and not src.startswith("http"):
        if not (V / src).exists():
            fails.append(f"{rel}: source 파일 없음 {src}")
record("공통 스키마 적합성", fails, warn)

# ================================================================ Scenario A
fails, warn = [], []
lec = notes.get("LEC-20260908-01")
if not lec:
    fails.append("LEC-20260908-01 없음")
else:
    b = lec["body"]
    tr = V / lec["fm"]["source"]
    if not tr.exists():
        fails.append("raw transcript가 보존되지 않았다")
    elif "00:41:12" not in tr.read_text(encoding="utf-8"):
        fails.append("raw transcript 원문이 훼손됐다")

    emph = section(b, "교수님 강조") or ""
    ai = section(b, "AI 해석 / 검증 필요") or ""
    if "중간고사에 반드시 나옵니다" not in emph:
        fails.append("교수 발언이 교수님 강조 절에 없다")
    if "AI 해석" in emph:
        fails.append("교수님 강조 절에 AI 해석이 섞였다")
    if "(AI 해석)" not in ai:
        fails.append("AI 해석 절에 AI 표시가 없다")
    # 교수가 강조하지 않았으나 AI가 중요하다고 본 항목은 AI 절에만 있어야 한다
    if "완전 비탄성 충돌" in emph:
        fails.append("교수가 강조하지 않은 항목이 교수님 강조 절에 있다")
    if not re.search(r"\(raw/transcripts/[^)]+,\s*\d\d:\d\d:\d\d\)", emph):
        fails.append("교수 발언에 원본 경로+타임스탬프가 없다")

    asm = notes.get("ASM-general-physics-2-20260908-01")
    if not asm:
        fails.append("Assignment가 생성되지 않았다")
    exm = notes.get("EXM-general-physics-2-2026-2-midterm")
    if not exm:
        fails.append("EXM이 없다")
    elif len(exm["fm"]["sources"]) < 2:
        fails.append("EXM이 근거를 누적할 수 있는 형태가 아니다")
    if not by_type("course-fact"):
        fails.append("Course Fact가 생성되지 않았다")
    if len(by_type("question")) < 2:
        fails.append("학생 질문이 QST로 추출되지 않았다")
    rq = section(b, "Review Questions") or ""
    if "(AI 생성)" not in rq:
        fails.append("Review Question에 AI 생성 표시가 없다")
    if not lec["fm"]["resources"] or lec["fm"]["resources"][0].get("pages") != "21-38":
        fails.append("PPT 페이지 범위가 기록되지 않았다")
    # 결정적 대시보드: 자동 관리 영역이 조회 결과와 일치하는가
    crs = notes["CRS-2026-2-general-physics-2"]
    auto = re.search(r"<!-- AUTO-MANAGED:start -->\n(.*?)<!-- AUTO-MANAGED:end -->",
                     crs["body"], re.S).group(1)
    listed = set(re.findall(r"^- ([A-Z]{3}-[a-z0-9-]+) ", auto, re.M))
    expected = {i for i, n in notes.items()
                if n["fm"].get("course") == crs["fm"]["id"] and i != crs["fm"]["id"]}
    if listed != expected:
        fails.append(f"대시보드 불일치: 누락 {sorted(expected - listed)} / 잉여 {sorted(listed - expected)}")
    order = re.findall(r"^- ([A-Z]{3}-[a-z0-9-]+) ", auto, re.M)
    TYPE_ORDER = ["LEC", "ASM", "EXM", "FAC", "RES"]
    def key(i):
        p = i[:3]
        return (TYPE_ORDER.index(p) if p in TYPE_ORDER else len(TYPE_ORDER) + ord(p[0]), i)
    if order != sorted(order, key=key):
        warn.append("대시보드 정렬이 SECOND-BRAIN 2.9의 타입 순서와 다르다")
record("A Lecture Ingestion", fails, warn)

# ================================================================ Scenario B
fails, warn = [], []
res_notes = [n for n in notes.values() if n["fm"]["type"] == "resource"]
ch03 = [n for n in res_notes if "ch03" in n["fm"]["id"]]
if len(ch03) != 1:
    fails.append(f"같은 자료의 RES가 {len(ch03)}개다. 1개여야 한다")
else:
    r = ch03[0]
    rid = r["fm"]["id"]
    fwd = {}   # LEC -> pages
    for lid, n in by_type("lecture").items():
        for item in (n["fm"].get("resources") or []):
            if item["id"] == rid:
                fwd[lid] = item.get("pages")
    if len(fwd) != 4:
        fails.append(f"이 RES를 참조하는 LEC이 {len(fwd)}개다. 4개여야 한다")
    if len(set(fwd.values())) != len(fwd):
        fails.append("Lecture별 page range가 보존되지 않았다")
    back = set(r["fm"]["lectures"])
    if back != set(fwd):
        fails.append(f"양방향 drift: Resource.lectures={sorted(back)} vs 정방향={sorted(fwd)}")
    # Resource 쪽에서 사용 관계를 재구성할 수 있는가
    usage = section(r["body"], "Lecture Usage") or ""
    for lid, pages in fwd.items():
        if lid not in usage or pages not in usage:
            warn.append(f"Lecture Usage 요약에 {lid} {pages}가 없다")
    # 재등록 시 새 RES를 만들지 않는가: 같은 source를 가리키는 RES가 1개인지
    same_src = [n for n in res_notes if n["fm"]["source"] == r["fm"]["source"]]
    if len(same_src) != 1:
        fails.append("같은 원본을 가리키는 RES가 여러 개다")
record("B Resource N:N", fails, warn)

# ================================================================ Scenario C
fails, warn = [], []
cons = by_type("concept")
alias_map = {}
for cid, n in cons.items():
    for a in [n["fm"]["title"]] + (n["fm"].get("aliases") or []):
        alias_map.setdefault(a.strip().lower(), set()).add(cid)
for expr in ("운동량", "momentum", "linear momentum"):
    hit = alias_map.get(expr.lower(), set())
    if len(hit) == 0:
        fails.append(f"표현 '{expr}'로 기존 Concept를 찾을 수 없다")
    elif len(hit) > 1:
        fails.append(f"표현 '{expr}'가 Concept {sorted(hit)}로 갈렸다")
mom = {c for e in ("운동량", "momentum", "linear momentum") for c in alias_map.get(e.lower(), set())}
if len(mom) > 1:
    fails.append(f"같은 개념이 여러 CON으로 나뉘었다: {sorted(mom)}")
# SECOND-BRAIN 2.7이 정한 항목 형태만 registry로 읽는다.
# 규칙 설명 불릿을 topic으로 오인하지 않기 위해 "- <slug> — ..." 형태를 요구한다.
topics_reg = set(re.findall(r"^- ([a-z0-9-]+) — ",
                            (V / "wiki/clusters/_topics.md").read_text(encoding="utf-8"), re.M))
for nid, n in notes.items():
    for tp in (n["fm"].get("topics") or []):
        if tp not in topics_reg:
            fails.append(f"{n['rel']}: 미등록 topic '{tp}'")
# Concept identity와 topic vocabulary가 1:1로 강제되는가
con_slugs = {c.split("-", 1)[1] for c in cons}
if con_slugs != topics_reg:
    warn.append(f"CON slug와 topic 어휘가 1:1이 아니다 (설계상 정상). CON={sorted(con_slugs)} topics={sorted(topics_reg)}")
record("C Concept Deduplication", fails, warn)

# ================================================================ Scenario D
fails, warn = [], []
CASES = {"ASM-general-physics-2-20260908-01": ("2026-09-18", "confirmed", "9월 18일"),
         "ASM-general-physics-2-20260908-02": (None, "needs-review", "다음 주까지"),
         "ASM-general-physics-2-20260908-03": (None, "needs-review", "다음 수업 전에"),
         "ASM-general-physics-2-20260908-04": (None, "needs-review", "금요일쯤")}
for aid, (due, dstat, quote) in CASES.items():
    n = notes.get(aid)
    if not n:
        fails.append(f"{aid} 없음")
        continue
    got = n["fm"]["due"]
    got = got.isoformat() if hasattr(got, "isoformat") else got
    if due is None:
        if got is not None:
            fails.append(f"{aid}: 애매한 표현 '{quote}'인데 due를 {got}로 지어냈다")
    elif got != due:
        fails.append(f"{aid}: due가 {got}다. {due}여야 한다")
    if n["fm"]["due_status"] != dstat:
        fails.append(f"{aid}: due_status가 {n['fm']['due_status']}다. {dstat}여야 한다")
    if quote not in n["body"]:
        fails.append(f"{aid}: 원문 표현 '{quote}'가 본문에 없다")
record("D Assignment 날짜", fails, warn)

# ================================================================ Scenario E
fails, warn = [], []
old = notes.get("FAC-general-physics-2-20260901-01")
c1 = notes.get("FAC-general-physics-2-20260908-01")
c2 = notes.get("FAC-general-physics-2-20260909-01")
c3 = notes.get("FAC-general-physics-2-20260910-01")
if not old or not old["path"].exists():
    fails.append("Case 1: 이전 Fact 파일이 삭제됐다")
if old and old["fm"]["status"] != "superseded":
    fails.append(f"Case 1: 이전 Fact status가 {old['fm']['status']}다")
if not c1 or "FAC-general-physics-2-20260901-01" not in (c1["fm"].get("supersedes") or []):
    fails.append("Case 1: 새 Fact에 supersedes가 기록되지 않았다")
if c1 and c1["fm"]["status"] != "active":
    fails.append("Case 1: 새 Fact가 active가 아니다")
for nid, n in notes.items():
    if "superseded_by" in n["fm"]:
        fails.append(f"{n['rel']}: superseded_by 필드가 저장됐다 (단방향 정책 위반)")
for label, n in (("Case 2", c2), ("Case 3", c3)):
    if not n:
        fails.append(f"{label} Fact 없음")
        continue
    if n["fm"]["status"] != "needs-review":
        fails.append(f"{label}: status가 {n['fm']['status']}다. needs-review여야 한다")
    if n["fm"].get("supersedes"):
        fails.append(f"{label}: 자동 supersede가 적용됐다")
    if n["fm"]["value"] is not None:
        fails.append(f"{label}: 확정 Fact로 값을 채웠다")
exm = notes.get("EXM-general-physics-2-2026-2-midterm")
if exm and exm["fm"]["date_status"] == "confirmed":
    fails.append("상충이 남아 있는데 EXM date_status가 confirmed다")
# supersedes 순환/자기참조
for nid, n in by_type("course-fact").items():
    if nid in (n["fm"].get("supersedes") or []):
        fails.append(f"{nid}: supersedes 자기 참조")
record("E Course Fact Conflict", fails, warn)

# ================================================================ Scenario F
fails, warn = [], []
pex = by_type("past-exam")
if len(pex) != 3:
    fails.append(f"PEX가 {len(pex)}개다. 3개여야 한다")
recur = [p for p in pex.values() if "CON-momentum" in (p["fm"].get("concepts") or [])]
if len(recur) != 3:
    fails.append("반복 출제 개념이 3개 회차 모두에 연결되지 않았다")
for p in pex.values():
    ev = section(p["body"], "출제 경향의 근거") or ""
    if "표본" not in ev:
        fails.append(f"{p['rel']}: 표본 수 기록이 없다")
    # 긍정 예측만 잡는다. "확정하는 근거가 아니다" 같은 부인 문장은 정상이다.
    if re.search(r"(이번 시험에.{0,12}(출제|나온다|나올)|출제가 확정|확정적으로)", ev):
        fails.append(f"{p['rel']}: 현재 시험 출제를 확정하는 서술이 있다")
    if not re.search(r"(아니다|않는다|확정하지)", ev):
        fails.append(f"{p['rel']}: 출제 확정이 아니라는 표시가 없다")
    if p["fm"]["status"] == "analyzed" and p["fm"]["provenance"] == "reconstructed":
        warn.append(f"{p['rel']}: 복원본인데 analyzed다. 정답 검증 여부 확인 필요")
if exm:
    scope = section(exm["body"], "확정 범위") or ""
    aip = section(exm["body"], "AI 예상 / 검증 필요") or ""
    prof = section(exm["body"], "교수님 시험 언급") or ""
    if re.search(r"(기출|자료 p\.|AI 해석)", scope):
        fails.append("확정 범위 절에 기출·자료 강조·AI 해석이 섞였다")
    for kind, pat, sec, label in (("기출 빈도", "기출", aip, "AI 예상"),
                                  ("자료 강조", "자료 p.", aip, "AI 예상"),
                                  ("교수 발언", "출제 명시", prof, "교수님 시험 언급")):
        if pat not in sec:
            warn.append(f"{kind} 근거가 {label} 절에서 확인되지 않는다")
    if not set(exm["fm"]["related"] or []) | {p for p in pex} & set(
            re.findall(r"PEX-[a-z0-9-]+", exm["body"])):
        warn.append("EXM과 PEX 연결이 본문에서 확인되지 않는다")
record("F Past Exam", fails, warn)

# ================================================================ Scenario G/J
fails, warn = [], []


def protected_blocks(text):
    out = {}
    for title in PROTECTED:
        s = section(text, title)
        if s is not None:
            out[title] = s
    return out


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


before = {}
for nid, n in notes.items():
    for title, blk in protected_blocks(n["body"]).items():
        before[f"{nid}::{title}"] = digest(blk)


def simulate_reingest(text):
    """L1 재실행이 문서상 허용하는 수정만 가한다. 보호 영역은 건드리지 않는다."""
    def repl(m):
        return m.group(0).replace("(AI 요약)", "(AI 요약, 재처리 2026-09-20)")
    text = re.sub(r"^## 수업 요약\n(?:.*\n)*?(?=^## )", repl, text, count=1, flags=re.M)
    return text.replace("updated: 2026-09-08", "updated: 2026-09-20", 1)


lec_path = notes["LEC-20260908-01"]["path"]
orig = lec_path.read_text(encoding="utf-8")
lec_path.write_text(simulate_reingest(orig), encoding="utf-8")
after_txt = lec_path.read_text(encoding="utf-8")
after_body = re.match(r"^---\n(.*?)\n---\n(.*)$", after_txt, re.S).group(2)
for title, blk in protected_blocks(after_body).items():
    k = f"LEC-20260908-01::{title}"
    if before.get(k) != digest(blk):
        fails.append(f"재처리 후 보호 영역이 변경됐다: {k}")
if "재처리 2026-09-20" not in after_txt:
    fails.append("재처리 시뮬레이션이 적용되지 않았다")
lec_path.write_text(orig, encoding="utf-8")   # 원복

n_protected = len(before)
if n_protected < 5:
    warn.append(f"보호 영역 fixture가 {n_protected}개뿐이다")
SNAP.write_text(json.dumps(before, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8")
record("G Protected Sections", fails, warn)

# ---- Scenario J: 재실행 안전성
fails, warn = [], []
seen = {}
for lid, n in by_type("lecture").items():
    k = (n["fm"]["course"], str(n["fm"]["date"]))
    if k in seen:
        fails.append(f"같은 course+date의 LEC 중복: {seen[k]} / {lid}")
    seen[k] = lid
titles = [n["fm"]["title"] for n in by_type("assignment").values()]
if len(titles) != len(set(titles)):
    fails.append("같은 제목의 Assignment가 중복 생성됐다")
for nid, n in notes.items():
    for k in ("sources", "concepts", "lectures", "members", "targets", "related"):
        v = [x["id"] if isinstance(x, dict) else x for x in (n["fm"].get(k) or [])]
        if len(v) != len(set(v)):
            fails.append(f"{n['rel']}: {k}에 중복 항목 (재실행 append 누수)")
crs = notes["CRS-2026-2-general-physics-2"]
auto = re.search(r"<!-- AUTO-MANAGED:start -->\n(.*?)<!-- AUTO-MANAGED:end -->",
                 crs["body"], re.S).group(1)
dash = re.findall(r"^- ([A-Z]{3}-[a-z0-9-]+) ", auto, re.M)
if len(dash) != len(set(dash)):
    fails.append("Course 대시보드에 중복 항목이 있다")
tr_dir = V / "raw/transcripts"
tr_files = list(tr_dir.glob("*general-physics-2-01*"))
if len(tr_files) != 1:
    fails.append(f"같은 전사 원본이 {len(tr_files)}개로 복제됐다")
log = (V / "_system/log.md").read_text(encoding="utf-8")
log_lines = [l for l in log.splitlines() if l.startswith("- 20")]
if len(log_lines) != len(set(log_lines)):
    fails.append("log에 완전히 동일한 줄이 중복됐다")
if not any("| partial |" in l for l in log_lines):
    warn.append("log에 partial 줄이 없어 재개 시나리오를 검증할 수 없다")
record("J Re-ingestion / Idempotency", fails, warn)

# ================================================================ Scenario K
fails, warn = [], []
CODES = {"preserve-source", "create-note", "update-note", "sync-relations", "register-topic",
         "reconcile-fact", "refresh-dashboard", "record-review", "promote-pattern",
         "merge-duplicate", "finalize-run"}
parsed = []
for l in log_lines:
    parts = [p.strip() for p in l.lstrip("- ").split("|")]
    if len(parts) != 6:
        fails.append(f"log 형식 위반: {l}")
        continue
    parsed.append(parts)
    if parts[2] not in CODES:
        fails.append(f"log에 승인되지 않은 작업 코드 '{parts[2]}'")
    if parts[4] not in ("done", "partial", "held", "conflict"):
        fails.append(f"log에 잘못된 결과값 '{parts[4]}'")
# partial 이후 같은 대상+레이어+코드의 done이 있어야 복구 완료로 본다
part = [p for p in parsed if p[4] == "partial"]
for p in part:
    idx = parsed.index(p)
    later = [q for q in parsed[idx + 1:]
             if q[1] == p[1] and q[2] == p[2] and q[3] == p[3] and q[4] == "done"]
    if not later:
        warn.append(f"partial({p[3]}, {p[1]}, {p[2]})에 대응하는 done이 없다 (미복구 상태)")
# 실패가 학습 노트 status로 표현되지 않았는가
for nid, n in notes.items():
    if str(n["fm"]["status"]) in ("partial", "failed", "error"):
        fails.append(f"{n['rel']}: 실행 실패를 status로 표현했다")
# 부분 실패 이전 단계 결과가 남아 있는가
if not (V / "raw/transcripts/2026-09-08-general-physics-2-01.md").exists():
    fails.append("부분 실패 후 raw 원본이 유실됐다")
if "LEC-20260908-01" not in notes:
    fails.append("부분 실패 후 Lecture가 유실됐다")
record("K Partial Failure / Recovery", fails, warn)

# ================================================================ Scenario H
fails, warn = [], []
# 근거 요청형 질문은 structured note만으로 확정할 수 없어야 한다
asm_b = notes["ASM-general-physics-2-20260908-02"]
if asm_b["fm"]["due"] is not None:
    fails.append("마감 근거 질문의 대상 ASM이 이미 확정돼 Evidence Recall이 불필요해졌다")
if not asm_b["fm"]["sources"]:
    fails.append("ASM에 sources가 없어 raw로 확장할 경로가 없다")
else:
    lid = asm_b["fm"]["sources"][0]
    src = notes[lid]["fm"].get("source")
    if not src or not (V / src).exists():
        fails.append("sources -> source -> raw 경로가 끊겼다")
    else:
        if "다음 주까지 제출하세요" not in (V / src).read_text(encoding="utf-8"):
            fails.append("원문에서 마감 발언을 찾을 수 없다")
if exm and exm["fm"]["scope_status"] == "confirmed":
    fails.append("시험 범위가 근거 없이 confirmed다")
# 일반 Recall은 구조화 노트만으로 답할 수 있어야 한다
mom_note = notes["CON-momentum"]
if not mom_note["fm"]["sources"]:
    fails.append("CON-momentum에 sources가 없어 근거 ID를 붙일 수 없다")
if not (section(mom_note["body"], "정의") or "").strip():
    fails.append("CON-momentum 정의가 비어 일반 Recall만으로 답할 수 없다")
raw_only = [f for f in (V / "raw").rglob("*.md")]
if len(raw_only) < 4:
    warn.append("raw fixture가 적어 Evidence Recall 확장 범위 검증이 제한적이다")
record("H Evidence Recall", fails, warn)

# ================================================================ Scenario I
fails, warn = [], []


def mk(kind, **kw):
    """common.md의 Type별 권장 형태를 그대로 적용한다."""
    return {
        "EXM": "EXM-{course}-{term}-{exam_type}",
        "RES": "RES-{course}-{res}",
        "REV": "REV-{course}-{date}-{review_type}",
        "CRS": "CRS-{term}-{course}",
        "PEX": "PEX-{course}-{year}-{sem}-{exam_type}",
        "ASM": "ASM-{course}-{date}-{nn}",
    }[kind].format(**kw)


SITU = [
    # 같은 과목을 여러 학기에 수강하는 상황. EXM은 <term>을 쓰므로 학기별로 갈린다.
    ("2026-1 일반물리학2 중간고사", mk("EXM", course="general-physics-2", term="2026-1", exam_type="midterm")),
    ("2026-2 일반물리학2 중간고사", mk("EXM", course="general-physics-2", term="2026-2", exam_type="midterm")),
    ("2026-여름 계절학기 중간고사", mk("EXM", course="general-physics-2", term="2026-summer", exam_type="midterm")),
    ("2027-1 재수강 중간고사", mk("EXM", course="general-physics-2", term="2027-1", exam_type="midterm")),
    ("2026-1 퀴즈 3회", mk("EXM", course="general-physics-2", term="2026-1", exam_type="quiz-03")),
    ("2026-2 퀴즈 3회", mk("EXM", course="general-physics-2", term="2026-2", exam_type="quiz-03")),
    ("2026-1 기말고사", mk("EXM", course="general-physics-2", term="2026-1", exam_type="final")),
    ("2026-1 Chapter 3 Slides", mk("RES", course="general-physics-2", res="ch03-slides")),
    ("2026-2 Chapter 3 Slides", mk("RES", course="general-physics-2", res="ch03-slides")),
    ("2026-1 주간복습 03-15", mk("REV", course="general-physics-2", date="20260315", review_type="weekly")),
    ("2026-2 주간복습 09-13", mk("REV", course="general-physics-2", date="20260913", review_type="weekly")),
    ("2026-1 Course", mk("CRS", term="2026-1", course="general-physics-2")),
    ("2026-2 Course", mk("CRS", term="2026-2", course="general-physics-2")),
    ("2027-1 재수강 Course", mk("CRS", term="2027-1", course="general-physics-2")),
    ("2024-2 기출", mk("PEX", course="general-physics-2", year="2024", sem="2", exam_type="midterm")),
    ("2024-1 기출", mk("PEX", course="general-physics-2", year="2024", sem="1", exam_type="midterm")),
]
seen = {}
collisions = []
for label, gid in SITU:
    if not ID_CONTRACT.match(gid):
        fails.append(f"권장 형태가 ID 형식 계약을 위반한다: {gid}")
    if gid in seen:
        collisions.append((gid, seen[gid], label))
    seen[gid] = label
for gid, a, b in collisions:
    if gid.startswith("RES-"):
        warn.append(f"RES 재사용(설계상 정상): {gid} <- '{a}' / '{b}'. 같은 자료는 RES 하나를 공유한다")
    else:
        fails.append(f"ID 충돌: {gid} <- '{a}' / '{b}'")

# 회귀 방지: 문서가 EXM 권장 형태를 <term>으로 유지하는지 직접 확인한다.
# 연도만 쓰는 형태로 되돌아가면 여기서 FAIL이 난다.
cm = (SCH / "common.md").read_text(encoding="utf-8")
row = re.search(r"^\| exam \| `([^`]+)` \| `([^`]+)` \|", cm, re.M)
if not row:
    fails.append("common.md에서 exam ID 권장 형태 행을 찾지 못했다")
else:
    shape, example = row.group(1), row.group(2)
    if "<term>" not in shape:
        fails.append(f"common.md의 exam 권장 형태가 <term>을 쓰지 않는다: {shape}")
    if "<연도>" in shape:
        fails.append("common.md의 exam 권장 형태가 <연도>로 되돌아갔다. 학기 간 충돌이 재발한다")
    if not ID_CONTRACT.match(example):
        fails.append(f"common.md의 exam 예시가 형식 계약을 위반한다: {example}")
    if example != "EXM-general-physics-2-2026-2-midterm":
        warn.append(f"common.md의 exam 예시가 바뀌었다: {example}")
ex_md = (SCH / "exam.md").read_text(encoding="utf-8")
if "<연도>" in re.search(r"^## Identity.*?(?=\Z|^## )", ex_md, re.M | re.S).group(0):
    fails.append("exam.md의 Identity 절이 여전히 <연도>를 권장한다")

# 나머지 Type이 실제로 안전한지 확인
SAFE = [
    ("ASM 2026-1/2026-2", "ASM-general-physics-2-20260315-01", "ASM-general-physics-2-20260908-01"),
    ("REV 2026-1/2026-2", "REV-general-physics-2-20260315-weekly", "REV-general-physics-2-20260913-weekly"),
    ("PEX 2024-2/2024-1", "PEX-general-physics-2-2024-2-midterm", "PEX-general-physics-2-2024-1-midterm"),
    ("CRS 2026-1/2026-2", "CRS-2026-1-general-physics-2", "CRS-2026-2-general-physics-2"),
]
for label, a, b in SAFE:
    if a == b:
        fails.append(f"{label}: 권장 형태가 충돌한다")
record("I ID 충돌 압박", fails, warn)

# ================================================================ L8 탐지
fails, warn = [], []
detected = {}
for f in sorted(BROKEN.glob("bad-*.md")):
    raw = f.read_text(encoding="utf-8")
    hits = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        hits.append("frontmatter 없음")
    else:
        try:
            fmb = yaml.safe_load(m.group(1))
        except Exception:
            hits.append("항목1 invalid YAML")
            fmb = None
        if fmb:
            t = fmb.get("type")
            i = str(fmb.get("id", ""))
            if t in PREFIX and not i.startswith(PREFIX[t] + "-"):
                hits.append("항목3 접두사 불일치")
            if not ID_CONTRACT.match(i):
                hits.append("항목3 ID 형식 위반")
            if t in spec and fmb.get("status") not in spec[t]["status"]:
                hits.append("항목2 status 불허")
            refs = [r for k in ("related", "sources", "supersedes", "concepts")
                    for r in (fmb.get(k) or [])]
            for r in refs:
                if isinstance(r, str) and r not in IDS:
                    hits.append("항목4/9 없는 ID 참조")
                    break
            src = fmb.get("source")
            if isinstance(src, str) and not src.startswith("http") and not (V / src).exists():
                hits.append("항목6 source 파일 없음")
            for tp in (fmb.get("topics") or []):
                if tp not in topics_reg:
                    hits.append("항목7 미등록/중복 topic")
                    break
            al = {a.lower() for a in (fmb.get("aliases") or [])}
            if al & {a for k, v in alias_map.items() for a in [k]}:
                hits.append("L9 중복 개념 후보")
            if not refs and not (fmb.get("sources") or []) and t == "concept" and "orphan" in i:
                hits.append("항목4 orphan 후보")
    detected[f.name] = hits
    if not hits:
        fails.append(f"{f.name}: 심은 오류를 하나도 탐지하지 못했다")
record("L8 오류 탐지", fails, warn)

# ================================================================ 출력
print("=" * 68)
print("Study Brain 통합 시험 — Scenario 결과")
print("=" * 68)
order = ["공통 스키마 적합성", "A Lecture Ingestion", "B Resource N:N",
         "C Concept Deduplication", "D Assignment 날짜", "E Course Fact Conflict",
         "F Past Exam", "G Protected Sections", "H Evidence Recall", "I ID 충돌 압박",
         "J Re-ingestion / Idempotency", "K Partial Failure / Recovery", "L8 오류 탐지"]
nfail = 0
for k in order:
    v, det = results[k]
    if v == "FAIL":
        nfail += 1
    print(f"\n[{v}] {k}")
    for d in det:
        print(f"    - {d}")

print("\n" + "-" * 68)
print("L8 fixture별 탐지 결과")
for name, hits in detected.items():
    print(f"  {name:28} {', '.join(hits) if hits else '탐지 실패'}")

print("\n" + "=" * 68)
tally = {}
for v, _ in results.values():
    tally[v] = tally.get(v, 0) + 1
print("  " + " / ".join(f"{k}: {n}" for k, n in sorted(tally.items())))
print(f"  보호 영역 {n_protected}개 해시 기록 -> {SNAP.name}")
print("=" * 68)
sys.exit(1 if nfail else 0)
