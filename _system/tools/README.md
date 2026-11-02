# Tools

학습 노트가 아닌 보조 실행 도구를 두는 곳이다. 도구마다 하위 폴더 하나를 쓰고, 자기 README에 실행 방법을 적는다.

## 여기 두는 것

- 저장소 밖에서 돌아가며 `inbox/` 같은 입력 폴더에 파일을 넣어 주는 도구의 소스 코드
- 도구의 의존성 정의와 lock 파일(`pyproject.toml`, `uv.lock`)
- 현재 도구: [lecture-inbox](lecture-inbox/README.md) (강의 영상·음성을 전사해 `inbox/`에 넣는 Windows 로컬 도구)

## 여기 두지 않는 것

- 모델 파일, 내려받은 영상·음성, 작업 중간물, 가상환경(venv). 이들은 저장소 밖 `%LOCALAPPDATA%\lecture-inbox\`에 둔다
- 학습 노트와 원본 → `study/`, `wiki/`, `raw/`
- 검증 스위트 → `_system/docs/<이름>-validation/`

## 규격

해당 없음.

## 관련 문서

도구의 검증은 [`_system/docs/lecture-inbox-validation/`](../docs/lecture-inbox-validation/README.md)에 있고 [`run_all.py`](../docs/run_all.py)가 함께 부른다. 도구가 만든 전사의 처리는 [SECOND-BRAIN.md](../../SECOND-BRAIN.md)의 입력 정책을 따른다.
