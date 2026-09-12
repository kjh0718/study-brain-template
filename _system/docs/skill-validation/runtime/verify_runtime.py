"""Runtime Test A~F 검증. Skill을 따라 실행한 결과가 규칙과 맞는지 기계적으로 확인한다.

구조 검사(check_skills.py)와 다르다. 이 스크립트는 **실행 결과물**을 본다.

    python seed_workspace.py     # 최초 1회
    (Skill을 따라 workspace에서 실행)
    python verify_runtime.py

종료 코드 0이면 FAIL 없음. 표준 라이브러리 + PyYAML만 쓴다.
"""
import hashlib, json, pathlib, re, sys, yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCH = ROOT / "_system/schemas"
WS = HERE / "workspace"
SEED = json.loads((HERE / "seed-manifest.json").read_text(encoding="utf-8"))
CANON = ROOT / ".agents/skills"

ID_CONTRACT = re.compile(
    r"^(?:CRS|LEC|CON|ASM|EXM|PEX|FAC|QST|RES|REV|CLU)-[a-z0-9]+(?:-[a-z0-9]+)*$")
OPTIONAL = {"course": {"code", "term", "instructor"}, "lecture": {"week"},
            "resource": {"page_count"}, "assignment": {"submission_method"},
            "course-fact": {"effective_from"}}
CODES = {"preserve-source", "create-note", "update-note", "sync-relations", "register-topic",
         "reconcile-fact", "refresh-dashboard", "record-review", "promote-pattern",
         "merge-duplicate", "finalize-run"}

results = {}


def record(name, fails, notes_):
    results[name] = ("FAIL" if fails else ("PASS WITH NOTES" if notes_ else "PASS"),
                     fails + notes_)


spec = {}
for f in SCH.glob("*.md"):
    if f.name in ("README.md", "common.md"):
        continue
    txt = f.read_text(encoding="utf-8")
    ex = yaml.safe_load(re.search(r"^```yaml\n(.*?)^```$", txt, re.M | re.S).group(1).strip().strip("-"))
    ms = re.search(r"^## Status(?: Values)?\s*$", txt, re.M)
    st = set(re.findall(r"^- `?([a-z-]+)`?:",
                        re.split(r"^## ", txt[ms.end():], maxsplit=1, flags=re.M)[0], re.M))
    spec[f.stem] = {"fields": set(ex), "required": set(ex) - OPTIONAL.get(f.stem, set()),
                    "status": st}

notes = {}
for f in sorted(WS.rglob("*.md")):
    rel = f.relative_to(WS)
    if rel.parts[0] in ("raw", "_system") or f.name == "_topics.md":
        continue
    raw = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if m:
        fm = yaml.safe_load(m.group(1))
        notes[fm["id"]] = {"rel": rel, "fm": fm, "body": m.group(2), "path": f}
IDS = set(notes)


def sec(body, title):
    m = re.search(rf"^## {re.escape(title)}\s*$", body, re.M)
    if not m:
        return None
    rest = body[m.end():]
    n = re.search(r"^## ", rest, re.M)
    return rest[:n.start()] if n else rest


# ---------------------------------------------------------- 공통 스키마 적합성
fails, warn = [], []
for nid, n in notes.items():
    t, rel, fm = n["fm"]["type"], n["rel"], n["fm"]
    s = spec[t]
    if s["required"] - set(fm):
        fails.append(f"{rel}: 필수 필드 누락 {sorted(s['required'] - set(fm))}")
    if set(fm) - s["fields"]:
        fails.append(f"{rel}: 스키마에 없는 필드 {sorted(set(fm) - s['fields'])}")
    if fm["status"] not in s["status"]:
        fails.append(f"{rel}: status '{fm['status']}' 불허")
    if not ID_CONTRACT.match(nid):
        fails.append(f"{rel}: ID 형식 계약 위반 {nid}")
    for k in ("related", "concepts", "questions", "assignments", "exams", "course_facts",
              "sources", "answer_sources", "targets", "members", "lectures", "supersedes"):
        for r in (fm.get(k) or []):
            r = r["id"] if isinstance(r, dict) else r
            if isinstance(r, str) and re.match(r"^[A-Z]{3}-", r) and r not in IDS:
                fails.append(f"{rel}: {k}의 {r} 대상 노트 없음")
    for k in ("course", "subject"):
        v = fm.get(k)
        if isinstance(v, str) and re.match(r"^[A-Z]{3}-", v) and v not in IDS:
            fails.append(f"{rel}: {k}의 {v} 대상 노트 없음")
    src = fm.get("source")
    if isinstance(src, str) and not src.startswith("http") and not (WS / src).exists():
        fails.append(f"{rel}: source 파일 없음 {src}")
