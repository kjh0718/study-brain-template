"""Scenario A~K 통합 시험용 가상 vault를 생성한다.

여기서 만드는 모든 파일은 **가상 테스트 데이터**다. 실제 학습 자료가 아니다.
저장소의 실제 study/, wiki/, raw/를 건드리지 않고 vault/ 아래에만 쓴다.

    python build_fixtures.py
"""
import pathlib, shutil, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
V = HERE / "vault"          # 가상 저장소 루트
B = HERE / "broken"         # L8 검사용 고의 오류 fixture

BANNER = "<!-- 통합 시험용 가상 데이터. 실제 학습 자료가 아니다. -->"


def w(rel, text, root=None):
    p = (root or V) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.lstrip("\n"), encoding="utf-8")
    return p


def fm(**kw):
    """frontmatter 블록을 만든다. 값은 이미 YAML로 직렬화된 문자열이어야 한다."""
    lines = ["---"]
    for k, v in kw.items():
        lines.append(f"{k}: {v}" if v is not None else f"{k}: null")
    lines.append("---")
    return "\n".join(lines) + "\n"


def lst(items, indent=0):
    if not items:
        return "[]"
    pad = " " * indent
    return "\n" + "\n".join(f"{pad}  - {i}" for i in items)


for d in (V, B):
    if d.exists():
        shutil.rmtree(d)

CRS = "CRS-2026-2-general-physics-2"
CRS1 = "CRS-2026-1-general-physics-2"
RES = "RES-general-physics-2-ch03-slides"
EXM = "EXM-general-physics-2-2026-2-midterm"   # <term> 사용. 연도만 쓰면 학기 간 충돌한다

# ---------------------------------------------------------------- Scenario A
# 수업 전사 원본. L1의 1단계 결과물이며 이후 어떤 단계가 실패해도 남아야 한다.
w("raw/transcripts/2026-09-08-general-physics-2-01.md", f"""
{BANNER}
# 일반물리학2 2026-09-08 1교시 전사 (가상)

[00:00:10] 자 시작합시다. 지난 시간에 뉴턴 제2법칙까지 했고 오늘은 운동량과 충격량입니다.

[00:03:40] 운동량은 질량 곱하기 속도입니다. p = mv. 벡터량이라는 걸 꼭 기억하세요.

[00:08:15] 충격량은 힘을 시간에 대해 적분한 겁니다. J = ∫F dt. 그리고 이게 운동량 변화량과
같습니다. 이걸 충격량-운동량 정리라고 합니다.

[00:19:02] 자, 여기 3장 슬라이드 21페이지부터 보겠습니다. 38페이지까지가 오늘 범위입니다.

[00:24:30] 계에 작용하는 외력의 합이 0이면 전체 운동량은 보존됩니다. 이게 운동량 보존 법칙이에요.

[00:31:55] 탄성 충돌에서는 운동에너지도 보존되는데, 비탄성 충돌에서는 운동에너지가 보존되지
않습니다. 운동량은 두 경우 모두 보존됩니다.

[00:41:12] 이 부분은 중간고사에 반드시 나옵니다. 충격량-운동량 정리는 꼭 이해하고 오세요.

[00:44:00] 그리고 로켓 추진도 운동량 보존으로 설명할 수 있는데, 이건 참고로만 알아두세요.
시험에는 안 냅니다.

[00:52:20] (학생 질문) 교수님, 비탄성 충돌에서 운동에너지는 어디로 가나요?
[00:52:35] 열이나 소리, 변형으로 갑니다. 사라지는 게 아니라 형태가 바뀌는 거예요.

[00:55:10] (학생 질문) 완전 비탄성 충돌이면 두 물체가 붙어서 같이 움직이는 건가요?
[00:55:25] 네 맞습니다. 그 경우가 운동에너지 손실이 최대입니다.

[01:02:15] 과제 얘기 하겠습니다. HW3는 다음 주까지 제출하세요. 3장 연습문제 중에 홀수 번호만
풀어 오시면 됩니다.

[01:05:40] 중간고사는 아마 10월 중순쯤 될 것 같은데 확정되면 LMS에 올리겠습니다.

[01:08:00] 다음 시간에는 회전 운동 들어갑니다. 4장 미리 읽어 오세요.

[01:09:30] 오늘 여기까지 하겠습니다.
""")

