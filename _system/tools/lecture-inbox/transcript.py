"""전사 형식과 체크포인트. .md의 타임스탬프는 노트 정리 에이전트가 그대로 가져다 쓴다.

타임스탬프 형식은 Chuseok22/transcribe-inbox의 transcript formatter(MIT)를 따른다.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


def format_hms(seconds: float) -> str:
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def to_markdown(segments: list[Segment]) -> str:
    return "".join(f"[{format_hms(s.start)}] {s.text}\n" for s in segments)


def _parse(line: bytes) -> Segment:
    d = json.loads(line.decode("utf-8"))
    return Segment(float(d["start"]), float(d["end"]), str(d["text"]))


def read_checkpoint(path: Path) -> list[Segment]:
    """JSONL 체크포인트를 읽는다. 쓰다 끊긴 마지막 줄은 파일에서도 잘라 내 이어 쓸 수 있게 한다."""
    path = Path(path)
    if not path.exists():
        return []
    data = path.read_bytes()
    cut = data.rfind(b"\n") + 1  # 마지막 개행 뒤부터가 꼬리. 개행이 없으면 0.
    segments = []
    for n, line in enumerate(data[:cut].split(b"\n")[:-1], 1):
        try:
            segments.append(_parse(line))
        except (ValueError, KeyError, TypeError) as e:  # UnicodeDecodeError, JSONDecodeError는 ValueError
            raise ValueError(f"체크포인트 {n}번째 줄이 깨져 있습니다: {path}") from e
    tail = data[cut:]
    if tail:
        try:
            segments.append(_parse(tail))
        except (ValueError, KeyError, TypeError):
            os.truncate(path, cut)  # 바이트 기준. 글자 수로 자르면 한글에서 어긋난다.
        else:
            with open(path, "ab") as f:  # 온전하지만 개행만 빠진 줄. 다음 append가 이어 붙지 않게 개행을 채운다.
                f.write(b"\n")
    return segments


def append_checkpoint(path: Path, seg: Segment) -> None:
    line = json.dumps({"start": seg.start, "end": seg.end, "text": seg.text}, ensure_ascii=False) + "\n"
    with open(path, "ab") as f:
        f.write(line.encode("utf-8"))
        f.flush()
        os.fsync(f.fileno())
