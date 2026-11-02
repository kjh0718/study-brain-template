"""학교 CDN의 HLS(m3u8) 영상을 ffmpeg로 mp4 한 파일로 받는다. 표준 라이브러리만 쓴다."""
import ipaddress
import socket
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from config import DOWNLOAD_TIMEOUT_S, MAX_MEDIA_BYTES
from school import UserError

REFERER = "Referer: https://ecampus.sejong.ac.kr/\r\n"
STDERR_PEEK = 16 * 1024


def validate_cdn(url: str, resolve=None) -> None:
    """학교 페이지에서 뽑은 주소가 공인 IP의 https 기본 포트인지 확인한다.

    ponytail: 여기서 DNS를 확인한 뒤 ffmpeg가 다시 조회하므로 그 사이 응답이 바뀔 수 있다(DNS rebinding).
    원본과 같은 수준의 상한이고, 필요하면 확인한 IP로 고정하는 프록시를 둔다.
    """
    try:
        parsed = urlsplit(url)
        ok = parsed.scheme == "https" and parsed.hostname and parsed.port in (None, 443) and not (parsed.username or parsed.password)
    except ValueError:
        ok = False
    if not ok:
        raise UserError("영상 주소 형식이 올바르지 않습니다.")
    try:
        addresses = (resolve or socket.getaddrinfo)(parsed.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise UserError("내부 네트워크 영상 주소는 처리하지 않습니다.")
    except (OSError, ValueError):
        raise UserError("영상 서버 주소에 연결할 수 없습니다.") from None


def ffmpeg_args(ffmpeg: str, stream: str, dest: Path, referer: bool) -> list[str]:
    # 학교 쿠키는 넘기지 않는다. 서명된 URL만으로 받는다.
    args = [ffmpeg, "-nostdin", "-y", "-loglevel", "error", "-rw_timeout", "30000000",
            "-tls_verify", "1", "-protocol_whitelist", "https,tls,tcp,crypto"]
    if referer:
        args += ["-headers", REFERER]
    return args + ["-i", stream, "-c", "copy", "-fs", str(MAX_MEDIA_BYTES), "-f", "mp4", str(dest)]


def _run(args, popen, timeout) -> str:
    """'ok' | '403' | 'failed'. stderr에는 서명 URL이 있을 수 있어 403 여부만 보고 버린다."""
    with tempfile.TemporaryFile() as errors:
        proc = popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=errors)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise UserError("영상 받기가 2시간을 넘었습니다. 다시 시도해 주세요.") from None
        if not proc.returncode:
            return "ok"
        errors.seek(0)
        return "403" if b"403" in errors.read(STDERR_PEEK) else "failed"


def download_hls(stream: str, dest: Path, *, ffmpeg: str, popen=subprocess.Popen,
                 max_bytes: int = MAX_MEDIA_BYTES, timeout: int = DOWNLOAD_TIMEOUT_S) -> None:
    # ponytail: 취소 훅 없음. 작업 삭제 중에도 ffmpeg는 끝/시간 초과까지 돈다. 필요하면 proc 핸들을 밖에 노출한다.
    validate_cdn(stream)
    part = dest.with_name(dest.name + ".part")
    try:
        result = _run(ffmpeg_args(ffmpeg, stream, part, False), popen, timeout)
        if result == "403":
            result = _run(ffmpeg_args(ffmpeg, stream, part, True), popen, timeout)
        if result != "ok":
            raise UserError("영상 다운로드에 실패했습니다. 학교에서 재생 가능한 강의인지 확인해 주세요.")
        if not part.exists() or not 0 < part.stat().st_size < max_bytes:
            raise UserError("영상이 비어 있거나 파일 크기 제한을 초과했습니다.")
        part.replace(dest)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