# L1이 만든 Lecture. 교수 발언 / AI 해석 / 자료 강조를 서로 다른 절에 둔다.
w("study/lectures/2026-09-08-momentum.md", fm(
    schema=1, type="lecture", id="LEC-20260908-01", title="운동량과 충격량",
    status="processed", topics=lst(["momentum", "impulse"]), related="[]",
    created="2026-09-08", updated="2026-09-08", course=CRS, date="2026-09-08",
    week=3, source="raw/transcripts/2026-09-08-general-physics-2-01.md",
    resources=f"\n  - id: {RES}\n    pages: \"21-38\"",
    concepts=lst(["CON-momentum", "CON-impulse"]),
    assignments=lst(["ASM-general-physics-2-20260908-01"]),
    exams=lst([EXM]),
    course_facts=lst(["FAC-general-physics-2-20260908-01"]),
    questions=lst(["QST-general-physics-2-20260908-01", "QST-general-physics-2-20260908-02"]),
) + f"""
{BANNER}

## 수업 요약

운동량과 충격량을 정의하고 충격량-운동량 정리를 유도한 뒤 탄성·비탄성 충돌에 적용했다.
(AI 요약)

## 핵심 내용

- 운동량 p = mv, 벡터량
- 충격량 J = ∫F dt
- 충격량-운동량 정리
- 외력 합이 0인 계의 운동량 보존
- 탄성 충돌과 비탄성 충돌의 차이

## 교수님 강조

- "이 부분은 중간고사에 반드시 나옵니다. 충격량-운동량 정리는 꼭 이해하고 오세요."
  (raw/transcripts/2026-09-08-general-physics-2-01.md, 00:41:12)
- "벡터량이라는 걸 꼭 기억하세요."
  (raw/transcripts/2026-09-08-general-physics-2-01.md, 00:03:40)
- "로켓 추진은 참고로만 알아두세요. 시험에는 안 냅니다."
  (raw/transcripts/2026-09-08-general-physics-2-01.md, 00:44:00)

## 공식 / 정의

- p = mv
- J = ∫F dt = Δp

## 예제

미확인. 이번 수업에서 별도 예제 풀이는 없었다.

## 시험 관련

- 교수의 출제 명시: 충격량-운동량 정리 (00:41:12)
- 교수의 출제 제외 명시: 로켓 추진 (00:44:00)
- 시험 일정 언급은 확정 표현이 아니었다. FAC-general-physics-2-20260908-01 참조.

## 과제

- HW3, 3장 연습문제 홀수 번호. 원문 표현은 "다음 주까지 제출하세요" (01:02:15)
- 날짜를 확정하지 않았다. ASM-general-physics-2-20260908-01 참조.

## 공지 / Course Facts

- 다음 시간 회전 운동. 4장 예습 안내 (01:08:00)

## Concepts

- [[CON-momentum]] 운동량
- [[CON-impulse]] 충격량
- 후보: 탄성 충돌 (1회 등장, 독립 노트 가치 미확인)

## Questions

- [[QST-general-physics-2-20260908-01]]
- [[QST-general-physics-2-20260908-02]]

## 사용 자료

- {RES} pages 21-38 (00:19:02). 페이지 기준은 슬라이드 번호다.

## 기출 연결

- PEX-general-physics-2-2024-2-midterm
- PEX-general-physics-2-2023-2-midterm
- PEX-general-physics-2-2022-2-midterm

## Review Questions

<!-- 아래 문항은 AI가 생성했다. 교수 출제 예고가 아니다. -->

1. 운동량이 벡터량이라는 사실이 충돌 문제 풀이에서 왜 중요한가? (AI 생성)
2. 충격량-운동량 정리를 유도해 보라. (AI 생성)
3. 비탄성 충돌에서 보존되는 양과 보존되지 않는 양을 구분하라. (AI 생성)

## AI 해석 / 검증 필요

- 충격량-운동량 정리는 이후 충돌 단원 전체의 전제라 복습 가치가 높다. (AI 해석)
- 완전 비탄성 충돌의 운동에너지 손실 최대 조건은 자주 출제되는 유형으로 보인다. (AI 해석,
  근거 없음. 교수 발언 아님)
- 미확인: 3주차가 맞는지 원문에 명시가 없다. week는 사용자 확인 후 확정한다.

## My Notes

<!-- AI-PROTECTED -->

충돌에서 운동에너지가 왜 안 지켜지는지 아직 헷갈림.
p=mv는 외웠는데 적분 형태가 잘 안 와닿는다.

## Source

- raw/transcripts/2026-09-08-general-physics-2-01.md (주 전사본)
""")

# ---------------------------------------------------------------- Scenario B
w("study/resources/ch03-slides.md", fm(
    schema=1, type="resource", id=RES, title="제3장 운동량과 충돌 슬라이드",
    status="active", topics=lst(["momentum"]), related=lst([CRS1]),
    created="2026-09-08", updated="2026-09-17", course=CRS,
    resource_type="slides", authority="professor",
    source="raw/resources/general-physics-2-ch03-slides.pdf", page_count=60,
    lectures=lst(["LEC-20260908-01", "LEC-20260910-01", "LEC-20260915-01", "LEC-20260917-01"]),
) + f"""
{BANNER}

## Overview

교수 배포 3장 슬라이드. 총 60페이지. 네 번의 수업에 걸쳐 사용됐다.

## Structure

- pp.1-20 운동량 정의와 벡터 성질
- pp.21-38 충격량과 충격량-운동량 정리
- pp.39-48 탄성 충돌
- pp.49-60 비탄성 충돌과 2차원 충돌

## Key Concepts

<!-- RES에는 concepts 필드가 없다. 개념 연결은 related와 이 절로 한다. -->

- [[CON-momentum]] 운동량
- [[CON-impulse]] 충격량

## Material Emphasis

- p.27 충격량-운동량 정리 상자 강조
- p.52 완전 비탄성 충돌 별표 표시

## Professor Emphasis

- 충격량-운동량 정리 출제 명시 (LEC-20260908-01, 원문 00:41:12)

## Lecture Usage

<!-- 기준 데이터는 Lecture.resources[].pages다. 이 표는 그것을 요약한 보기다. -->

| Lecture | pages |
|---|---|
| LEC-20260908-01 | 21-38 |
| LEC-20260910-01 | 1-20 |
| LEC-20260915-01 | 39-48 |
| LEC-20260917-01 | 49-60 |

## Exam References

- p.27 강조 상자. 시험 출제 후보이나 자료 강조만으로 확정하지 않았다. L5 미처리.

## Assignment References

- p.58 연습문제 목록. L5 미처리.

## Version / Provenance

초판. 배포처 LMS, 작성자 담당 교수. 2026-1학기에도 같은 파일이 사용됐다(related 참조).

## My Notes

<!-- AI-PROTECTED -->

## Source

- raw/resources/general-physics-2-ch03-slides.pdf (보존됨)
""")

