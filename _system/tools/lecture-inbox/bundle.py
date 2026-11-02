"""inbox 묶음 폴더 쓰기와 `안내.md` 생성. 표준 라이브러리만 쓴다."""
import os
import re
import shutil
from datetime import date
from pathlib import Path

KIND_LABEL = {"transcript": "전사", "resource": "자료", "past-exam": "족보", "assignment": "과제"}
STATUS_LABEL = {"done": "완료", "failed": "실패"}  # 그 밖의 상태는 모두 "대기"

_RESERVED = re.compile(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])")


def safe_name(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|\x00-\x1f\x7f]', "_", value).strip(" .")
    value = value.encode("utf-8")[:120].decode("utf-8", errors="ignore")
    value = value or "미분류"
    # Windows는 확장자가 붙어도 첫 마디가 예약 이름이면 장치로 취급한다.
    if _RESERVED.fullmatch(value.split(".")[0].rstrip(" ")):
        value = "_" + value
    return value


def bundle_dir_name(course: str, day: date) -> str:
    return f"{day:%Y%m%d}-{safe_name(course)}"


def transcript_name(week: int, session: int) -> str:
    return f"week_{week:02d}_{session:02d}.md"


def write_new_file(dest: Path, src: "bytes | Path") -> None:
    """dest가 없을 때만 만든다. partial에 쓴 뒤 os.rename: Windows에서는 대상이 있으면 FileExistsError."""
    if dest.exists():
        raise FileExistsError(str(dest))
    partial = dest.with_name(f".{dest.name}.partial")
    try:
        if isinstance(src, (bytes, bytearray)):
            partial.write_bytes(src)
        else:
            shutil.copyfile(src, partial)
        os.rename(partial, dest)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def _one(value) -> str:
    # 값 안의 줄바꿈이 "### 가짜 항목" 같은 구조를 만들지 못하게 한 줄로 합친다.
    return " ".join(str(value).split())


def _item_lines(item: dict) -> list[str]:
    transcript = item["kind"] == "transcript"
    status = STATUS_LABEL.get(item["status"], "대기")
    if item["status"] == "failed" and item.get("error"):
        status += f" — {_one(item['error'])}"
    lines = [f"### {_one(item['filename'])}", f"- 상태: {status}", f"- 종류: {KIND_LABEL[item['kind']]}"]
    if transcript:
        lines.append(f"- 주차·차시: {item['week']}주차 {item['session']}차시")
    source = item.get("source") or {}
    if source.get("type") == "ecampus":
        lines.append(f'- 출처: 이캠퍼스 강의 "{_one(source["title"])}"')
    elif source.get("type") == "upload":
        lines.append(f'- 출처: 원래 파일 "{_one(source["name"])}"')
    if transcript:
        lines.append(f"- 수업일: {_one(item['date']) if item.get('date') else '미확인'}")
        if item["status"] == "done":
            if item.get("model"):
                lines.append(f"- 모델: {_one(item['model'])}")
            reps = item.get("repetitions")
            if reps:
                if isinstance(reps, (list, tuple)):
                    reps = ", ".join(map(str, reps))
                lines.append(f"- 반복 감지 구간: {_one(reps)}")
    return lines


def render_guide(meta: dict, items: list[dict], present: set[str]) -> str:
    out = [
        "# 강의 수집 도구 안내",
        "",
        "이 파일은 강의 수집 도구(`_system/tools/lecture-inbox`)가 사용자가 화면에서 지정한 내용을 받아 쓴 것이다. "
        "아래의 과목·학기·종류·주차·차시·수업일은 사용자 지정이다. 도구가 다시 쓰는 파일이므로 고치지 않는다. "
        "처리 규칙은 `inbox/README.md`의 `강의 수집 도구 묶음` 절을 따른다.",
        "",
        "## 과목",
        "",
    ]
    for label, key in (("과목명", "course"), ("term", "term"), ("이캠퍼스 과목 id", "ecampus_id"),
                       ("학수번호", "code"), ("분반", "section")):
        if meta.get(key):
            out.append(f"- {label}: {_one(meta[key])}")
    out += ["", "## 항목"]
    # 이미 옮긴 완료 항목은 뺀다.
    for item in sorted(items, key=lambda i: i["created"]):
        if item["status"] == "done" and item["filename"] not in present:
            continue
        out += ["", *_item_lines(item)]
    return "\n".join(out) + "\n"


def write_guide(folder: Path, meta: dict, items: list[dict]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    present = {p.name for p in folder.iterdir()}
    partial = folder / ".안내.md.partial"
    partial.write_text(render_guide(meta, items, present), encoding="utf-8", newline="\n")
    os.replace(partial, folder / "안내.md")
