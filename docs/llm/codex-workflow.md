# Codex와 Superpowers 활용 방식

이 문서는 “LLM을 어떤 목적으로 사용했는지”를 설명하기 위한 핵심 자료입니다. 본 프로젝트는 Codex를 단순 코드 생성기가 아니라 PM/개발 리드의 설계, 계획, 검증 보조 도구로 사용합니다.

## 사용 원칙

- LLM이 만든 코드를 그대로 제출하지 않습니다.
- 설계, 계획, 코드 초안, 오류 분석, 테스트 아이디어를 얻는 데 사용합니다.
- 최종 코드는 팀원이 직접 읽고 수정하고 실행합니다.
- 주요 함수와 흐름은 발표에서 설명할 수 있어야 합니다.
- 사용 기록은 `docs/llm/usage-log.md`에 남깁니다.

## Superpowers 흐름

```txt
brainstorming
-> design spec
-> implementation plan
-> implementation
-> verification
-> completion record
```

## repo 안에 남기는 산출물

| 산출물 | 위치 | 목적 |
| --- | --- | --- |
| 설계 문서 | `docs/superpowers/specs/` | 요구사항, 범위, 아키텍처 확정 |
| 실행 계획 | `docs/superpowers/plans/` | 구현 순서와 검증 명령 |
| LLM 활용 기록 | `docs/llm/usage-log.md` | 제출용 LLM 사용 내역 |
| 프롬프트 요약 | `docs/llm/prompt-summary-log.md` | 중요한 요청과 결정 요약 |
| 작업 상태 | `docs/contributing/plans-status.md` | 현재 진행 상황 |
| 리뷰 대응 기록 | GitHub PR thread, 관련 plan 문서 | Gemini Code Assist/팀원 리뷰를 어떻게 반영했는지 증명 |

## Codex 사용 예시

- PRD를 읽고 MVP 범위를 줄이는 데 사용
- OpenCairn의 문서 구조를 조사하고 이 repo에 맞게 축소하는 데 사용
- README, CONTRIBUTING, AGENTS, docs index 초안 작성에 사용
- 기술 스택 후보와 공식 문서 근거를 대조하는 데 사용
- 검증 명령과 GitHub 공개 repo 세팅을 점검하는 데 사용

## 개인 Codex 스킬

김성빈의 로컬 Codex 환경에는 `kmu-freshman-ai` 전용 스킬을 둡니다.

```txt
~/.codex/skills/kmu-freshman-ai
```

이 스킬은 새 Codex 세션이 시작될 때 아래 내용을 빠르게 복원하기 위한 가이드입니다.

- 과제 조건과 제출물
- 문서 먼저 읽는 순서
- Superpowers spec/plan/verification 기록 방식
- Mini LLM Wiki와 RAG 개발 흐름
- Gemini Code Assist 리뷰 확인과 답변 방식
- 직접 push와 PR 기반 작업을 구분하는 기준

사용 예시:

```txt
Use $kmu-freshman-ai before working in the kmu-freshman-ai repo.
```

## 코드 리뷰 활용

기능 단위 작업은 PR을 통해 Gemini Code Assist 자동 리뷰와 팀원 리뷰를 받습니다. 리뷰 코멘트는 그대로 따르는 것이 아니라, 타당성을 확인한 뒤 반영하거나 반영하지 않는 이유를 답합니다. 이 과정은 “LLM 생성 코드를 그대로 제출하지 않았다”는 협업 증거로 사용합니다.

코드 주석은 설명 가능한 부분에만 답니다. 특히 RAG 검색 우선순위, wiki compiler의 병합 규칙, 추천 조건문처럼 발표에서 질문받을 가능성이 높은 의사결정에는 짧은 의도 주석을 남깁니다.