w("raw/resources/general-physics-2-ch03-slides.pdf", "가상 PDF 자리표시자. 실제 파일이 아니다.\n")

_LEC_B = [
    ("LEC-20260910-01", "2026-09-10", "운동량 정의 복습", "1-20", "2026-09-10-momentum-review"),
    ("LEC-20260915-01", "2026-09-15", "탄성 충돌", "39-48", "2026-09-15-elastic-collision"),
    ("LEC-20260917-01", "2026-09-17", "비탄성 충돌", "49-60", "2026-09-17-inelastic-collision"),
]
# collision topic은 대응하는 CON이 없다. Concept identity와 topic vocabulary가
# 1:1로 강제되지 않는지 검증하기 위한 fixture다.
_LEC_TOPICS = {"LEC-20260917-01": ["momentum", "collision"]}

for lid, date, title, pages, slug in _LEC_B:
    w(f"study/lectures/{slug}.md", fm(
        schema=1, type="lecture", id=lid, title=title, status="processed",
        topics=lst(_LEC_TOPICS.get(lid, ["momentum"])), related="[]", created=date, updated=date,
        course=CRS, date=date, source="raw/transcripts/2026-09-08-general-physics-2-01.md",
        resources=f"\n  - id: {RES}\n    pages: \"{pages}\"",
        concepts=lst(["CON-momentum"]), assignments="[]", exams="[]",
        course_facts="[]", questions="[]",
    ) + f"""
{BANNER}

## 수업 요약

Scenario B(Resource N:N) 전용 축약 fixture다. 같은 RES를 서로 다른 페이지 범위로 참조한다.

## 핵심 내용

- {title}

## 교수님 강조

해당 없음. 이 fixture는 N:N 관계만 검증한다.

## 공식 / 정의

해당 없음.

## 예제

해당 없음.

## 시험 관련

해당 없음.

## 과제

해당 없음.

## 공지 / Course Facts

해당 없음.

## Concepts

- [[CON-momentum]]

## Questions

해당 없음.

## 사용 자료

- {RES} pages {pages}

## 기출 연결

해당 없음.

## Review Questions

해당 없음.

## AI 해석 / 검증 필요

이 노트는 통합 시험용 축약 fixture다.

## My Notes

<!-- AI-PROTECTED -->

## Source

- raw/transcripts/2026-09-08-general-physics-2-01.md
""")

# ---------------------------------------------------------------- Scenario C
w("wiki/concepts/momentum.md", fm(
    schema=1, type="concept", id="CON-momentum", title="운동량",
    status="active", topics=lst(["momentum"]), related="[]",
    created="2026-03-02", updated="2026-09-08",
    aliases=lst(["momentum", "linear momentum", "선운동량"]),
    sources=lst(["LEC-20260908-01", RES, "PEX-general-physics-2-2024-2-midterm"]),
) + f"""
{BANNER}

## 정의

물체의 질량과 속도의 곱으로 정의되는 벡터량. p = mv.

## 직관

같은 속도라도 무거운 물체를 멈추기 어렵다는 사실의 정량화다.

## 공식 / 적용 조건

p = mv. 외력의 합이 0인 계에서 전체 운동량이 보존된다.

## 예제

탄성·비탄성 충돌 문제. LEC-20260908-01 참조.

## 흔한 오해

비탄성 충돌에서 운동량도 보존되지 않는다고 생각하기 쉽다. 보존되지 않는 것은 운동에너지다.

## 연결 개념

- [[CON-impulse]] 충격량

## Sources

- LEC-20260908-01 (2026-09-08 수업, 00:03:40)
- {RES} pp.1-20
- PEX-general-physics-2-2024-2-midterm 3번 문항

## 검증 필요

없음.

## My Understanding

<!-- AI-PROTECTED -->

벡터라는 게 계속 걸린다. 1차원에서는 부호만 신경쓰면 되는데 2차원 가면 헷갈림.
""")

w("wiki/concepts/impulse.md", fm(
    schema=1, type="concept", id="CON-impulse", title="충격량",
    status="active", topics=lst(["impulse"]), related="[]",
    created="2026-09-08", updated="2026-09-08",
    aliases=lst(["impulse"]),
    sources=lst(["LEC-20260908-01", RES]),
) + f"""
{BANNER}

## 정의

힘을 작용 시간에 대해 적분한 벡터량. J = ∫F dt.

## 직관

같은 힘이라도 오래 작용하면 운동 상태가 더 많이 바뀐다.

## 공식 / 적용 조건

J = ∫F dt = Δp (충격량-운동량 정리)

## 예제

LEC-20260908-01 참조.

## 흔한 오해

충격량을 순간적인 힘 자체로 오해하기 쉽다.

## 연결 개념

- [[CON-momentum]] 운동량

## Sources

- LEC-20260908-01 (2026-09-08 수업, 00:08:15)
- {RES} pp.21-38

## 검증 필요

없음.

## My Understanding

<!-- AI-PROTECTED -->
""")

w("wiki/clusters/_topics.md", f"""
{BANNER}
# Topic Vocabulary (테스트 fixture)

- impulse — 힘의 시간 적분으로 정의되는 벡터량 (최초 근거: LEC-20260908-01)
- collision — 두 물체가 짧은 시간 상호작용하는 사건 (최초 근거: LEC-20260917-01)
- momentum — 질량과 속도의 곱으로 정의되는 벡터량 (최초 근거: LEC-20260908-01) 별칭: 운동량, linear momentum
""")

