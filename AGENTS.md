# kmu-sw-navigator Agent Guide

이 문서는 Codex, Claude, Gemini Code Assist 같은 AI 개발 도구와 팀원이 이 repo에서 작업할 때 따르는 규칙입니다. 모든 응답과 문서는 기본적으로 한국어로 작성합니다.

## 프로젝트 목표

국민대학교 소프트웨어융합대학 학생이 커리큘럼, 트랙, 진로/취업/창업, 동아리/활동, 학교 시스템, 과제 일정을 쉽게 탐색할 수 있도록 돕는 개인화 RAG 기반 AI 웹앱을 만든다.

MVP는 신입생 지원을 주요 데모로 유지하되, 설계 범위는 소프트웨어학부/인공지능학부 전체 학년을 지원하는 `kmu-sw-navigator` 방향으로 확장한다.

## 문서 읽기 순서

작업을 시작하기 전에 아래 순서대로 읽습니다.

1. `docs/README.md`
2. `docs/product/prd-dev-plan.md`
3. `docs/contributing/roadmap.md`
4. `docs/contributing/feature-registry.md`
5. 관련 `docs/superpowers/specs/*.md`
6. 관련 `docs/superpowers/plans/*.md`
7. 구현 대상과 관련된 `docs/architecture/*.md`, `docs/testing/*.md`

## Codex/Superpowers 워크플로우

이 repo는 LLM 활용 기록 자체가 과제 산출물입니다. 큰 기능은 다음 흐름을 남깁니다.

작업을 시작할 때는 프로젝트 전용 Codex 스킬을 먼저 호출합니다.

```txt
프로젝트 전용 Codex 스킬을 먼저 호출한 뒤 kmu-sw-navigator repo에서 작업한다.
```

1. Brainstorming: 요구사항과 범위를 정리합니다.
2. Spec: `docs/superpowers/specs/`에 설계 문서를 작성합니다.
3. Plan: `docs/superpowers/plans/`에 실행 계획을 작성합니다.
4. Implementation: 계획 단위로 구현합니다.
5. Verification: 실행한 테스트, 빌드, 수동 검증을 기록합니다.
6. Documentation Update: 변경된 기능, 상태, 실행 결과를 관련 문서에 반영합니다.
7. Code Review: 완료 전 코드 리뷰를 수행하거나 PR에서 Gemini Code Assist/팀원 리뷰를 확인합니다.
8. LLM Log: LLM 사용 목적과 결과를 `docs/llm/usage-log.md`에 남깁니다.

## 완료 전 필수 절차

모든 개발 작업이 끝날 때는 아래 절차를 생략하지 않습니다.

1. 관련 문서를 갱신합니다.
   - `docs/contributing/feature-registry.md`
   - `docs/contributing/plans-status.md`
   - 관련 `docs/superpowers/specs/*.md`
   - 관련 `docs/superpowers/plans/*.md`
   - 필요한 경우 `docs/llm/usage-log.md`
2. `superpowers:verification-before-completion`을 호출하고 검증 명령을 실행합니다.
3. `superpowers:requesting-code-review`를 호출해 코드 리뷰 관점으로 변경을 점검합니다.
4. PR 기반 작업이면 Gemini Code Assist와 팀원 리뷰를 확인하고, 반영/미반영 이유를 남깁니다.
5. 직접 push 작업이면 최소한 자체 코드 리뷰 결과와 검증 명령을 plan 또는 LLM 활용 기록에 남깁니다.

## 기여 규칙

- 새 작업은 브랜치를 만들어 진행합니다.
- 브랜치 이름 예시: `feature/rag-chat`, `feature/schedule-dday`, `docs/report-outline`
- 커밋 메시지 예시:
  - `docs: 초기 문서 구조 추가`
  - `feat(backend): RAG 검색 API 추가`
  - `feat(frontend): 챗봇 화면 추가`
  - `test(backend): 추천 로직 테스트 추가`
- PR에는 변경 요약과 검증 명령을 적습니다.
- 비밀값, API 키, 개인 계정 정보는 절대 커밋하지 않습니다.

## 코드 규칙

### Python

- Python 3.12 이상을 사용합니다.
- FastAPI route, service, schema를 역할별로 분리합니다.
- Pydantic 모델로 API 입출력을 명확히 정의합니다.
- 핵심 로직은 LLM이 생성한 코드를 그대로 제출한 것처럼 두지 않고, 팀원이 읽고 리팩토링한 구조로 정리합니다.
- 사용자 입력을 받아 의미 있는 처리 결과를 출력하는 Python 흐름을 유지합니다.
- 조건문, 반복문, 함수, 리스트/딕셔너리 사용 지점은 발표에서 설명 가능해야 합니다.
- 추천, 일정 계산, RAG 검색, 메모리 분류 같은 핵심 로직에는 왜 그런 판단을 하는지 설명하는 짧은 의도 주석을 남깁니다.
- 주석은 발표에서 질문받을 판단 기준, 추천 규칙, RAG 검색 우선순위, 민감도/저장 정책처럼 이해가 필요한 곳에만 답니다.
- 테스트는 `backend/tests/`에 둡니다.

### Python 구현 중 주석 작성 규칙

- 핵심 Python 로직을 작성하거나 수정할 때는 주석을 나중에 몰아서 붙이지 않고, 코드와 함께 작성합니다.
- 주석 대상은 수업/발표에서 질문받을 수 있는 판단 기준입니다.
  - 사용자 입력을 어떻게 분류하는지
  - 조건문 분기 기준이 무엇인지
  - 리스트/딕셔너리 규칙을 왜 그렇게 구성했는지
  - 반복문으로 어떤 후보나 문서를 순회하는지
  - 민감정보, RAG 근거, 추천, 일정 계산처럼 정책 판단이 들어가는 부분
- 단순 문법 설명은 쓰지 않습니다.
  - 나쁜 예: `# if문으로 확인한다`
  - 좋은 예: `# 일정 문장은 학업 단어와 섞여도 저장 행동이 필요하므로 먼저 분류한다.`
- 새 Python 기능을 완료할 때는 관련 설명을 필요한 경우 `docs/architecture/python-core-logic.md`에도 반영합니다.

### Frontend

- React + Vite + TypeScript를 사용합니다.
- 화면은 기능 탭 중심으로 구성합니다.
- UI 문구는 한국어로 작성합니다.
- API 호출은 `frontend/src/lib/api.ts`에 모읍니다.
- 타입은 `frontend/src/types/`에 둡니다.

### 문서

- 사용자가 보는 설명은 한국어로 씁니다.
- 문서가 오래되면 코드보다 문서를 먼저 고칩니다.
- 기능이 완료되면 `docs/contributing/feature-registry.md`와 `docs/contributing/plans-status.md`를 갱신합니다.

## 검증 기준

작업 완료 전 최소한 아래 중 관련 항목을 실행합니다.

```powershell
pnpm docs:check
pnpm wiki:build
pnpm lint:backend
pnpm test:backend
pnpm build:frontend
```

아직 의존성을 설치하지 않았거나 외부 키가 없어 실행하지 못한 경우, PR과 LLM 활용 기록에 이유를 남깁니다.

## 과제 제출 기준

- ChatGPT, Claude, Gemini, Codex 같은 LLM 사용은 허용되지만, LLM이 생성한 코드를 그대로 제출하지 않습니다.
- 제출 코드에는 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력이 확인되어야 합니다.
- 핵심 Python 기능은 단독 실행 또는 테스트로 재현 가능해야 합니다.
- LLM을 사용한 목적, 결과, 직접 검토/수정한 내용은 `docs/llm/usage-log.md`에 남깁니다.