record("공통 스키마 적합성", fails, warn)

# ---------------------------------------------------------- A: capture 라우팅 결정성
fails, warn = [], []
cap = (CANON / "capture/SKILL.md").read_text(encoding="utf-8")
rows = re.findall(r"^\s*\| (.+?) \| \[(.+?)\]\(.+?\) — (L\d) \|", cap, re.M)
if len(rows) < 4:
    fails.append(f"capture 라우팅 표 행이 {len(rows)}개다. 4개 이상이어야 한다")
KEYS = {r[1]: [k.strip() for k in r[0].replace("·", " ").split()] for r in rows}
CASES = [
    ("A 전사", "일반물리학2 전체 전사본", "ingest-lecture"),
    ("B 자료", "교수님이 올린 Chapter 3 PPT", "ingest-resource"),
    ("C 기출", "2024년 중간고사 족보", "ingest-past-exam"),
    ("D 모호", "이거 넣어줘", None),
]
for label, text, expect in CASES:
    hit = [skill for skill, keys in KEYS.items() if any(k and k in text for k in keys)]
    if expect is None:
        if hit:
            fails.append(f"{label}: 종류가 불명확한데 {hit}로 라우팅됐다. 물어야 한다")
    elif hit != [expect]:
        fails.append(f"{label}: {hit}로 라우팅. {expect} 하나여야 한다")
if "여기서 멈춘다" not in cap or "묻는다" not in cap:
    fails.append("capture에 모호 입력 중단 규칙이 없다")
record("A capture 라우팅", fails, warn)

# ---------------------------------------------------------- C: maintain 읽기 전용
fails, warn = [], []
cur = {}
for f in sorted(WS.rglob("*")):
    if f.is_file():
        cur[str(f.relative_to(WS)).replace("\\", "/")] = hashlib.sha256(f.read_bytes()).hexdigest()
raw_changed = [p for p in SEED if p.startswith("raw/") and cur.get(p) != SEED[p]]
if raw_changed:
    fails.append(f"raw 원본이 변경됐다: {raw_changed}")
mt = (CANON / "maintain/SKILL.md").read_text(encoding="utf-8")
for phrase in ("기본은 검사 모드다", "파일을 고치거나 로그를 쓰지 않는다", "범위를 추정해 고치지 않는다"):
    if phrase not in mt:
        fails.append(f"maintain에 '{phrase}' 규칙이 없다")
record("C maintain 읽기 전용", fails, warn)

# ---------------------------------------------------------- D: ingest-lecture 결과
fails, warn = [], []
lec = notes.get("LEC-20260908-01")
if not lec:
    fails.append("LEC이 생성되지 않았다")
else:
    b = lec["body"]
    tr = "raw/transcripts/2026-09-08-general-physics-2-01.md"
    if lec["fm"]["source"] != tr:
        fails.append("LEC.source가 보존된 전사를 가리키지 않는다")
    if cur.get(tr) != SEED.get(tr):
        fails.append("전사 원문이 변경됐다")
    emph, ai = sec(b, "교수님 강조") or "", sec(b, "AI 해석 / 검증 필요") or ""
    if not re.search(r"\(raw/transcripts/[^)]+,\s*\d\d:\d\d:\d\d\)", emph):
        fails.append("교수 발언에 원본 경로+타임스탬프가 없다")
    if "AI 해석" in emph:
        fails.append("교수님 강조 절에 AI 해석이 섞였다")
    if "(AI 해석)" not in ai:
        fails.append("AI 해석 절에 AI 표시가 없다")
    if "(AI 생성)" not in (sec(b, "Review Questions") or ""):
        fails.append("Review Question에 AI 생성 표시가 없다")
    if lec["fm"].get("week") is not None:
        warn.append("원문에 주차 언급이 없는데 week가 채워졌다")
    r = lec["fm"]["resources"]
    if not r or r[0].get("pages") != "21-38":
        fails.append("자료 페이지 범위가 기록되지 않았다")
    else:
        res = notes.get(r[0]["id"])
        if not res:
            fails.append("참조한 RES가 없다")
        elif "LEC-20260908-01" not in (res["fm"]["lectures"] or []):
            fails.append("Lecture->Resource 역방향이 없다")
# 개념: 기존 연결 + 신규 생성
mom = [i for i, n in notes.items() if n["fm"]["type"] == "concept"
       and "운동량" in (n["fm"]["title"] + " ".join(n["fm"].get("aliases") or []) + " momentum")]