# ---------------------------------------------------------------- Scenario D
_ASM = [
    ("A", "ASM-general-physics-2-20260908-01", "HW3 3장 연습문제",
     '"과제는 9월 18일까지 제출하세요."', "2026-09-18", "confirmed", "hw3"),
    ("B", "ASM-general-physics-2-20260908-02", "HW4 4장 예습 과제",
     '"과제는 다음 주까지 제출하세요."', None, "needs-review", "hw4"),
    ("C", "ASM-general-physics-2-20260908-03", "HW5 보고서",
     '"다음 수업 전에 내세요."', None, "needs-review", "hw5"),
    ("D", "ASM-general-physics-2-20260908-04", "HW6 문제풀이",
     '"금요일쯤 제출하면 됩니다."', None, "needs-review", "hw6"),
]
for case, aid, title, quote, due, dstat, slug in _ASM:
    w(f"study/assignments/{slug}.md", fm(
        schema=1, type="assignment", id=aid, title=title, status="open",
        topics="[]", related="[]", created="2026-09-08", updated="2026-09-08",
        course=CRS, assigned="2026-09-08", due=(due or "null"), due_status=dstat,
        sources=lst(["LEC-20260908-01"]),
    ) + f"""
{BANNER}
<!-- Scenario D Case {case} -->

## 요구사항

{title}

## 마감 / 원문 표현

교수 발언 원문: {quote}
(raw/transcripts/2026-09-08-general-physics-2-01.md)

{"확정된 날짜다. due를 기록했다." if due else "기준이 되는 날짜를 특정할 수 없다. due를 null로 두고 due_status를 needs-review로 표시했다. 임의의 날짜를 만들지 않았다."}

## 제출 방법

미확인.

## 진행 체크리스트

- [ ] 문제 풀이
- [ ] 제출

## 제출 기록

없음.

## Sources

- LEC-20260908-01

## My Notes

<!-- AI-PROTECTED -->
""")

# ---------------------------------------------------------------- Scenario E
w("study/exams/2026-midterm.md", fm(
    schema=1, type="exam", id=EXM, title="일반물리학2 2026-2 중간고사",
    status="planned", topics=lst(["momentum"]), related="[]",
    created="2026-09-01", updated="2026-09-08", course=CRS,
    exam_type="midterm", date="2026-10-15", date_status="needs-review",
    scope_status="needs-review",
    sources=lst(["LEC-20260908-01", "FAC-general-physics-2-20260901-01",
                 "FAC-general-physics-2-20260908-01"]),
    concepts=lst(["CON-momentum", "CON-impulse"]),
) + f"""
{BANNER}

## 일정 / 장소

- 기존 공지: 2026-10-15 (FAC-general-physics-2-20260901-01)
- 이후 언급이 있으나 확정 여부가 갈린다. 아래 Scenario E 처리 결과를 따른다.
- date_status: needs-review. 기존 값을 지우지 않았다.

## 확정 범위

<!-- 교수의 명시적 공지만 적는다. -->

미확정. 범위 공지가 아직 없다.

## 교수님 시험 언급

- "이 부분은 중간고사에 반드시 나옵니다. 충격량-운동량 정리는 꼭 이해하고 오세요."
  (LEC-20260908-01, 00:41:12) — 출제 명시
- "로켓 추진은 시험에는 안 냅니다." (LEC-20260908-01, 00:44:00) — 출제 제외 명시

## AI 예상 / 검증 필요

<!-- 교수 발언이 아니다. 확정 범위 절에 올리지 않는다. -->

- 기출 3회차에서 운동량 보존이 반복 출제됐다. 출제 경향의 근거일 뿐 확정이 아니다. (AI 해석)
- 자료 p.27 강조 상자. 자료 강조이며 교수 발언이 아니다.

## 준비 체크리스트

- [ ] 충격량-운동량 정리
- [ ] 충돌 유형 구분

## 관련 기출

- PEX-general-physics-2-2024-2-midterm
- PEX-general-physics-2-2023-2-midterm
- PEX-general-physics-2-2022-2-midterm

## Sources

- LEC-20260908-01
- FAC-general-physics-2-20260901-01
- FAC-general-physics-2-20260908-01

## My Notes

<!-- AI-PROTECTED -->
""")

# 기존 Fact. Case 1(명시적 변경)에 의해 superseded 되는 쪽.
w("study/course-facts/exam-date-v1.md", fm(
    schema=1, type="course-fact", id="FAC-general-physics-2-20260901-01",
    title="중간고사 일정 최초 공지", status="superseded", topics="[]", related="[]",
    created="2026-09-01", updated="2026-09-08", course=CRS, fact_type="schedule",
    subject=EXM, value='"중간고사 2026-10-15"', authority="official-lms",
    sources="[]", effective_from="2026-09-01", supersedes="[]",
) + f"""
{BANNER}
<!-- Scenario E: 명시적 변경으로 대체된 이전 Fact. 파일을 삭제하지 않는다. -->

## 사실 / 적용 범위

2026-2학기 일반물리학2 중간고사 2026-10-15. LMS 공지.

## 근거 원문

raw/notices/2026-09-01-lms-midterm.md

## 이전 정보와의 비교

최초 공지이므로 이전 정보 없음.

## 충돌 / 확인 필요

FAC-general-physics-2-20260908-01이 이 사실을 명시적으로 대체했다.

## 변경 이력

- 2026-09-01 최초 공지 2026-10-15
- 2026-09-08 명시적 변경으로 superseded

## Sources

- raw/notices/2026-09-01-lms-midterm.md

## My Notes

<!-- AI-PROTECTED -->
""")

w("raw/notices/2026-09-01-lms-midterm.md",
  f"{BANNER}\n중간고사는 10월 15일에 시행합니다. (가상 LMS 공지)\n")

