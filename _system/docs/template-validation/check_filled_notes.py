"""B. 값을 채운 가상 노트 검사. 템플릿 검증이며 L1~L9 실행 테스트가 아니다."""
import pathlib, re, sys, yaml

# Windows 콘솔 기본 인코딩(cp949)에서는 em dash 등이 UnicodeEncodeError를 낸다.
# 검사 결과가 인코딩 때문에 끊기지 않도록 출력 스트림을 UTF-8로 맞춘다.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCH  = ROOT/"_system/schemas"
BOX  = HERE/"filled"                      # 이 폴더가 가상 저장소 루트다
OPTIONAL = {"course":{"code","term","instructor"},"lecture":{"week"},"resource":{"page_count"},
            "assignment":{"submission_method"},"course-fact":{"effective_from"}}
PREFIX = {"course":"CRS","lecture":"LEC","concept":"CON","assignment":"ASM","exam":"EXM",
          "past-exam":"PEX","course-fact":"FAC","question":"QST","resource":"RES",
          "review":"REV","cluster":"CLU"}
# _system/schemas/common.md의 `id` 형식 계약. 접두사 뒤는 ASCII 소문자/숫자/단일 하이픈만 허용한다.
ID_CONTRACT = r"^(?:CRS|LEC|CON|ASM|EXM|PEX|FAC|QST|RES|REV|CLU)-[a-z0-9]+(?:-[a-z0-9]+)*$"
DATE_FIELDS = {"created","updated","date","assigned","due","effective_from","resolved_on",
               "scheduled_on","completed_on","next_review"}
REL_FIELDS = {"related","concepts","questions","assignments","exams","course_facts","sources",
              "answer_sources","targets","members","lectures","supersedes","course","subject"}
problems, ok = [], []

spec = {}
for f in SCH.glob("*.md"):
    if f.name in ("README.md","common.md"): continue
    t=f.stem; txt=f.read_text(encoding="utf-8")
    fmex=yaml.safe_load(re.search(r"^```yaml\n(.*?)^```$",txt,re.M|re.S).group(1).strip().strip("-"))
    ms=re.search(r"^## Status(?: Values)?\s*$",txt,re.M)
    st=set(re.findall(r"^- `?([a-z-]+)`?:", re.split(r"^## ",txt[ms.end():],maxsplit=1,flags=re.M)[0], re.M))
    spec[t]={"fields":set(fmex),"required":set(fmex)-OPTIONAL.get(t,set()),"status":st}

notes={}
for f in sorted(BOX.rglob("*.md")):
    if f.name == "_topics.md" or "raw" in f.relative_to(BOX).parts: continue
    raw=f.read_text(encoding="utf-8")
    m=re.match(r"^---\n(.*?)\n---\n(.*)$",raw,re.S)
    if not m: problems.append(f"{f.name}: frontmatter 없음"); continue
    try: fm=yaml.safe_load(m.group(1))
    except Exception as e: problems.append(f"{f.name}: YAML 오류 {e}"); continue
    notes[fm["id"]]=(f,fm,m.group(2),raw)
ok.append(f"가상 노트 {len(notes)}개 파싱 OK")

topics_reg={l.split("—")[0].strip("- ").strip() for l in (BOX/"wiki/clusters/_topics.md").read_text(encoding="utf-8").splitlines() if l.strip()}
ids=set(notes)
if len(ids)!=len(notes): problems.append("ID 중복")

