"""템플릿에 가상 값을 채워 임시 검증용 노트를 만든다. 실제 학습 폴더는 건드리지 않는다."""
import pathlib, re, shutil, sys

# Windows 콘솔 기본 인코딩(cp949)에서는 em dash 등이 UnicodeEncodeError를 낸다.
# 검사 결과가 인코딩 때문에 끊기지 않도록 출력 스트림을 UTF-8로 맞춘다.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
TPL = HERE.parents[2]/"_system/templates"
OUT = HERE/"filled"
if OUT.exists(): shutil.rmtree(OUT)
D = "2026-09-08"
# 가상 과목(일반물리학 1, term 2026-2)의 폴더. common.md Storage Paths의 학기·과목 구조를 따른다.
C = "study/2026-2/general-physics-1"
R = "raw/2026-2/general-physics-1"

def set_field(txt, key, val):
    pat = re.compile(rf"^{re.escape(key)}: .*$", re.M)
    assert pat.search(txt), f"no field {key}"
    return pat.sub(f"{key}: {val}", txt, count=1)

def add_after(txt, anchor, lines):
    # anchor는 값까지 포함한 줄(여러 줄 가능)이다. 예전에는 뒤에 ": .*"를 또 붙여 어떤 줄과도
    # 맞지 않았고, 매칭 실패를 확인하지 않아 code·instructor·week·effective_from이 조용히 빠졌다.
    # set_field는 목록 값을 "key: \n  - ..."로 쓰므로 각 줄 끝의 공백을 허용한다.
    body = r"[ \t]*\n".join(re.escape(part) for part in anchor.split("\n"))
    pat = re.compile(rf"^{body}[ \t]*$", re.M)
    assert pat.search(txt), f"no anchor {anchor!r}"
    return pat.sub(lambda m: m.group(0)+"\n"+lines, txt, count=1)

def fill(txt, heading, content):
    pat = re.compile(rf"^(## {re.escape(heading)}\n)(.*?)(?=^## |\Z)", re.M|re.S)
    assert pat.search(txt), f"no heading {heading}"
    return pat.sub(lambda m: m.group(1)+"\n"+content.rstrip()+"\n\n", txt, count=1)

def base(t, ident, title, **kw):
    s = (TPL/f"{t}.md").read_text(encoding="utf-8")
    s = (s.replace('"{{id}}"', ident).replace('"{{title}}"', title)
           .replace('"{{created}}"', D).replace('"{{updated}}"', D))
    for k,v in kw.items(): s = set_field(s, k, v)
    return s

N = {}
N["course"] = base("course","CRS-20260908-01","일반물리학 1", status="active", term='"2026-2"',
                   topics="\n  - classical-mechanics")
N["course"] = add_after(N["course"], "updated: "+D, 'code: PHY101\ninstructor: 홍길동')
N["course"] = fill(N["course"], "Related Notes",
 """<!-- AUTO-MANAGED:start -->
- LEC-20260908-01 | 운동량과 충격량 | processed | 주 과목
- ASM-20260908-01 | 물리학 HW03 | open | 주 과목
- EXM-20260908-01 | 일반물리학 중간고사 | planned | 주 과목
- FAC-20260908-01 | 중간고사 일정 확정 | active | 주 과목
- RES-general-physics-1-week03-slides | Chapter 3 - Momentum | active | 주 과목
- PEX-20260908-01 | 물리학 2024 중간고사 기출 | needs-review | 주 과목
- QST-20260908-01 | 운동량 보존 조건 확인 | open | 주 과목
- REV-20260908-01 | 물리학 주간 복습 | planned | 주 과목
<!-- AUTO-MANAGED:end -->""")
N["course"] = fill(N["course"], "My Notes", "<!-- AI-PROTECTED -->\n\n사용자가 직접 쓴 메모. 재생성 시에도 남아야 한다.")

N["lecture"] = base("lecture","LEC-20260908-01","운동량과 충격량", status="processed",
    course="CRS-20260908-01", date=D, source=f"{R}/transcripts/2026-09-08-physics-01.md",
    topics="\n  - momentum", resources='\n  - id: RES-general-physics-1-week03-slides\n    pages: "32-45"',
    concepts="\n  - CON-20260908-01", assignments="\n  - ASM-20260908-01",
    exams="\n  - EXM-20260908-01", course_facts="\n  - FAC-20260908-01",
    questions="\n  - QST-20260908-01")
N["lecture"] = add_after(N["lecture"], "date: "+D, "week: 3")
N["lecture"] = fill(N["lecture"], "My Notes", "<!-- AI-PROTECTED -->\n\n사용자 필기. 보호 영역 유지 확인용.")