# Case 1: 명시적 변경 → supersede 가능
w("study/course-facts/exam-date-v2-case1.md", fm(
    schema=1, type="course-fact", id="FAC-general-physics-2-20260908-01",
    title="중간고사 일정 변경", status="active", topics="[]", related="[]",
    created="2026-09-08", updated="2026-09-08", course=CRS, fact_type="schedule",
    subject=EXM, value='"중간고사 2026-10-17"', authority="professor",
    sources=lst(["LEC-20260908-01"]), effective_from="2026-09-08",
    supersedes=lst(["FAC-general-physics-2-20260901-01"]),
) + f"""
{BANNER}
<!-- Scenario E Case 1: "시험 날짜를 10월 17일로 변경합니다." -->

## 사실 / 적용 범위

2026-2학기 일반물리학2 중간고사 2026-10-17.

## 근거 원문

> "시험 날짜를 10월 17일로 변경합니다."

원문이 이전 내용을 바꾼다고 명시했고, 발화 권한(담당 교수)과 적용 범위(이번 학기 이 과목)가
확인된다. 따라서 명시적 변경으로 판정했다.

## 이전 정보와의 비교

- 이전: 2026-10-15 (FAC-general-physics-2-20260901-01)
- 변경 후: 2026-10-17

## 충돌 / 확인 필요

없음. 명시적 변경이다.

## 변경 이력

- 2026-09-08 명시적 변경. supersedes에 이전 FAC ID 기록. 이전 Fact는 status만 superseded로
  바꾸고 파일과 ID를 남겼다. superseded_by 필드는 만들지 않았다.

## Sources

- LEC-20260908-01

## My Notes

<!-- AI-PROTECTED -->
""")

# Case 2: 변경 선언 없는 단순 진술 → 자동 overwrite 금지
w("study/course-facts/exam-date-case2.md", fm(
    schema=1, type="course-fact", id="FAC-general-physics-2-20260909-01",
    title="중간고사 일정 언급 (변경 선언 없음)", status="needs-review", topics="[]",
    related="[]", created="2026-09-09", updated="2026-09-09", course=CRS,
    fact_type="schedule", subject=EXM, value="null", authority="professor",
    sources=lst(["LEC-20260908-01"]), supersedes="[]",
) + f"""
{BANNER}
<!-- Scenario E Case 2: "시험이 10월 17일입니다." -->

## 사실 / 적용 범위

미확정. 값을 확정하지 않았으므로 value는 null이다.

## 근거 원문

> "시험이 10월 17일입니다."

## 이전 정보와의 비교

- 기존: 2026-10-15 (FAC-general-physics-2-20260901-01)
- 신규 언급: 2026-10-17

## 충돌 / 확인 필요

원문이 이전 내용을 바꾼다고 말하지 않았다. 단순 진술이므로 명시적 변경으로 볼 수 없다.
양쪽 근거를 모두 남기고 needs-review로 두었다. 자동으로 덮어쓰지 않았고 supersedes도 비웠다.
나중에 나온 발언이라는 이유로 채택하지 않았다.

사용자 확인이 필요하다.

## 변경 이력

없음. 아직 확정하지 않았다.

## Sources

- LEC-20260908-01

## My Notes

<!-- AI-PROTECTED -->
""")

# Case 3: 추측 표현 → 확정 Fact로 만들지 않음
w("study/course-facts/exam-date-case3.md", fm(
    schema=1, type="course-fact", id="FAC-general-physics-2-20260910-01",
    title="중간고사 일정 추측 언급", status="needs-review", topics="[]", related="[]",
    created="2026-09-10", updated="2026-09-10", course=CRS, fact_type="schedule",
    subject=EXM, value="null", authority="professor",
    sources=lst(["LEC-20260908-01"]), supersedes="[]",
) + f"""
{BANNER}
<!-- Scenario E Case 3: "시험은 아마 10월 17일쯤일 것 같습니다." -->

## 사실 / 적용 범위

미확정. 확정 표현이 아니므로 value를 채우지 않았다.

## 근거 원문

> "시험은 아마 10월 17일쯤일 것 같습니다."

"아마", "쯤", "것 같습니다"는 확정 표현이 아니다.

## 이전 정보와의 비교

기존 2026-10-15를 바꿀 근거로 쓰지 않았다.

## 충돌 / 확인 필요

확정 Fact로 승격하지 않았다. EXM의 date도 고치지 않았다.

## 변경 이력

없음.

## Sources

- LEC-20260908-01

## My Notes

<!-- AI-PROTECTED -->
""")

