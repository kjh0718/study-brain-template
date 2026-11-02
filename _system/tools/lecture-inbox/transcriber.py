"""faster-whisper 전사: 체크포인트 이어하기와 반복 구간 재디코딩.

반복 재디코딩은 Chuseok22/transcribe-inbox의 whisper.py(MIT)를 faster-whisper 위로 이식했다.
"""
import logging
from pathlib import Path
from typing import Callable, Sequence

from repetition import find_repetition_span
from transcript import Segment, append_checkpoint, read_checkpoint

log = logging.getLogger(__name__)

SAMPLE_RATE = 16000
MIN_TAIL_SECONDS = 1.0  # 이만큼도 안 남았으면 이어서 디코딩하지 않는다
PAD_SECONDS = 0.5
MAX_RETRY_SPAN_SECONDS = 180.0
REPETITION_MARK = "[⚠️ 반복 감지 - 확인 필요] "
BASE_OPTIONS = {"language": "ko", "vad_filter": True, "condition_on_previous_text": False}
# 원본의 [] / ["-et", "2.6", "-tp", "0.5"]에 대응한다.
RETRY_OPTIONS = ({}, {"temperature": 0.5, "compression_ratio_threshold": 2.6})


class WhisperEngine:
    def __init__(self, model_dir: Path):
        from faster_whisper import WhisperModel  # 무거운 import라 엔진을 만들 때만 한다

        self.model = WhisperModel(str(model_dir), device="cpu", compute_type="int8")

    def segments(self, audio, offset: float, **options):
        """offset을 더한 원본 기준 타임스탬프의 Segment를 낸다. text는 strip된 상태."""
        found, _info = self.model.transcribe(audio, **options)
        for s in found:
            yield Segment(offset + s.start, offset + s.end, s.text.strip())


def load_audio(path: Path):
    # ponytail: 파일 전체를 한 번에 디코딩한다. float32로 1시간에 약 230MB라 4시간 이상의 녹음이
    # 생기면 청크 단위로 디코딩하도록 바꾼다.
    from faster_whisper import decode_audio

    return decode_audio(str(path), sampling_rate=SAMPLE_RATE)


def transcribe(audio: Sequence[float], work: Path, engine, on_progress: Callable[[float], None] = lambda f: None) -> tuple[list[Segment], int]:
    """(최종 구간, 미해결 반복 수). 이미 디코딩한 만큼은 체크포인트에서 읽고 나머지만 디코딩한다."""
    duration = len(audio) / SAMPLE_RATE
    ckpt, marker = work / "segments.jsonl", work / "decoded"
    segments = read_checkpoint(ckpt)  # 재시작 뒤 첫 append 전에 반드시 호출: 잘린 꼬리를 고친다
    if not marker.exists():
        offset = segments[-1].end if segments else 0.0
        if duration - offset >= MIN_TAIL_SECONDS:
            for seg in engine.segments(audio[int(offset * SAMPLE_RATE):], offset, **BASE_OPTIONS):
                if not seg.text or seg.start < offset - 0.05:  # 체크포인트된 시간은 다시 쓰지 않는다
                    continue
                append_checkpoint(ckpt, seg)
                segments.append(seg)
                on_progress(min(seg.end / duration, 1.0))
        marker.touch()
    return resolve_repetitions(segments, audio, engine)


def resolve_repetitions(segments: list[Segment], audio: Sequence[float], engine) -> tuple[list[Segment], int]:
    unresolved = 0
    search_from = 0
    while True:
        span = find_repetition_span(segments[search_from:])
        if span is None:
            return segments, unresolved
        start, end = search_from + span[0], search_from + span[1]
        fixed, ok = _retry_span(segments[start:end + 1], audio, engine)
        unresolved += not ok
        segments = segments[:start] + fixed + segments[end + 1:]
        search_from = start + len(fixed)  # 항상 앞으로만 움직이므로 루프가 끝난다


def _retry_span(span: list[Segment], audio: Sequence[float], engine) -> tuple[list[Segment], bool]:
    first, last = span[0], span[-1]
    placeholder = [Segment(first.start, last.end, REPETITION_MARK + first.text)]
    if last.end - first.start > MAX_RETRY_SPAN_SECONDS:
        log.warning("반복 구간 %.0f-%.0f초가 너무 길어 재시도 없이 표시만 합니다.", first.start, last.end)
        return placeholder, False
    duration = len(audio) / SAMPLE_RATE
    clip_offset = max(0.0, first.start - PAD_SECONDS)
    clip = audio[int(clip_offset * SAMPLE_RATE):int(min(duration, last.end + PAD_SECONDS) * SAMPLE_RATE)]
    for opts in RETRY_OPTIONS:
        try:
            retried = [s for s in engine.segments(clip, clip_offset, **{**BASE_OPTIONS, **opts}) if s.text]
        except Exception:  # 재시도 실패가 멀쩡한 전사 전체를 무너뜨리면 안 된다
            log.warning("반복 구간 재디코딩 실패 (%.0f-%.0f초)", first.start, last.end, exc_info=True)
            continue
        if retried and find_repetition_span(retried) is None:
            return retried, True
    log.warning("반복 구간 %.0f-%.0f초를 해결하지 못해 표시합니다.", first.start, last.end)
    return placeholder, False