if len([i for i, n in notes.items() if n["fm"]["type"] == "concept"]) != 2:
    fails.append("Concept 개수가 2개가 아니다 (기존 1 보강 + 신규 1)")
cm = notes.get("CON-momentum")
if cm and "LEC-20260908-01" not in (cm["fm"]["sources"] or []):
    fails.append("기존 CON-momentum에 이번 근거가 추가되지 않았다")
ci = notes.get("CON-impulse")
if not ci:
    fails.append("CON-impulse가 생성되지 않았다")
elif len(ci["fm"]["sources"] or []) < 2:
    fails.append("CON-impulse의 독립 근거가 2개 미만인데 생성됐다")
# topic 등록
reg = set(re.findall(r"^- ([a-z0-9-]+) — ",
                     (WS / "wiki/clusters/_topics.md").read_text(encoding="utf-8"), re.M))
for n in notes.values():
    for tp in (n["fm"].get("topics") or []):
        if tp not in reg:
            fails.append(f"{n['rel']}: 미등록 topic '{tp}'")
if "impulse" not in reg:
    fails.append("새 topic impulse가 어휘표에 등록되지 않았다")
if len([i for i, n in notes.items() if n["fm"]["type"] == "question"]) != 2:
    fails.append("학생 질문 2건이 QST로 추출되지 않았다")
# 대시보드 결정성
crs = notes.get("CRS-2026-2-general-physics-2")
if crs:
    auto = re.search(r"<!-- AUTO-MANAGED:start -->\n(.*?)<!-- AUTO-MANAGED:end -->",
                     crs["body"], re.S).group(1)
    listed = set(re.findall(r"^- ([A-Z]{3}-[a-z0-9-]+) ", auto, re.M))
    expected = {i for i, n in notes.items()
                if n["fm"].get("course") == crs["fm"]["id"] and i != crs["fm"]["id"]}
    if listed != expected:
        fails.append(f"대시보드 불일치: 누락 {sorted(expected-listed)} / 잉여 {sorted(listed-expected)}")
# 로그
log = [l for l in (WS / "_system/log.md").read_text(encoding="utf-8").splitlines()
       if l.startswith("- 20")]
if not log:
    fails.append("로그가 기록되지 않았다")
for l in log:
    p = [x.strip() for x in l.lstrip("- ").split("|")]
    if len(p) != 6:
        fails.append(f"로그 형식 위반: {l[:50]}")
    elif p[2] not in CODES:
        fails.append(f"승인되지 않은 작업 코드 '{p[2]}'")
    elif p[4] not in ("done", "partial", "held", "conflict"):
        fails.append(f"잘못된 결과값 '{p[4]}'")
record("D ingest-lecture", fails, warn)

# ---------------------------------------------------------- E: check-conflict
fails, warn = [], []
old = notes.get("FAC-general-physics-2-20260901-01")
new = notes.get("FAC-general-physics-2-20260908-01")
if not old:
    fails.append("기존 FAC가 사라졌다")
if not new:
    fails.append("이번 언급의 FAC가 없다")
else:
    if new["fm"]["status"] != "needs-review":
        fails.append(f"추측 표현인데 status가 {new['fm']['status']}다")
    if new["fm"]["value"] is not None:
        fails.append("추측 표현인데 value를 확정했다")
    if new["fm"].get("supersedes"):
        fails.append("변경 선언이 없는데 supersede가 적용됐다")
for n in notes.values():
    if "superseded_by" in n["fm"]:
        fails.append(f"{n['rel']}: superseded_by 필드 (단방향 정책 위반)")
asm = notes.get("ASM-general-physics-2-20260908-01")
if not asm:
    fails.append("ASM이 생성되지 않았다")
else:
    if asm["fm"]["due"] is not None:
        fails.append(f"모호한 마감인데 due를 {asm['fm']['due']}로 지어냈다")
    if asm["fm"]["due_status"] != "needs-review":
        fails.append(f"due_status가 {asm['fm']['due_status']}다")
    if "다음 주까지" not in asm["body"]:
        fails.append("원문 표현이 본문에 없다")
exms = [i for i, n in notes.items() if n["fm"]["type"] == "exam"]
if len(exms) != 1:
    fails.append(f"EXM이 {len(exms)}개다. 기존 하나에 누적해야 한다")
elif "LEC-20260908-01" not in (notes[exms[0]]["fm"]["sources"] or []):
    fails.append("EXM에 이번 근거가 누적되지 않았다")

# 명시적 변경(supersede) 전이
chg = notes.get("FAC-general-physics-2-20260910-01")
if not chg:
    warn.append("명시적 변경 FAC가 없다. supersede 전이를 검증하지 못했다")
