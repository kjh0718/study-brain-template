# 04. Source and Trust Policy

## 핵심 원칙
Study Brain에서 원문(Evidence)과 구조화된 해석(Structured Knowledge)은 같은 것이 아니다.

```text
Raw Source
→ Evidence
→ Structured Note
→ AI Summary / Interpretation
```

각 층위를 혼동하지 않는다.

## Raw Source 보존
수업 전체 전사본은 분석 전에 먼저 저장한다. 원문은 교수 표현 확인, 잘못된 요약 검증, 시험/과제 일정 근거 확인, 추후 재분석, hallucination 교정에 필요하다.

AI는 Raw Source를 정리 편의를 위해 조용히 수정하거나 요약본으로 대체하지 않는다.

## 외부 transcription
V1에서는 audio-to-text 자체를 Study Brain 책임으로 두지 않는다.

```text
recording
→ CLOVA/Gemini/기타 transcription
→ full transcript
→ Study Brain
```

## Authority
중요한 사실은 출처 권위를 구분한다.

권장 값:
```text
professor
official-lms
course-material
textbook
student-provided
external
ai-generated
unknown
```

일반적인 우선순위 예:
```text
교수의 명시적 발언 / 공식 LMS
> 교수 배포 자료
> 교재
> 학생 제공 자료
> 외부 자료
> AI 추론
```

다만 실제 충돌 해결을 단순 순위만으로 자동 처리하지 않는다.

## Confidence
필요한 경우 `high`, `medium`, `low`, `needs-review`를 사용한다. Confidence는 authority와 별개다.

예:
- 학생이 직접 올린 족보 파일이라는 사실: authority=`student-provided`, confidence=`high`
- 그 족보 정답이 맞다는 주장: authority=`student-provided`, answer_status=`unverified`

## Provenance
중요한 구조화 사실은 가능한 한 출처 ID를 가진다.

```yaml
source_refs:
  - LEC-20260908-01
  - RES-general-physics-2-ch03-slides
```

AI 자체 추론을 교수 발언이나 공식 사실처럼 기록하지 않는다.

## Conflict 처리

### 명시적 변경
> 중간고사는 10월 15일이 아니라 10월 17일로 변경합니다.

새 Fact가 기존 Fact를 명시적으로 대체한다. supersede를 자동 적용할 수 있다.

### 애매한 충돌
기존: 시험 10월 15일  
신규: 시험은 10월 17일쯤...

명시적 변경인지 불확실하면 자동 덮어쓰기 금지. `needs-review`로 두고 사용자 확인.

## Supersede History
과거 정보는 삭제하지 않는다.

대체 관계는 **새 Fact가 이전 Fact를 가리키는 한 방향만** 저장한다.

새 Fact:
```yaml
status: active
supersedes:
  - FAC-...
```

이전 Fact:
```yaml
status: superseded
```

이전 Fact에 `superseded_by`를 두지 않는다. 역방향이 필요하면 `supersedes`에 그 ID가 들어 있는 Fact를 검색해 결정적으로 찾는다. 양방향 필드를 함께 두면 한쪽만 갱신됐을 때 drift가 생기고, 무결성 검사가 어느 쪽을 정본으로 볼지 정할 수 없다.

## Exam 관련 보수성
다음을 구분한다.

```text
교수가 "시험에 낸다"라고 명시
≠ PPT에 별표가 있음
≠ 족보에 자주 나옴
≠ AI가 중요해 보인다고 판단
```

## Evidence Recall
일반 Recall에서는 Raw 전체를 기본 검색하지 않는다. 사용자가 정확한 교수 발언, 마감일 근거, 원문, 시험 범위 확정 근거를 요구할 때만 Raw Evidence까지 확장한다.