N["resource"] = base("resource","RES-general-physics-1-week03-slides","Chapter 3 - Momentum", status="active",
    course="CRS-20260908-01", resource_type="slides", authority="professor",
    source=f"{R}/resources/week03-slides.pdf", topics="\n  - momentum",
    lectures="\n  - LEC-20260908-01")
N["concept"] = base("concept","CON-20260908-01","운동량", status="active", topics="\n  - momentum",
    aliases="\n  - momentum", sources="\n  - LEC-20260908-01\n  - RES-general-physics-1-week03-slides")
N["assignment"] = base("assignment","ASM-20260908-01","물리학 HW03", course="CRS-20260908-01",
    assigned=D, due="null", due_status="needs-review", sources="\n  - LEC-20260908-01")
N["exam"] = base("exam","EXM-20260908-01","일반물리학 중간고사", course="CRS-20260908-01",
    exam_type="midterm", date="null", date_status="needs-review", scope_status="unknown",
    sources="\n  - LEC-20260908-01\n  - FAC-20260908-01", concepts="\n  - CON-20260908-01")
N["past-exam"] = base("past-exam","PEX-20260908-01","물리학 2024 중간고사 기출", status="needs-review",
    course="CRS-20260908-01", year=2024, exam_type="midterm",
    source="https://example.edu/past-exams/2024-midterm.pdf",
    authority="student-provided", provenance="reconstructed", concepts="\n  - CON-20260908-01")
N["past-exam"] = fill(N["past-exam"], "자료 식별 / 출처",
    "- 접근 여부: 확인하지 못함. 링크만 등록했고 문항 분석은 보류한다.\n- 배포 경로: 학생 공유\n- 표본 범위: 1회차")
N["course-fact"] = base("course-fact","FAC-20260908-01","중간고사 일정 확정", status="active",
    course="CRS-20260908-01", fact_type="schedule", subject="EXM-20260908-01",
    value='"중간고사는 2026-10-20에 실시한다"', authority="professor",
    sources="\n  - LEC-20260908-01", supersedes="[]")
N["course-fact"] = add_after(N["course-fact"], "sources:\n  - LEC-20260908-01", "effective_from: "+D)
N["question"] = base("question","QST-20260908-01","운동량 보존 조건 확인", course="CRS-20260908-01",
    question_type="conceptual", sources="\n  - LEC-20260908-01",
    answer_sources="[]", resolved_on="null")
N["review"] = base("review","REV-20260908-01","물리학 주간 복습", course="CRS-20260908-01",
    review_type="weekly", targets="\n  - LEC-20260908-01\n  - CON-20260908-01",
    scheduled_on="2026-09-14", completed_on="null", next_review="null")
N["cluster"] = base("cluster","CLU-20260908-01","고전역학 개념 지도", status="active",
    topics="\n  - classical-mechanics", members="\n  - CON-20260908-01")

# CRS는 과목 폴더의 course.md, course-scoped 노트는 그 아래 종류 폴더, CON·CLU는 전역 wiki에 둔다.
LOC = {"course":C,"lecture":f"{C}/lectures","resource":f"{C}/resources",
       "concept":"wiki/concepts","assignment":f"{C}/assignments","exam":f"{C}/exams",
       "past-exam":f"{C}/past-exams","course-fact":f"{C}/course-facts",
       "question":f"{C}/questions","review":f"{C}/reviews","cluster":"wiki/clusters"}
for t, txt in N.items():
    d = OUT/LOC[t]; d.mkdir(parents=True, exist_ok=True)
    name = "course.md" if t == "course" else f"{t}-sample.md"
    (d/name).write_text(txt, encoding="utf-8", newline="\n")

(OUT/R/"transcripts").mkdir(parents=True, exist_ok=True)
(OUT/R/"resources").mkdir(parents=True, exist_ok=True)
(OUT/R/"transcripts/2026-09-08-physics-01.md").write_text(
    "가상 전사 원본. 실제 수업 자료가 아니다.\n", encoding="utf-8", newline="\n")
(OUT/R/"resources/week03-slides.pdf").write_text(
    "가상 수업자료 원본. 실제 PDF 대신 쓰는 자리 파일이다.\n", encoding="utf-8", newline="\n")
(OUT/"wiki/clusters/_topics.md").write_text(
    "- momentum — 운동량과 충격량 (최초 근거: LEC-20260908-01)\n"
    "- classical-mechanics — 고전역학 전반 (최초 근거: CON-20260908-01)\n",
    encoding="utf-8", newline="\n")
print("filled 노트", len(N), "개 생성:", OUT)
