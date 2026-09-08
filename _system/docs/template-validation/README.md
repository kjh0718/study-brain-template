# Template Validation

`_system/templates/`의 11개 템플릿을 검사하기 위한 임시 자료다. 학습 데이터가 아니며 언제든 통째로 지워도 된다.

## 파일

| 파일 | 역할 |
|---|---|
| `check_templates.py` | A. 템플릿 자체 검사 |
| `build_filled.py` | 템플릿에 가상 값을 채워 `filled/`를 다시 만든다 |
| `check_filled_notes.py` | B. 값을 채운 가상 노트 검사 |
| `filled/` | 생성된 가상 노트와 가상 원본. `build_filled.py`가 매번 새로 만든다 |

```
python3 check_templates.py
python3 build_filled.py && python3 check_filled_notes.py
```

## 두 검사의 차이

- **A**는 양식이 스키마와 맞는지만 본다. 자리표시자는 실제 날짜나 ID가 아니므로 A를 통과했다고 해서 완성 노트 검증을 통과한 것이 아니다.
- **B**는 자리표시자를 모두 치환한 가상 노트를 본다. 필드 타입, 허용 상태, `null` 조건, 관계 대상 존재, Lecture–Resource 양방향, 로컬 `source` 존재와 외부 참조 구분, topic 등록, Course 자동 관리 영역과 보호 영역 경계를 검사한다.

**둘 다 템플릿 검증이며 L1~L9 전체 실행 테스트가 아니다.** 워크플로 실행, 로그 기록, 대시보드 갱신 절차 자체는 검증하지 않는다.

## `filled/`의 위치 규칙

`filled/`가 가상 저장소 루트 역할을 한다. 그 안의 `study/`, `wiki/`, `raw/`는 실제 학습 폴더가 아니라 경로 의미를 같게 맞추기 위한 사본 구조다. 노트의 `source` 경로는 `filled/`를 기준으로 해석한다.

저장소 루트의 실제 `study/`, `wiki/`, `raw/`에는 이 검증으로 아무 파일도 만들지 않는다.

## 가상 데이터 안내

`filled/` 안의 과목명, 강사명, 기출, 전사는 모두 지어낸 값이다. 실제 수업 자료가 아니다.
