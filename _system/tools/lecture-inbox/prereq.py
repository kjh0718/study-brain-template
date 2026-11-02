"""ffmpeg와 Whisper 모델 준비. 표준 라이브러리만 맨 위에서 import한다(faster_whisper는 필요할 때 지연 import)."""
import os
import shutil
import subprocess
from pathlib import Path

WINGET_COMMAND = ["winget", "install", "--id", "Gyan.FFmpeg", "-e"]


def ffmpeg_path(env=os.environ, which=shutil.which) -> "str | None":
    found = which("ffmpeg")
    if found:
        return found
    # winget으로 방금 설치했다면 이 프로세스의 PATH에는 아직 없고 Links 폴더에만 있다
    local = env.get("LOCALAPPDATA")
    if local:
        link = Path(local) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe"
        if link.is_file():
            return str(link)
    return None


def offer_ffmpeg_install(ask=input, run=subprocess.run) -> bool:
    print("ffmpeg가 없습니다. 이캠퍼스 영상 다운로드에 필요합니다(파일 업로드 전사는 없어도 됩니다).")
    print("설치 명령: " + " ".join(WINGET_COMMAND))
    try:
        answer = ask("지금 설치할까요? [y/N] ")
    except EOFError:
        return False
    if answer.strip().lower() != "y":
        return False
    try:
        result = run(WINGET_COMMAND)
    except OSError:
        print("winget을 실행하지 못했습니다. 위 명령을 직접 실행해 주세요.")
        return False
    if getattr(result, "returncode", 0) != 0:
        print("ffmpeg 설치에 실패했습니다. 위 명령을 터미널에서 직접 실행해 확인해 주세요.")
        return False
    return True


def ensure_model(name: str, models_dir: Path, download=None) -> Path:
    target = models_dir / name
    if (target / "model.bin").is_file():
        return target
    if download is None:
        from faster_whisper import download_model as download
    download(name, output_dir=str(target))
    return target
