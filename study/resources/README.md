# Resources

학습 자료를 **한 번만** 등록해 여러 강의에서 재사용하는 노트다.

## 여기 두는 것

- 자료당 RES 노트 하나
- 자료 구조, 강의별 사용 범위 요약, 판·출처

## 여기 두지 않는 것

- 원본 파일 → `raw/resources/`
- 같은 자료를 수업마다 새로 만든 노트. RES는 하나이며 Lecture와 N:N이다
- 기출 분석 → `study/past-exams/`

## 규격

[`resource.md`](../../_system/schemas/resource.md)

## 관련 워크플로

[L2 Resource ingestion](../../_system/workflows/l2-resource-ingestion.md)

사용 페이지의 기준 데이터는 `Lecture.resources[].pages`다. 본문의 Lecture Usage는 그것을 요약한 보기다.