# ---------------------------------------------------------------- Scenario F
_PEX = [
    ("PEX-general-physics-2-2024-2-midterm", 2024, "2024-2", "3번", "2024-2-midterm"),
    ("PEX-general-physics-2-2023-2-midterm", 2023, "2023-2", "2번", "2023-2-midterm"),
    ("PEX-general-physics-2-2022-2-midterm", 2022, "2022-2", "4번", "2022-2-midterm"),
]
for pid, year, term, qno, slug in _PEX:
    w(f"study/past-exams/{slug}.md", fm(
        schema=1, type="past-exam", id=pid, title=f"일반물리학2 {term} 중간고사 기출",
        status="needs-review", topics=lst(["momentum"]), related="[]",
        created="2026-09-09", updated="2026-09-09", course=CRS, year=year,
        exam_type="midterm", source=f"raw/past-exams/general-physics-2-{term}-midterm.md",
        authority="student-provided", provenance="reconstructed",
        concepts=lst(["CON-momentum"]),
    ) + f"""
{BANNER}

## 자료 식별 / 출처

{term} 중간고사. 학생 복원본이며 원본 시험지가 아니다. 담당 교수 동일 여부 미확인.

## 문항별 분석

- {qno} 운동량 보존 적용 문제. 원본 p.1. 난이도 중 (AI 판단).
- 나머지 문항은 이 fixture에서 생략했다.

## 제공된 정답 / 해설

복원본에 함께 있던 정답. 출처는 학생 제공이며 공식 정답이 아니다.

## AI 풀이 / 검증 필요

<!-- 제공된 정답과 같은 절에 넣지 않는다. -->

AI 풀이 결과는 제공된 정답과 일치했다. 다만 공식 정답으로 확인된 것은 아니다.

## Concept 연결

- [[CON-momentum]]

## 출제 경향의 근거

운동량 보존이 이 회차 {qno}에서 확인됐다.
표본: 이 노트 단독으로는 1회차. 전체 표본과 반복성 판단은 L9가 한다.
현재 시험 출제를 확정하는 근거가 아니다.

## My Notes

<!-- AI-PROTECTED -->

## Source

- raw/past-exams/general-physics-2-{term}-midterm.md (접근 확인됨)
""")
    w(f"raw/past-exams/general-physics-2-{term}-midterm.md",
      f"{BANNER}\n{term} 중간고사 복원본 (가상). {qno} 운동량 보존 문제.\n")

# ---------------------------------------------------------------- Scenario G/J
w("study/reviews/2026-09-13-weekly.md", fm(
    schema=1, type="review", id="REV-general-physics-2-20260913-weekly",
    title="일반물리학2 주간 복습", status="in-progress", topics=lst(["momentum"]),
    related="[]", created="2026-09-13", updated="2026-09-13", course=CRS,
    review_type="weekly",
    targets=lst(["LEC-20260908-01", "CON-momentum", "CON-impulse"]),
    scheduled_on="2026-09-13", completed_on="null", next_review="2026-09-20",
) + f"""
{BANNER}

## 복습 목표 / 대상

LEC-20260908-01, CON-momentum, CON-impulse

## Recall

1. 운동량의 정의를 쓰라. (AI 생성)

## Understanding

2. 충격량-운동량 정리를 설명하라. (AI 생성)

## Application

3. 완전 비탄성 충돌의 운동에너지 손실을 구하라. (AI 생성)

## 응답 / 관찰 결과

- 1번: 응답함
- 2번: 미평가
- 3번: 미평가

점수를 추정하지 않았다.

## 오개념 / 미해결 질문

- [[QST-general-physics-2-20260908-01]] 미해결

## 다음 행동

next_review 2026-09-20. 계획값이며 알림 자동화가 아니다.

## Personal Reflection

<!-- AI-PROTECTED -->

이번 주는 시간이 없어서 절반만 했다. 다음 주에 Application 부분 다시.
""")

_QST = [
    ("QST-general-physics-2-20260908-01", "비탄성 충돌에서 운동에너지의 행방",
     "conceptual", "open", "q-inelastic-energy"),
    ("QST-general-physics-2-20260908-02", "3장 전체가 시험 범위인지 확인",
     "source-verification", "open", "q-exam-scope"),
]
for qid, title, qtype, st, slug in _QST:
    w(f"study/questions/{slug}.md", fm(
        schema=1, type="question", id=qid, title=title, status=st, topics="[]",
        related="[]", created="2026-09-08", updated="2026-09-08", course=CRS,
        question_type=qtype, sources=lst(["LEC-20260908-01"]),
        answer_sources="[]", resolved_on="null",
    ) + f"""
{BANNER}

## 질문

{title}

## 발생 맥락

LEC-20260908-01. raw/transcripts/2026-09-08-general-physics-2-01.md의 학생 질문 구간.

## 시도한 이해 / 풀이

미기록.

## 답변 후보

AI 설명은 있으나 사용자 확인 전이다. status를 resolved로 올리지 않았다.

## 해결 근거

없음.

## 남은 확인

{"원문 근거를 찾아야 한다. 사용자 확인만으로 해결하지 않는다." if qtype == "source-verification" else "사용자 이해 확인이 필요하다."}

## My Questions

<!-- AI-PROTECTED -->

이거 시험에 나오면 어떻게 쓰지?
""")