for nid,(f,fm,body,raw) in notes.items():
    t=fm["type"]; s=spec[t]; tag=f.relative_to(BOX)
    if "{{" in raw: problems.append(f"{tag}: 치환되지 않은 자리표시자 남음")
    miss=s["required"]-set(fm)
    if miss: problems.append(f"{tag}: 필수 필드 누락 {sorted(miss)}")
    ext=set(fm)-s["fields"]
    if ext: problems.append(f"{tag}: 스키마에 없는 필드 {sorted(ext)}")
    if fm["status"] not in s["status"]: problems.append(f"{tag}: status {fm['status']} 불허")
    if not str(nid).startswith(PREFIX[t]+"-"): problems.append(f"{tag}: ID 접두사 불일치 {nid}")
    # common.md의 id 형식 계약. Type별 권장 형태는 강제하지 않고 계약만 검사한다.
    if not re.match(ID_CONTRACT, str(nid)): problems.append(f"{tag}: ID 형식 계약 위반 {nid}")
    if fm.get("schema")!=1: problems.append(f"{tag}: schema != 1")
    for k in DATE_FIELDS & set(fm):
        v=fm[k]
        if v is None: continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}(T[\d:+\-]+)?$", str(v)):
            problems.append(f"{tag}: {k} 날짜 형식 아님 -> {v}")
    for k in REL_FIELDS & set(fm):
        v=fm[k]
        vals=[]
        if isinstance(v,str): vals=[v]
        elif isinstance(v,list):
            for it in v: vals.append(it["id"] if isinstance(it,dict) else it)
        for r in vals:
            if not isinstance(r,str) or not re.match(r"^[A-Z]{3}-",r): continue
            if r not in ids: problems.append(f"{tag}: {k}의 {r} 대상 노트 없음")
            if r==nid: problems.append(f"{tag}: {k}에 자기 자신")
    for tp in fm.get("topics") or []:
        if tp not in topics_reg: problems.append(f"{tag}: topic '{tp}' 어휘표 미등록")
    src=fm.get("source")
    if isinstance(src,str):
        if src.startswith("http"): ok.append(f"{tag}: 외부 참조 source (파일 존재 검사 제외)")
        elif not (BOX/src).exists(): problems.append(f"{tag}: source 로컬 경로 없음 {src}")
        else: ok.append(f"{tag}: 로컬 source 존재 확인")
    for h in ("My Notes","My Understanding","My Questions","Personal Reflection"):
        if f"## {h}" in body and "<!-- AI-PROTECTED -->" not in body:
            problems.append(f"{tag}: 보호 표식 없음")

# Lecture <-> Resource 양방향
for nid,(f,fm,b,r) in notes.items():
    if fm["type"]=="lecture":
        for item in fm.get("resources") or []:
            rid=item["id"] if isinstance(item,dict) else item
            back=notes.get(rid,(None,{},"",""))[1].get("lectures") or []
            if nid not in back: problems.append(f"{nid} -> {rid} 연결의 역방향 없음")
            else: ok.append(f"양방향 확인: {nid} <-> {rid}")
    if fm["type"]=="resource":
        for lid in fm.get("lectures") or []:
            fwd=[i["id"] if isinstance(i,dict) else i for i in (notes.get(lid,(None,{},"",""))[1].get("resources") or [])]
            if nid not in fwd: problems.append(f"{nid} -> {lid} 역방향의 정방향 없음")

# Course 자동 관리 영역 + 보호 영역 경계
cid=[i for i,(f,fm,b,r) in notes.items() if fm["type"]=="course"][0]
cf,cfm,cbody,craw=notes[cid]
m=re.search(r"<!-- AUTO-MANAGED:start -->\n(.*?)<!-- AUTO-MANAGED:end -->",cbody,re.S)
if not m: problems.append("course: AUTO-MANAGED 경계 없음")
else:
    cur=[l for l in m.group(1).strip().splitlines() if l.strip()]
    order=["lecture","assignment","exam","course-fact","resource"]
    def key(n):
        t=notes[n][1]["type"]
        return (order.index(t) if t in order else len(order)+1, t, n)
    rows=[]
    for n,(f2,fm2,b2,r2) in notes.items():
        if fm2["type"]=="course": continue
        shared = fm2.get("course")!=cid and cid in (fm2.get("related") or [])
        if fm2.get("course")==cid or shared:
            rows.append((n, f"- {n} | {fm2['title']} | {fm2['status']} | {'공유' if shared else '주 과목'}"))
    exp=[t for _,t in sorted(rows, key=lambda x: key(x[0]))]
    if exp!=cur:
        problems.append("course 대시보드가 재구성 결과와 다름")
        problems.append("  기대:\n    "+"\n    ".join(exp))
        problems.append("  실제:\n    "+"\n    ".join(cur))
    else: ok.append(f"course 대시보드 재구성 일치 ({len(exp)}행) — 변경 없음이므로 재작성 대상 아님")
    after=cbody.split("<!-- AUTO-MANAGED:end -->",1)[1]
    seg=re.split(r"^## ",after.split("## My Notes\n",1)[1],maxsplit=1,flags=re.M)[0]
    user=[l for l in seg.splitlines() if l.strip() and not l.strip().startswith("<!--")]
    if not user: problems.append("course: 보호 영역의 사용자 내용이 사라짐")
    else: ok.append(f"course 보호 영역 유지: {user[0][:40]}")

print("\n".join(ok))
print("\n===== B. 가상 노트 검사 PROBLEMS =====")
print("\n".join(problems) if problems else "none")
sys.exit(1 if problems else 0)
