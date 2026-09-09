# 고의 오류 fixture

<!-- 통합 시험용 가상 데이터. 실제 학습 자료가 아니다. -->

L8 무결성 검사가 각 오류를 잡는지 확인하기 위한 파일이다. **정상 노트가 아니다.**
`vault/`와 분리해 두어 정상 검사 결과를 오염시키지 않는다.

| 파일 | 심은 오류 | L8 검사 항목 |
|---|---|---|
| `bad-yaml.md` | invalid YAML | 1 |
| `bad-prefix.md` | type과 ID 접두사 불일치 | 3 |
| `bad-id-shape.md` | ID 형식 계약 위반(대문자·공백) | 3 |
| `bad-missing-ref.md` | 없는 ID 참조 | 4 |
| `bad-duplicate-concept.md` | 중복 개념 + 중복 topic slug | 7, L9 후보 |
| `bad-status.md` | 허용되지 않는 status | 2 |
| `bad-orphan.md` | orphan 노트 | 4 |
| `bad-missing-source.md` | 로컬 source 파일 없음 | 6 |
| `bad-supersedes.md` | 끊어진 supersede 참조 | 9 |