w("study/courses/general-physics-2-2026-2.md", fm(
    schema=1, type="course", id=CRS, title="일반물리학2", status="active",
    topics=lst(["momentum"]), related="[]", created="2026-09-01",
    updated="2026-09-17", code="PHY102", term="2026-2", instructor="가상 교수",
) + f"""
{BANNER}

## Overview

통합 시험용 가상 과목이다.

## Schedule

- 기간: 2026-09-01 ~
- 수업 시간: 미확인
- 장소 또는 링크: 미확인

## Learning Goals

- 운동량과 충돌 이해

## Key Concepts

- [[CON-momentum]]
- [[CON-impulse]]

## Related Notes

<!-- AUTO-MANAGED:start -->
- LEC-20260908-01 — 운동량과 충격량 — processed — 주 과목
- LEC-20260910-01 — 운동량 정의 복습 — processed — 주 과목
- LEC-20260915-01 — 탄성 충돌 — processed — 주 과목
- LEC-20260917-01 — 비탄성 충돌 — processed — 주 과목
- ASM-general-physics-2-20260908-01 — HW3 3장 연습문제 — open — 주 과목
- ASM-general-physics-2-20260908-02 — HW4 4장 예습 과제 — open — 주 과목
- ASM-general-physics-2-20260908-03 — HW5 보고서 — open — 주 과목
- ASM-general-physics-2-20260908-04 — HW6 문제풀이 — open — 주 과목
- EXM-general-physics-2-2026-2-midterm — 일반물리학2 2026-2 중간고사 — planned — 주 과목
- FAC-general-physics-2-20260901-01 — 중간고사 일정 최초 공지 — superseded — 주 과목
- FAC-general-physics-2-20260908-01 — 중간고사 일정 변경 — active — 주 과목
- FAC-general-physics-2-20260909-01 — 중간고사 일정 언급 (변경 선언 없음) — needs-review — 주 과목
- FAC-general-physics-2-20260910-01 — 중간고사 일정 추측 언급 — needs-review — 주 과목
- {RES} — 제3장 운동량과 충돌 슬라이드 — active — 주 과목
- PEX-general-physics-2-2022-2-midterm — 일반물리학2 2022-2 중간고사 기출 — needs-review — 주 과목
- PEX-general-physics-2-2023-2-midterm — 일반물리학2 2023-2 중간고사 기출 — needs-review — 주 과목
- PEX-general-physics-2-2024-2-midterm — 일반물리학2 2024-2 중간고사 기출 — needs-review — 주 과목
- QST-general-physics-2-20260908-01 — 비탄성 충돌에서 운동에너지의 행방 — open — 주 과목
- QST-general-physics-2-20260908-02 — 3장 전체가 시험 범위인지 확인 — open — 주 과목
- REV-general-physics-2-20260913-weekly — 일반물리학2 주간 복습 — in-progress — 주 과목
<!-- AUTO-MANAGED:end -->

## Sources

- raw/notices/2026-09-01-lms-midterm.md

## Open Questions

- [[QST-general-physics-2-20260908-01]]
- [[QST-general-physics-2-20260908-02]]

## My Notes

<!-- AI-PROTECTED -->

이 과목은 실험 리포트 비중이 크다고 들었음. 확인 필요.
""")

# 2026-1학기 같은 과목. Scenario I(ID 충돌) 검증용.
w("study/courses/general-physics-2-2026-1.md", fm(
    schema=1, type="course", id=CRS1, title="일반물리학2", status="completed",
    topics=lst(["momentum"]), related="[]", created="2026-03-02",
    updated="2026-06-20", code="PHY102", term="2026-1", instructor="가상 교수",
) + f"""
{BANNER}
<!-- Scenario I: 같은 과목을 2026-1과 2026-2에 각각 수강한 상황을 만든다. -->

## Overview

같은 과목의 이전 학기 수강 기록이다. 담당 교수와 사용 자료가 같다.

## Schedule

- 기간: 2026-03-02 ~ 2026-06-20

## Learning Goals

- 운동량과 충돌 이해

## Key Concepts

- [[CON-momentum]]

## Related Notes

<!-- AUTO-MANAGED:start -->
- {RES} — 제3장 운동량과 충돌 슬라이드 — active — 공유
<!-- AUTO-MANAGED:end -->

## Sources

-

## Open Questions

-

## My Notes

<!-- AI-PROTECTED -->
""")

w("wiki/clusters/classical-mechanics.md", fm(
    schema=1, type="cluster", id="CLU-classical-mechanics", title="고전역학 개념 지도",
    status="active", topics=lst(["momentum", "impulse"]), related="[]",
    created="2026-09-08", updated="2026-09-08",
    members=lst(["CON-momentum", "CON-impulse", "LEC-20260908-01"]),
) + f"""
{BANNER}

## 범위 / 포함 기준

운동량과 충격량을 다루는 개념과 근거 노트.

## 핵심 개념

- [[CON-momentum]]
- [[CON-impulse]]

## 학습 순서 / 연결

운동량 → 충격량 → 충돌

## 관련 강의 / 자료

- LEC-20260908-01

## 열린 질문

- [[QST-general-physics-2-20260908-01]]

## My Notes

<!-- AI-PROTECTED -->
""")

w("_system/log.md", f"""
{BANNER}
- 2026-09-08 18:32 | L1 | preserve-source | raw/transcripts/2026-09-08-general-physics-2-01.md | done | 전사 원본 보존
- 2026-09-08 18:35 | L1 | create-note | LEC-20260908-01 | done | 일반물리학2 09-08 1교시
- 2026-09-08 18:38 | L2 | create-note | RES-general-physics-2-ch03-slides | done | 3장 슬라이드 신규 등록
- 2026-09-08 18:40 | L1 | sync-relations | LEC-20260908-01 + RES-general-physics-2-ch03-slides | done | pages 21-38 양방향
- 2026-09-08 18:41 | L4 | register-topic | impulse | done | 최초 근거 LEC-20260908-01
- 2026-09-08 18:42 | L4 | create-note | CON-impulse | done | 근거 2개
- 2026-09-08 18:42 | L4 | update-note | CON-momentum | done | sources에 LEC-20260908-01 추가
- 2026-09-08 18:44 | L5 | reconcile-fact | ASM-general-physics-2-20260908-02 | held | 마감 "다음 주까지" 모호. due null 유지
- 2026-09-08 18:45 | L5 | reconcile-fact | FAC-general-physics-2-20260901-01 | done | 명시적 변경으로 superseded
- 2026-09-08 18:45 | L5 | create-note | FAC-general-physics-2-20260908-01 | done | supersedes FAC-general-physics-2-20260901-01
- 2026-09-08 18:46 | L1 | refresh-dashboard | {CRS} | done | Related Notes 재구성
- 2026-09-08 18:47 | L1 | finalize-run | LEC-20260908-01 | partial | 대시보드 갱신 직전 중단 (Scenario K 재현용)
- 2026-09-09 10:02 | L1 | refresh-dashboard | {CRS} | done | Scenario K 재개. 남은 단계만 수행
- 2026-09-09 10:03 | L1 | finalize-run | LEC-20260908-01 | done | 재개 완료
""")

