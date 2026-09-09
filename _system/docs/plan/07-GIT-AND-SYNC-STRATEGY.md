# 07. Git and Sync Strategy

## 목표
OneDrive를 Second Brain의 주 동기화 수단으로 사용하지 않는다.

```text
Desktop
   ↕ push/pull
GitHub
   ↕ push/pull
Laptop
```

## Repository A — study-brain-template
포함:
- 구조
- Schema
- Workflow
- Skills
- Templates
- Agent rules
- README
- 필요한 기본 Obsidian 설정

실제 개인 학습자료는 넣지 않는다.

## Repository B — 실제 Private Brain
Template 완성 후 생성한다.

예:
```text
my-second-brain
```

포함:
- 실제 Course
- Lecture
- Transcript
- Assignment
- Exam
- Past Exam
- Concept
- Review
- 개인 학습 기록

기본은 Private.

## 개발/동기화 순서
```text
study-brain-template 개발
→ GitHub push
→ Desktop/Laptop clone
→ 템플릿 완성
→ GitHub Template Repository 설정
→ Private Brain 생성
→ 실제 자료 migration
```

## 기본 Git 습관
작업 시작:
```bash
git pull
```

작업 종료:
```bash
git status
git add .
git commit -m "..."
git push
```

두 기기에서 같은 파일을 장시간 동시에 수정하는 상황을 피한다.

## 첫 GitHub Push 시점
완성 후에만 올릴 필요는 없다. 다음 정도면 scaffold checkpoint로 push 가능:
- 폴더 골격
- README-per-folder
- 최소 `.gitignore`
- 기본 설계 문서
- schema 초안

첫 commit 예:
```text
chore: initialize study brain template structure
```

## .gitkeep
사용하지 않는다. 의미 있는 `README.md`로 폴더를 유지한다.

## .gitignore
최소 정책을 선호한다.

초기 예:
```gitignore
.DS_Store
**/.obsidian/workspace*.json
.claude/worktrees/
```

필요가 실제로 생긴 항목만 추가한다.

## Git LFS
V1 템플릿 단계에서는 강제하지 않는다.

초기 방향:
- Markdown/TXT: 일반 Git
- 오디오/영상: Brain에 넣지 않는 방향
- PDF/PPT/이미지: 실제 Private Brain 사용 패턴을 본 뒤 LFS 여부 결정

LFS를 Template의 필수 의존성으로 만들지 않는다.

## OneDrive
기존 DEVSTUDY는 migration 완료 전까지 백업으로 유지할 수 있다. 새 시스템의 핵심 동기화는 Git으로 단일화한다.
