"""이캠퍼스 로그인·강의 목록·스트림 주소. Task 6에서 채운다. 지금은 jobs가 쓰는 예외 두 개만 둔다."""


class UserError(Exception):
    """사용자 화면에 그대로 보여도 되는 문구를 담은 오류."""


class SchoolExpired(Exception):
    """학교 세션이 만료됐다. 다시 로그인하면 이어서 받을 수 있다."""