else:
    if "FAC-general-physics-2-20260901-01" not in (chg["fm"].get("supersedes") or []):
        fails.append("명시적 변경인데 supersedes에 이전 FAC가 없다")
    if chg["fm"]["status"] != "active":
        fails.append(f"명시적 변경 FAC의 status가 {chg['fm']['status']}다")
    if chg["fm"]["value"] is None:
        fails.append("명시적 변경인데 value가 비어 있다")
    if old:
        if old["fm"]["status"] != "superseded":
            fails.append(f"대체된 FAC의 status가 {old['fm']['status']}다")
        if not old["path"].exists():
            fails.append("대체된 FAC 파일이 삭제됐다")
    if exms:
        e = notes[exms[0]]["fm"]
        d = e["date"].isoformat() if hasattr(e["date"], "isoformat") else str(e["date"])
        if d != "2026-10-17":
            fails.append(f"명시적 변경이 EXM.date에 반영되지 않았다 ({d})")
        if e["date_status"] != "confirmed":
            fails.append(f"근거가 확인됐는데 date_status가 {e['date_status']}다")
record("E check-conflict", fails, warn)

# ---------------------------------------------------------- B/F: Skill spec 분기 규칙
fails, warn = [], []
rc = (CANON / "recall/SKILL.md").read_text(encoding="utf-8")
if "Evidence Recall" not in rc:
    fails.append("recall이 Evidence Recall 분기를 언급하지 않는다")
if "읽기 전용" not in rc:
    fails.append("recall에 읽기 전용 규칙이 없다")
if "raw/` 전체를 읽지 않는다" not in rc:
    fails.append("recall에 raw 전체 읽기 금지 규칙이 없다")
rv = (CANON / "review/SKILL.md").read_text(encoding="utf-8")
if "exam-prep" not in rv:
    fails.append("review가 exam-prep을 언급하지 않는다")
if re.search(r"`exam`[^-]", rv):
    fails.append("review에 구 값 `exam`이 남아 있다")
if "완료 처리하지 않는다" not in rv:
    fails.append("review에 '문항 생성만으로 완료 금지' 규칙이 없다")
rvs = spec["review"]["fields"]
allowed = re.search(r"\| `review_type` \| 예 \| (.+?) \|",
                    (SCH / "review.md").read_text(encoding="utf-8")).group(1)
if "exam-prep" not in allowed or re.search(r"\bexam\b(?!-)", allowed):
    fails.append(f"review 스키마의 review_type 허용 값이 어긋난다: {allowed}")

# 실제로 만들어진 REV 결과물
revs = {i: n for i, n in notes.items() if n["fm"]["type"] == "review"}
types = {n["fm"]["review_type"] for n in revs.values()}
if "weekly" not in types:
    fails.append("weekly 복습 회차가 없다")
if "exam-prep" not in types:
    fails.append("exam-prep 복습 회차가 없다")
if "exam" in types:
    fails.append("구 값 'exam'으로 회차가 만들어졌다")
for i, n in revs.items():
    fm = n["fm"]
    if fm["review_type"] not in allowed.split(", "):
        fails.append(f"{n['rel']}: review_type '{fm['review_type']}'가 허용 값 밖")
    if not (fm.get("targets") or []):
        fails.append(f"{n['rel']}: targets가 비었는데 회차가 시작됐다")
    resp = sec(n["body"], "응답 / 관찰 결과") or ""
    if "미평가" in resp and fm["status"] == "completed":
        fails.append(f"{n['rel']}: 응답이 없는데 completed다")
    if fm["status"] == "completed" and fm["completed_on"] is None:
        fails.append(f"{n['rel']}: completed인데 completed_on이 없다")
    if fm["completed_on"] is not None and "미평가" in resp:
        fails.append(f"{n['rel']}: 미평가 항목이 있는데 completed_on이 채워졌다")
    body_all = n["body"]
    if re.search(r"이번 시험에.{0,12}(출제|나온다|나올)", body_all):
        fails.append(f"{n['rel']}: 시험 출제를 예측하는 서술이 있다")
    if "(AI 생성)" not in body_all:
        fails.append(f"{n['rel']}: AI 생성 표시가 없다")
record("B/F recall·review 분기 규칙", fails, warn)

# ---------------------------------------------------------- G: ingest-resource 재등록
fails, warn = [], []
res = [n for n in notes.values() if n["fm"]["type"] == "resource"]
if len(res) != 1:
    fails.append(f"RES가 {len(res)}개다. 같은 자료는 하나여야 한다")