# ------------------------------------------------------------ L8 오류 fixture
w("bad-yaml.md", """
---
schema: 1
type: lecture
id: LEC-20260920-01
title: "닫히지 않은 따옴표
status: draft
---

<!-- 통합 시험용 고의 오류: invalid YAML -->
""", root=B)

w("bad-prefix.md", fm(
    schema=1, type="lecture", id="RES-20260920-01", title="잘못된 접두사",
    status="draft", topics="[]", related="[]", created="2026-09-20",
    updated="2026-09-20", course=CRS, date="2026-09-20", source="raw/transcripts/x.md",
    resources="[]", concepts="[]", assignments="[]", exams="[]",
    course_facts="[]", questions="[]",
) + "\n<!-- 고의 오류: type은 lecture인데 id 접두사가 RES -->\n", root=B)

w("bad-id-shape.md", fm(
    schema=1, type="concept", id="CON-Linear Momentum", title="ID 형식 위반",
    status="draft", topics="[]", related="[]", created="2026-09-20",
    updated="2026-09-20", aliases="[]", sources="[]",
) + "\n<!-- 고의 오류: 대문자와 공백. ID 형식 계약 위반 -->\n", root=B)

w("bad-missing-ref.md", fm(
    schema=1, type="concept", id="CON-dangling-ref", title="없는 ID 참조",
    status="draft", topics="[]", related=lst(["LEC-99999999-99"]),
    created="2026-09-20", updated="2026-09-20", aliases="[]", sources="[]",
) + "\n<!-- 고의 오류: 존재하지 않는 노트 참조 -->\n", root=B)

w("bad-duplicate-concept.md", fm(
    schema=1, type="concept", id="CON-linear-momentum", title="linear momentum",
    status="draft", topics=lst(["linear-momentum"]), related="[]",
    created="2026-09-20", updated="2026-09-20",
    aliases=lst(["운동량", "momentum"]), sources="[]",
) + "\n<!-- 고의 오류: CON-momentum과 의미 중복. topic slug도 momentum과 중복 -->\n", root=B)

w("bad-status.md", fm(
    schema=1, type="lecture", id="LEC-20260921-01", title="허용되지 않는 status",
    status="active", topics="[]", related="[]", created="2026-09-21",
    updated="2026-09-21", course=CRS, date="2026-09-21",
    source="raw/transcripts/x.md", resources="[]", concepts="[]",
    assignments="[]", exams="[]", course_facts="[]", questions="[]",
) + "\n<!-- 고의 오류: lecture에 active는 허용 값이 아니다 -->\n", root=B)

w("bad-orphan.md", fm(
    schema=1, type="concept", id="CON-orphan-topic", title="어디서도 참조되지 않는 노트",
    status="draft", topics="[]", related="[]", created="2026-09-20",
    updated="2026-09-20", aliases="[]", sources="[]",
) + "\n<!-- 고의 오류: orphan. 근거도 없고 참조하는 노트도 없다 -->\n", root=B)

w("bad-missing-source.md", fm(
    schema=1, type="resource", id="RES-general-physics-2-missing-file",
    title="없는 원본을 가리키는 자료", status="active", topics="[]", related="[]",
    created="2026-09-20", updated="2026-09-20", course=CRS,
    resource_type="slides", authority="professor",
    source="raw/resources/does-not-exist.pdf", lectures="[]",
) + "\n<!-- 고의 오류: 로컬 source 경로의 파일이 없다 -->\n", root=B)

w("bad-supersedes.md", fm(
    schema=1, type="course-fact", id="FAC-general-physics-2-20260920-01",
    title="끊어진 supersede 참조", status="active", topics="[]", related="[]",
    created="2026-09-20", updated="2026-09-20", course=CRS, fact_type="schedule",
    subject=EXM, value='"없는 사실을 대체한다고 주장"', authority="unknown",
    sources="[]", supersedes=lst(["FAC-general-physics-2-19990101-01"]),
) + "\n<!-- 고의 오류: supersedes가 존재하지 않는 FAC를 가리킨다 -->\n", root=B)

w("README.md", f"""
# 고의 오류 fixture

{BANNER}

L8 무결성 검사가 각 오류를 잡는지 확인하기 위한 파일이다. **정상 노트가 아니다.**
`vault/`와 분리해 두어 정상 검사 결과를 오염시키지 않는다.

| 파일 | 심은 오류 | L8 검사 항목 |
|---|---|---|
| `bad-yaml.md` | invalid YAML | 1 |
| `bad-prefix.md` | type과 ID 접두사 불일치 | 3 |
| `bad-id-shape.md` | ID 형식 계약 위반(대문자·공백) | 3 |
| `bad-missing-ref.md` | 없는 ID 참조 | 4 |
| `bad-duplicate-concept.md` | 중복 개념 + 중복 topic slug | 7, L9 후보 |
| `bad-status.md` | 허용되지 않는 status | 2 |
| `bad-orphan.md` | orphan 노트 | 4 |
| `bad-missing-source.md` | 로컬 source 파일 없음 | 6 |
| `bad-supersedes.md` | 끊어진 supersede 참조 | 9 |
""", root=B)

n = sum(1 for _ in V.rglob("*") if _.is_file()) + sum(1 for _ in B.rglob("*") if _.is_file())
print(f"fixture 생성 완료: vault/ + broken/ 총 {n}개 파일")
print(f"위치: {HERE}")
