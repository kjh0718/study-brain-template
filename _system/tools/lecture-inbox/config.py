"""lecture-inbox 설정과 경로. 표준 라이브러리만 쓴다(검사 스위트가 시스템 Python으로 import한다)."""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[3]  # 저장소 루트
INBOX = ROOT / "inbox"

HOST = "127.0.0.1"  # 로컬 전용. 바깥에 열지 않는다
PORT = 4319
MAX_MEDIA_BYTES = 2 * 1024**3
DOWNLOAD_TIMEOUT_S = 7200

DEFAULT_MODEL = "large-v3"
KNOWN_MODELS = ("large-v3", "large-v3-turbo", "medium", "small")


@dataclass(frozen=True)
class Paths:
    home: Path
    models: Path
    work: Path
    state_file: Path
    settings_file: Path

    @classmethod
    def at(cls, home: Path) -> "Paths":
        p = cls(home, home / "models", home / "work", home / "state" / "jobs.json", home / "settings.json")
        for d in (p.models, p.work, p.state_file.parent):
            d.mkdir(parents=True, exist_ok=True)
        return p


def data_home(env: Mapping[str, str] = os.environ) -> Path:
    """모델·작업물·상태를 두는 곳. 저장소 밖이다."""
    if env.get("LECTURE_INBOX_HOME"):
        return Path(env["LECTURE_INBOX_HOME"])
    return Path(env["LOCALAPPDATA"]) / "lecture-inbox"


def load_settings(path: Path) -> dict:
    if not path.exists():
        settings = {"model": DEFAULT_MODEL}
        path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return settings
    settings = json.loads(path.read_text(encoding="utf-8"))
    if settings.get("model") not in KNOWN_MODELS:
        raise ValueError(f"settings.json의 model은 {', '.join(KNOWN_MODELS)} 중 하나여야 합니다")
    return settings
