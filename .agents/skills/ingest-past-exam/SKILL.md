---
name: ingest-past-exam
description: 기출·족보를 보존하고 문항 단위로 분석한다 (족보 분석). Use when the input is a past exam or a student-reconstructed copy — records provenance and authority, analyses each question with its original page and number, keeps provided answers separate from AI solutions, and records sample size without predicting the current exam. Triggers include 족보, 기출, 과거 시험, past exam, and "이 기출 분석해줘".
---

# ingest-past-exam

## Purpose

L3의 진입점. 기출 한 묶음을 보존하고 문항 단위로 분석한다.

## When to use

입력이 과거 시험지나 학생 복원본일 때.

## Required reading

1. [`SECOND-BRAIN.md`](../../../SECOND-BRAIN.md) — 처음부터 끝까지
2. [`l3-past-exam-ingestion.md`](../../../_system/workflows/l3-past-exam-ingestion.md)
3. [`past-exam.md`](../../../_system/schemas/past-exam.md), 새 노트를 만들면 [`_system/templates/past-exam.md`](../../../_system/templates/past-exam.md)
4. `authority` 허용 값은 [`common.md`](../../../_system/schemas/common.md)의 Shared Authority Values

## Inputs

`$ARGUMENTS` — 기출 파일 경로 또는 접근 가능한 참조. 비어 있으면 묻는다.

## Execution

1. `SECOND-BRAIN.md`를 읽는다.
2. `l3-past-exam-ingestion.md`를 읽고 그 체크리스트를 수행한다.
3. **EXM과 PEX를 혼동하지 않는다.**

   | | EXM | PEX |
   |---|---|---|
   | 대상 | **현재** 과목의 시험 | 과거 시험·족보 |
   | 담당 | L5 / [check-conflict](../check-conflict/SKILL.md) | L3 / 이 Skill |

4. 대응 과목이 없어도 시작할 수 있다. 이때 `course: null`로 둔다. 이 점이 L1·L2와 다르다.
5. 개념 후보는 L4로 넘긴다.

## Completion / reporting

`l3-past-exam-ingestion.md`의 완료 보고 형식을 쓴다. `provenance`, `authority`, 문항 수, 정답 출처 구분, 표본 수를 밝힌다.

## Do not

- **과거 출제 빈도를 현재 시험 출제 확정으로 쓰지 않는다.**
- 한 회차만으로 출제 경향을 확정하지 않는다. 패턴 승격은 L9가 판단한다.
- **기출에 적힌 일정·범위를 현재 학기의 운영 사실로 옮기지 않는다.** PEX 본문에만 남긴다.
- EXM·ASM·FAC를 만들거나 고치지 않는다. L5를 호출하지 않는다.
- 제공된 정답과 AI 풀이를 같은 절에 섞지 않는다.
- 정답을 확인하지 못했는데 `analyzed`로 올리지 않는다.
- 원본에 없는 문항 번호를 원본 번호처럼 적지 않는다.
- 같은 자료인지 다른 판본인지 불명확하면 새 PEX를 만들지 않는다.

## Example

> 2024-2 중간고사 족보인데 분석해줘.

<!-- study-brain-template -->
