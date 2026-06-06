# Codex와 Superpowers 활용 방식

이 문서는 “LLM을 어떤 목적으로 사용했는지”를 설명하기 위한 핵심 자료입니다. 본 프로젝트는 Codex를 단순 코드 생성기가 아니라 PM/개발 리드의 설계, 계획, 검증 보조 도구로 사용합니다.

## 사용 원칙

- 설계, 계획, 구현 보조, 오류 분석, 테스트 아이디어를 얻는 데 사용합니다.
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
- README, CONTRIBUTING, AGENTS, docs index 구조 정리에 사용
- 기술 스택 후보와 공식 문서 근거를 대조하는 데 사용
- 검증 명령과 GitHub 공개 repo 세팅을 점검하는 데 사용

## 개인 Codex 스킬

김성빈의 로컬 Codex 환경에는 현재 repo인 `kmu-sw-navigator` 작업 규칙을 복원하는 전용 스킬을 둡니다. 스킬은 새 Codex 세션이 시작될 때 아래 내용을 빠르게 복원하기 위한 가이드입니다.

```txt
~/.codex/skills/kmu-sw-navigator-rules
~/.codex/skills/kmu-sw-navigator-post-feature
```

- 과제 조건과 제출물
- 문서 먼저 읽는 순서
- Superpowers spec/plan/verification 기록 방식
- Mini LLM Wiki와 RAG 개발 흐름
- Gemini Code Assist 리뷰 확인과 답변 방식
- 직접 push와 PR 기반 작업을 구분하는 기준

사용 예시:

```txt
Use $kmu-sw-navigator-rules before working in kmu-sw-navigator.
Use $kmu-sw-navigator-post-feature to finish this kmu-sw-navigator change.
```

추가로 개발 현황을 따라가기 위한 next-step 스킬을 둡니다.

```txt
~/.codex/skills/kmu-sw-navigator-next-step
~/.codex/skills/kmu-sw-navigator-parallel-sessions
```

이 스킬은 새 세션에서 문서, git 상태, 실제 코드, 검증 기록을 함께 읽고 현재 구현 상태와 다음 구현 단위를 추천하기 위한 가이드입니다. 단순히 `plans-status.md`만 믿지 않고 실제 파일과 테스트 근거를 대조하도록 지시합니다.

사용 예시:

```txt
Use $kmu-sw-navigator-next-step to inspect current status and recommend the next slice.
Use $kmu-sw-navigator-parallel-sessions to split safe parallel worktrees and prompts.
```

## LLM 개발 하네스

이 프로젝트에서 하네스는 LLM이 마음대로 코드를 생성하지 않도록 작업 범위, 문서 읽기 순서, 검증 절차를 고정하는 운영 장치입니다. 보고서에서는 이 구조를 “AI 개발 도구를 통제하고 검증하면서 활용한 방식”으로 설명합니다.

| 구성 요소 | 위치 | 역할 |
| --- | --- | --- |
| repo 규칙 | `AGENTS.md` | 한국어 응답, 문서 읽기 순서, Superpowers 흐름, 완료 전 검증 규칙을 고정 |
| 문서 라우터 | `docs/README.md` | PRD, roadmap, feature registry, architecture, testing 문서로 이동하는 출발점 |
| 작업 상태 | `docs/contributing/plans-status.md` | 현재 활성 작업과 다음 작업 후보를 기록 |
| 기능 레지스트리 | `docs/contributing/feature-registry.md` | 기능별 소유 경로와 중복 방지 규칙을 기록 |
| 설계/계획 기록 | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 기능을 구현하기 전 요구사항과 실행 순서를 남김 |
| Codex 스킬 | `~/.codex/skills/kmu-sw-navigator-rules`, `~/.codex/skills/kmu-sw-navigator-post-feature` | 새 Codex 세션이 kmu-sw-navigator 과제 조건, repo 규칙, 완료 전 검증 절차를 복원하도록 함 |
| 다음 작업/병렬 스킬 | `~/.codex/skills/kmu-sw-navigator-next-step`, `~/.codex/skills/kmu-sw-navigator-parallel-sessions` | 현재 구현 상태를 다시 읽고 다음 vertical slice를 고르거나 안전한 worktree 병렬 작업을 나누도록 함 |
| 검증 명령 | `pnpm docs:check`, `pnpm wiki:build`, `pnpm test:backend`, `pnpm lint:backend`, `pnpm build:frontend` | 문서, Python 백엔드, wiki 생성, 프론트 빌드가 실제로 동작하는지 확인 |
| 사용 기록 | `docs/llm/usage-log.md`, `docs/llm/prompt-summary-log.md` | 어떤 목적으로 LLM을 썼고 어떤 결정을 사람이 검토했는지 제출용으로 남김 |

교수님이 에이전트 기반 코딩 과정을 확인할 수 있도록 별도 증거 문서도 둡니다.

```txt
docs/llm/agent-coding-evidence.md
```

이 문서는 에이전트 개발 하네스, Codex/Gemini Code Assist/Gemini API 역할 구분, 사람이 직접 검토한 기준, 과제 조건과의 연결을 한 번에 설명합니다.

이 구조의 핵심은 “프롬프트 한 번으로 완성된 코드”가 아니라, 다음 순서를 반복했다는 점입니다.

```txt
AGENTS.md와 docs/README.md로 규칙 복원
-> PRD/roadmap/feature registry로 범위 확인
-> spec/plan으로 구현 단위 기록
-> 코드 작성
-> 검증 명령 실행
-> usage log와 prompt summary에 LLM 사용 결과 기록
```

## 코드 리뷰 활용

기능 단위 작업은 PR을 통해 Gemini Code Assist 자동 리뷰와 팀원 리뷰를 받습니다. 리뷰 코멘트는 그대로 따르는 것이 아니라, 타당성을 확인한 뒤 반영하거나 반영하지 않는 이유를 답합니다. 이 과정은 협업과 검증 증거로 사용합니다.

코드 주석은 설명 가능한 부분에만 답니다. 특히 RAG 검색 우선순위, wiki compiler의 병합 규칙, 추천 조건문처럼 발표에서 질문받을 가능성이 높은 의사결정에는 짧은 의도 주석을 남깁니다.

## 발표에서 강조할 에이전트 활용 포인트

- Codex는 repo 문서를 먼저 읽고 feature registry와 plan을 기준으로 작업 범위를 좁히는 PM/개발 보조 역할로 사용했습니다.
- Superpowers spec/plan은 “바로 코드를 쓰는 것”을 막고 요구사항, 구현 순서, 검증 명령을 먼저 남기기 위한 하네스로 사용했습니다.
- Gemini Code Assist 리뷰는 정답이 아니라 검토 의견으로 다루고, 타당한 지적만 코드/테스트/문서에 반영했습니다.
- Gemini API는 앱 기능에서 사용하는 LLM으로, 개발 보조 에이전트인 Codex와 역할을 구분했습니다.
- 사람이 직접 한 일은 주제 결정, 범위 축소, 코드 구조 검토, 과제 조건 충족 확인, 테스트 실행, 실패 원인 판단, 문서 최신화입니다.
