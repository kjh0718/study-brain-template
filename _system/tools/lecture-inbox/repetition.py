"""Whisper 반복 루프 탐지. Chuseok22/transcribe-inbox에서 이식했다(MIT)."""
from difflib import SequenceMatcher

from transcript import Segment

MIN_REPEAT_RUN = 3
SIMILARITY_THRESHOLD = 0.9
MIN_REPEAT_TEXT_LENGTH = 5  # "네" 같은 짧은 맞장구의 반복은 정상 발화다


def find_repetition_span(segments: list[Segment]) -> tuple[int, int] | None:
    """거의 같은 구간이 3개 이상 이어지는 첫 구간의 (처음, 마지막) 인덱스. 양끝 포함."""
    run_start = 0
    for i in range(1, len(segments)):
        if SequenceMatcher(None, segments[i - 1].text, segments[i].text).ratio() < SIMILARITY_THRESHOLD:
            span = _qualifying(segments, run_start, i - 1)
            if span:
                return span
            run_start = i
    return _qualifying(segments, run_start, len(segments) - 1) if segments else None


def _qualifying(segments: list[Segment], start: int, end: int) -> tuple[int, int] | None:
    if end - start + 1 < MIN_REPEAT_RUN or len(segments[start].text) < MIN_REPEAT_TEXT_LENGTH:
        return None
    return (start, end)