else:
    r = res[0]
    if r["fm"]["id"] != "RES-general-physics-2-ch03-slides":
        fails.append(f"원본 확보 후 새 ID가 발급됐다: {r['fm']['id']}")
    src = r["fm"]["source"]
    if not src.startswith("raw/resources/"):
        fails.append(f"원본을 확보했는데 source가 {src}다")
    elif not (WS / src).exists():
        fails.append(f"source 파일이 없다: {src}")
    if r["fm"]["status"] != "active":
        warn.append(f"원본 확보 후에도 status가 {r['fm']['status']}다")
    if "concepts" in r["fm"] or "questions" in r["fm"]:
        fails.append("RES에 스키마에 없는 concepts/questions 필드가 생겼다")
    # 양방향 유지
    for lid in (r["fm"]["lectures"] or []):
        fwd = [i["id"] if isinstance(i, dict) else i
               for i in (notes.get(lid, {}).get("fm", {}).get("resources") or [])]
        if r["fm"]["id"] not in fwd:
            fails.append(f"{lid}의 정방향 연결이 끊겼다")
record("G ingest-resource 재등록", fails, warn)

# ---------------------------------------------------------- H: ingest-past-exam
fails, warn = [], []
pex = [n for n in notes.values() if n["fm"]["type"] == "past-exam"]
if not pex:
    fails.append("PEX가 생성되지 않았다")
for p in pex:
    fm = p["fm"]
    if fm["provenance"] != "reconstructed":
        warn.append(f"{p['rel']}: 학생 복원본인데 provenance가 {fm['provenance']}다")
    if fm["authority"] != "student-provided":
        warn.append(f"{p['rel']}: authority가 {fm['authority']}다")
    if fm["provenance"] == "reconstructed" and fm["status"] == "analyzed":
        fails.append(f"{p['rel']}: 정답 미검증 복원본인데 analyzed다")
    ev = sec(p["body"], "출제 경향의 근거") or ""
    if "표본" not in ev:
        fails.append(f"{p['rel']}: 표본 수 기록이 없다")
    if re.search(r"(이번 시험에.{0,12}(출제|나온다|나올)|출제가 확정)", ev):
        fails.append(f"{p['rel']}: 현재 시험 출제를 확정하는 서술이 있다")
    if not re.search(r"(아니다|않는다|확정하지)", ev):
        fails.append(f"{p['rel']}: 출제 확정이 아니라는 표시가 없다")
    given = sec(p["body"], "제공된 정답 / 해설") or ""
    ais = sec(p["body"], "AI 풀이 / 검증 필요") or ""
    if not given.strip() or not ais.strip():
        fails.append(f"{p['rel']}: 제공된 정답과 AI 풀이가 분리되지 않았다")
    if "AI" in given:
        fails.append(f"{p['rel']}: 제공된 정답 절에 AI 풀이가 섞였다")
# L3가 EXM을 건드리지 않았는가
e = notes.get("EXM-general-physics-2-2026-2-midterm")
if e:
    scope = sec(e["body"], "확정 범위") or ""
    if re.search(r"(기출|PEX-)", scope):
        fails.append("EXM의 확정 범위에 기출이 유입됐다")
# L3/L7 대시보드 단계가 문서에 있는가 (runtime에서 발견한 결함의 회귀 방지)
for wf, layer in (("l3-past-exam-ingestion.md", "L3"), ("l7-review.md", "L7"),
                  ("l9-knowledge-promotion.md", "L9")):
    if "대시보드" not in (ROOT / "_system/workflows" / wf).read_text(encoding="utf-8"):
        fails.append(f"{layer} 워크플로에 대시보드 갱신 단계가 없다")
record("H ingest-past-exam", fails, warn)

# ---------------------------------------------------------- 출력
print("=" * 66)
print("Runtime Test 검증")
print("=" * 66)
order = ["공통 스키마 적합성", "A capture 라우팅", "C maintain 읽기 전용",
         "D ingest-lecture", "E check-conflict", "B/F recall·review 분기 규칙",
         "G ingest-resource 재등록", "H ingest-past-exam"]
nfail = 0
for k in order:
    v, det = results[k]
    if v == "FAIL":
        nfail += 1
    print(f"\n[{v}] {k}")
    for d in det:
        print(f"    - {d}")
print("\n" + "=" * 66)
tally = {}
for v, _ in results.values():
    tally[v] = tally.get(v, 0) + 1
print("  " + " / ".join(f"{k}: {n}" for k, n in sorted(tally.items())))
print(f"  workspace 노트 {len(notes)}개, 로그 {len(log)}줄")
print("=" * 66)
sys.exit(1 if nfail else 0)
