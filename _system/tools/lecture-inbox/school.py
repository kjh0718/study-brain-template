"""이캠퍼스(세종대) 로그인·강의 목록·스트림 주소 파싱.

출처: EM-H20/lecture-inbox의 server/school.py를 작성자 허락을 받아 이식했다.
원본은 chuseok22-home-server의 흐름을 바탕으로 한다.
보안 전제: TLS 검증을 끄지 않는다. 학번·비밀번호는 로그인 요청 본문에만 쓰고 오류·반환값에 싣지 않는다.
쿠키는 메모리(CookieJar)에만 둔다. https://ecampus.sejong.ac.kr 밖으로 가는 리다이렉트는 막는다.
"""
import http.cookiejar
import json
import re
import ssl
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPCookieProcessor, HTTPRedirectHandler, Request, build_opener

SCHOOL = "https://ecampus.sejong.ac.kr"

class UserError(Exception):
    pass


class SchoolExpired(UserError):
    pass


class CourseParser(HTMLParser):
    """Read the school's coursefullname links and their year/semester cells."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.courses = {}
        self.cells = []
        self.cell = None
        self.link = None
        self.links = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "tr":
            self.cells, self.links = [], []
        elif tag == "td":
            self.cell = ""
        elif tag == "a" and "coursefullname" in attrs.get("class", "").split():
            parsed = urlsplit(attrs.get("href", ""))
            identifiers = parse_qs(parsed.query).get("id", [])
            if (parsed.path == "/course/view.php" and parsed.netloc in ("", "ecampus.sejong.ac.kr")
                    and len(identifiers) == 1 and re.fullmatch(r"[0-9]{1,12}", identifiers[0])):
                self.link = {"id": identifiers[0], "name": ""}

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data
        if self.link is not None:
            self.link["name"] += data

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.cells.append(" ".join(self.cell.split()))
            self.cell = None
        elif tag == "a" and self.link is not None:
            self.link["name"] = " ".join(self.link["name"].split())
            self.links.append(self.link)
            self.link = None
        elif tag == "tr" and len(self.cells) >= 2:
            for link in self.links:
                if link["name"]:
                    self.courses.setdefault(link["id"], dict(link, year=self.cells[0], semester=self.cells[1]))


class LectureParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lectures = {}
        self.identifier = None
        self.title = ""
        self.spans = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = attrs.get("class", "").split()
        if tag == "li" and {"activity", "vod"}.issubset(classes):
            match = re.fullmatch(r"module-([0-9]{1,12})", attrs.get("id", ""))
            self.identifier = match[1] if match else None
            self.title, self.spans = "", []
        elif tag == "span" and self.identifier:
            self.spans.append(classes)

    def handle_data(self, data):
        if (any("instancename" in classes for classes in self.spans)
                and not any("accesshide" in classes for classes in self.spans)):
            self.title += data

    def handle_endtag(self, tag):
        if tag == "span" and self.spans:
            self.spans.pop()
        elif tag == "li" and self.identifier:
            title = " ".join(self.title.split())
            if title:
                self.lectures.setdefault(self.identifier, {
                    "id": self.identifier, "title": title,
                    "url": SCHOOL + "/mod/vod/viewer.php?id=" + self.identifier,
                })
            self.identifier, self.spans = None, []


class PlayerParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stream = None
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "title":
            self.in_title = True
        if tag == "video" and attrs.get("data-setup-lazy"):
            try:
                config = json.loads(attrs["data-setup-lazy"])
                sources = config.get("sources", {})
                if isinstance(sources, dict):
                    self.stream = sources.get("src")
            except (ValueError, AttributeError):
                pass

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def extract_stream(html: str) -> tuple[str, str]:
    parser = PlayerParser()
    parser.feed(html)
    stream = parser.stream
    if not stream:
        match = re.search(r'https://[^\s"\'<>]+index\.m3u8', html)
        stream = match.group(0) if match else None
    if not isinstance(stream, str):
        raise UserError("영상 주소를 찾지 못했습니다. 강의 접근 권한이나 학교 플레이어 변경을 확인해 주세요.")
    parsed = urlsplit(stream)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or not parsed.path.endswith(".m3u8")
            or any(char in stream for char in "\r\n")):
        raise UserError("학교 페이지의 영상 주소 형식을 확인할 수 없습니다.")
    return stream, parser.title.strip()


class SchoolRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Credentials and cookies must stay at the explicitly selected school.
        if urlsplit(newurl).netloc != "ecampus.sejong.ac.kr" or not newurl.startswith("https://"):
            raise UserError("학교 로그인 주소가 변경되었습니다. 외부 주소로 로그인을 전달하지 않았습니다.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class SchoolSession:
    def __init__(self):
        self.opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()), SchoolRedirects())

    def page(self, path: str, form: dict | None = None) -> tuple[str, str]:
        data = urlencode(form).encode() if form else None
        request = Request(SCHOOL + path, data=data, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR,ko;q=0.9"})
        try:
            with self.opener.open(request, timeout=25) as response:
                body = response.read(8 * 1024 * 1024 + 1)
                if len(body) > 8 * 1024 * 1024:
                    raise UserError("학교 페이지 응답이 너무 큽니다.")
                return response.url, body.decode("utf-8", errors="replace")
        except HTTPError as error:
            raise UserError(f"학교 사이트가 HTTP {error.code} 오류를 반환했습니다.") from None
        except (URLError, TimeoutError, ssl.SSLError):
            raise UserError("학교 사이트에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요. 계속 실패하면 운영자에게 알려 주세요.") from None

    def login(self, student_id: str, password: str):
        url, html = self.page("/login/index.php", {
            "ssoGubun": "Login", "type": "popup_login", "username": student_id,
            "password": password, "loginbutton": "로그인",
        })
        if urlsplit(url).path in {"/login/index.php", "/login.php"} or "logout.php" not in html:
            raise UserError("학교 로그인이 확인되지 않았습니다. 학번·비밀번호를 확인하거나 학교 사이트에서 직접 로그인해 주세요.")

    def authenticated_page(self, path: str, require_logout=False):
        url, html = self.page(path)
        if (urlsplit(url).path in {"/login/index.php", "/login.php"}
                or (require_logout and "logout.php" not in html)):
            raise SchoolExpired("학교 로그인이 만료되었습니다. 다시 로그인한 뒤 재시도해 주세요.")
        return html

    def courses(self, year="all", semester="all"):
        html = self.authenticated_page("/local/ubion/user/index.php?" + urlencode({"year": year, "semester": semester}), require_logout=True)
        parser = CourseParser()
        parser.feed(html)
        return list(parser.courses.values())

    def lectures(self, identifier: str):
        html = self.authenticated_page("/course/view.php?" + urlencode({"id": identifier}))
        parser = LectureParser()
        parser.feed(html)
        return list(parser.lectures.values())

    def stream(self, identifier: str):
        return extract_stream(self.authenticated_page("/mod/vod/viewer.php?" + urlencode({"id": identifier})))


_TERMS = {"1학기": "1", "10": "1", "2학기": "2", "20": "2", "11": "summer", "21": "winter"}


def to_term(year: str, semester: str) -> str | None:
    """학교 목록의 연도·학기를 `YYYY-(1|2|summer|winter)`로 바꾼다. 모르는 값은 추측하지 않고 None."""
    if not re.fullmatch(r"\d{4}", year):
        return None
    sem = _TERMS.get(semester)
    if sem is None and "여름" in semester:
        sem = "summer"
    elif sem is None and "겨울" in semester:
        sem = "winter"
    return f"{year}-{sem}" if sem else None


def suggest_week(title: str) -> tuple[int | None, int | None]:
    """제목에서 (주차, 차시)를 제안한다. 1~99가 아니거나 없으면 None."""
    def find(pattern):
        m = re.search(pattern, title)
        return int(m[1]) if m and 1 <= int(m[1]) <= 99 else None
    return find(r"(\d{1,2})\s*주차"), find(r"(\d{1,2})\s*(?:차시|교시)")
