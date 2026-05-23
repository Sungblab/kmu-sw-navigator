# kmu-sw-navigator

국민대학교 소프트웨어융합대학 학생을 위한 **개인화 RAG 기반 AI 내비게이터**입니다. 학교와 학부 자료, 사용자 프로필/메모리, 최신 웹 grounding을 함께 활용해 학업, 진로/취업/창업, 프로젝트, 일정 관리를 돕습니다.

## 프로젝트 정보

| 항목 | 내용 |
| --- | --- |
| 프로젝트명 | kmu-sw-navigator |
| 주제 | 국민대 소프트웨어융합대학 학생 개인화 RAG AI 내비게이터 |
| PM / 개발 리드 | 김성빈 |
| 팀원 | 정재훈, 이가은, 차성민, 최승범, 비타 |
| 제출 마감 | 2026년 6월 11일 |
| 과제 조건 | Python 사용, 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력, 실행 가능한 코드, LLM 활용 기록 |

## 핵심 기능

- **개인화 AI 상담**: 학년, 소속, 관심사, 진로 고민 메모리를 참고해 학업/진로/프로젝트 질문에 답합니다.
- **RAG 챗봇**: 국민대/소프트웨어학부/인공지능학부 자료를 검색하고 출처와 함께 답변합니다.
- **Mini LLM Wiki**: 원문 자료를 신입생용 위키 페이지로 정리한 뒤 RAG 검색에 우선 사용합니다.
- **트랙/활동 추천**: 관심 분야, 목표, 코딩 경험, 학습 성향을 직접 입력하거나 메모리 기반 자동값으로 추천 결과를 제공합니다.
- **최신 진로 정보 grounding**: 취업, 창업, 공모전, 기술 트렌드처럼 최신성이 필요한 주제는 웹 grounding으로 보강합니다.
- **일정 관리**: 자연어로 입력한 과제/일정을 구조화하고 D-day를 계산하며 Google Calendar 내보내기를 지원합니다.
- **Supabase 연결 점검**: backend Direct 값과 frontend Framework/client 값을 분리해 확인합니다.
- **LLM 활용 기록**: 앱 내부 Gemini 사용 기록과 Codex 기반 개발 워크플로우를 함께 남깁니다.
- **발표/보고서 지원**: 라이브 시연 순서, 보고서 목차, 코드 설명 포인트를 repo 안에서 관리합니다.

## 기술 스택

| 영역 | 선택 |
| --- | --- |
| Frontend | React, Vite, TypeScript, Tailwind CSS, lucide-react |
| Backend | Python 3.12, FastAPI, Pydantic, Uvicorn |
| Database/Auth | Supabase Auth, Supabase Postgres |
| Vector Search | Supabase pgvector, `vector(768)` |
| LLM | Gemini API, `google-genai` |
| Package/Dev | uv, pnpm workspace |
| 문서/협업 | Superpowers 방식의 spec, plan, execution log, LLM usage log |

## 문서 먼저 읽기

이 repo는 문서를 작업 라우터로 사용합니다.

1. [docs/README.md](docs/README.md): 전체 문서 인덱스
2. [docs/product/prd-dev-plan.md](docs/product/prd-dev-plan.md): 초기 PRD와 개발 계획
3. [docs/contributing/dev-guide.md](docs/contributing/dev-guide.md): 로컬 개발 환경
4. [docs/contributing/feature-registry.md](docs/contributing/feature-registry.md): 기능 소유 영역
5. [docs/llm/codex-workflow.md](docs/llm/codex-workflow.md): Codex/Superpowers 활용 방식
6. [docs/architecture/mini-llm-wiki.md](docs/architecture/mini-llm-wiki.md): Mini LLM Wiki 설계
7. [CONTRIBUTING.md](CONTRIBUTING.md): 팀원 기여 방법

## 빠른 시작

### 1. 필수 도구

- Python 3.12+
- uv
- Node.js 20.19+
- pnpm 10+
- Supabase 프로젝트
- Gemini API Key

Docker는 기본 개발 흐름에 필요하지 않습니다. Supabase를 로컬 컨테이너로 완전히 재현하고 싶을 때만 선택적으로 사용합니다. 수업 제출용 MVP는 Supabase Cloud와 `supabase/schema.sql` 실행만으로 진행합니다.

### 2. 환경 변수

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

`.env`와 각 앱의 `.env`에 Supabase와 Gemini 값을 채웁니다. 비밀값은 커밋하지 않습니다.

Supabase Dashboard 기준으로는 다음처럼 나눕니다.

| 위치 | 값 |
| --- | --- |
| `backend/.env` | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET` |
| `frontend/.env` | `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` 또는 `VITE_SUPABASE_ANON_KEY` |

`SUPABASE_SERVICE_ROLE_KEY`는 backend 전용입니다. frontend env에 넣지 않습니다.

값을 넣기 전에도 환경 상태는 확인할 수 있습니다.

```powershell
pnpm env:check
pnpm live:smoke-plan
```

### 3. 백엔드 실행

```powershell
uv sync
pnpm dev:backend
```

백엔드 헬스체크:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 4. 프론트엔드 실행

```powershell
pnpm install
pnpm dev:frontend
```

프론트엔드는 기본적으로 `http://localhost:5173`에서 실행됩니다.

### 5. RAG 문서 준비

Mini LLM Wiki를 재생성합니다.

```powershell
pnpm wiki:build
```

Supabase나 Gemini 키 없이 ingest payload를 미리 확인합니다.

```powershell
pnpm rag:ingest:dry
```

Supabase schema와 env가 준비되면 실제 insert를 실행합니다.

```powershell
pnpm rag:ingest
```

Gemini key까지 있으면 embedding을 포함해 넣습니다.

```powershell
pnpm rag:ingest:embeddings
```

Gemini API key 자체를 먼저 확인하려면 embedding과 일정 parser smoke를 실행합니다.

```powershell
pnpm gemini:smoke
pnpm gemini:answer-smoke
pnpm gemini:grounding-smoke
```

embedding ingest도 LLM 사용 기록으로 남기려면 실제 Supabase user id를 지정합니다.

```powershell
cd backend
uv run python -m app.scripts.ingest_documents --raw-dir ../data/raw --wiki-dir ../data/wiki --with-embeddings --llm-log-user-id <supabase-user-id>
```

### 6. Supabase live smoke

Supabase 프로젝트에 `supabase/schema.sql`을 적용한 뒤 실행합니다.

```powershell
pnpm supabase:sql-copy
pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>
pnpm env:check:strict
pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>
pnpm supabase:auth-smoke -- --access-token <supabase-access-token>
pnpm supabase:login-smoke -- --email <email> --password <password>
pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>
pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>
```

`--user-id`에는 Supabase Auth에서 실제 생성된 사용자 UUID를 넣습니다. `profiles.id`, `assignments.user_id`, `user_memories.user_id`가 `auth.users(id)`를 참조하므로 임의 문자열은 live DB에서 실패합니다.
`--access-token`은 설정 화면에서 실제 로그인한 Supabase session의 access token입니다. 이 smoke는 FastAPI가 `Authorization: Bearer` 토큰을 검증하고 `/api/profile` write/read를 수행하는지 확인합니다.
`login-smoke`는 Supabase email/password login으로 access token을 받은 뒤 profile과 onboarding memory API smoke를 실행하므로 수동 token 복사 없이 가입/로그인/API 요청을 한 번에 확인할 때 사용합니다.
`llm-smoke`는 `llm_usage_logs`에 smoke row를 쓰고 같은 사용자 범위로 다시 조회되는지 확인합니다.
`google:calendar-smoke`는 같은 사용자에게 저장된 Google Calendar token이 있을 때 실제 `events.insert` 경로를 검증합니다.
`live:smoke-plan`은 비밀값을 출력하지 않고 어떤 smoke가 준비됐고 무엇이 빠졌는지 순서대로 보여줍니다.

현재 repo는 실제 Supabase 로그인과 live smoke를 최종 기준으로 둡니다. in-memory fallback은 단위 테스트와 장애 분석용 보조 경로이며, 사용자에게 보여주는 기본 흐름은 Supabase Auth 세션이 있어야 진행됩니다.

### 7. 검증

```powershell
pnpm verify:local
```

`verify:local`은 외부 키 없이 실행 가능한 문서 검사, Mini Wiki 생성, RAG dry-run, 제출 조건 증거 검사, Python 테스트, 백엔드 테스트/린트, 프론트엔드 빌드를 순서대로 실행합니다.

개별 명령을 따로 확인하려면 아래 명령을 실행합니다.

```powershell
pnpm docs:check
pnpm wiki:build
pnpm rag:ingest:dry
pnpm test:backend
python -m pytest tests
pnpm lint:backend
pnpm build:frontend
pnpm submission:check
```

`docs:check`는 제출과 협업에 필요한 핵심 문서가 존재하는지 검사합니다.

## 현재 구현 상태

구현/검증 상태는 [docs/contributing/plans-status.md](docs/contributing/plans-status.md)를 기준으로 확인합니다.

현재 완료된 주요 항목:

- Claude/NotebookLM식 workspace UI shell
- Supabase profile/memory/chat/session/assignment 저장소 adapter와 in-memory fallback
- Supabase JWT auth dependency와 frontend session token forwarding
- Mini LLM Wiki, local RAG, Supabase text/vector retrieval adapter
- Gemini answer generation, embedding, 일정 parser, Google grounding adapter
- 채팅 세션/메시지 저장과 recent chat UI
- 자연어 일정 preview/list/complete/delete/D-day
- Google Calendar OAuth/connect/token refresh/export adapter
- 트랙/활동 추천 API, RAG 근거, 직접 입력 편집 UI
- LLM usage log API와 LLM 기록 화면
- `env:check`, `supabase:smoke`, 보고서/발표 라이브 시연 문서
- `live:smoke-plan`으로 제출 전 live smoke 준비 상태 점검
- `supabase:auth-smoke`로 실제 Supabase access token API 요청 검증 경로
- `supabase:login-smoke`로 Supabase email/password login 후 API 요청 검증 경로
- `supabase:llm-smoke`로 Supabase LLM 사용 기록 insert/list 검증 경로
- `google:calendar-smoke`로 Google Calendar event insert 검증 경로
- `gemini:smoke`로 Gemini embedding/일정 parser live 검증 경로
- `gemini:answer-smoke`로 Gemini 답변 생성 live 검증 경로
- `gemini:grounding-smoke`로 Gemini Google Search grounding live 검증 경로

아직 live blocker가 남은 항목:

- Supabase live DB smoke
- 실제 Supabase Auth 가입/로그인/API 요청 smoke
- Google Calendar OAuth consent와 실제 event insert smoke

## 개발 원칙

- 기능을 만들기 전 `docs/superpowers/specs/`에 설계를 남깁니다.
- 구현 전에 `docs/superpowers/plans/`에 실행 계획을 남깁니다.
- LLM을 사용하면 `docs/llm/usage-log.md`에 목적과 결과를 기록합니다.
- 새 기능은 `feature/<short-name>` 브랜치에서 작업합니다.
- PR에는 실행한 검증 명령을 반드시 적습니다.
- 발표에서 설명할 수 없는 코드는 제출하지 않습니다.

## GitHub 운영

- 기본 브랜치: `main`
- 공개 repo로 운영합니다.
- 이슈로 작업 단위를 만들고, 브랜치와 PR을 연결합니다.
- 팀원이 구현한 기능은 PR 리뷰 후 병합합니다.
- 김성빈은 PM/개발 리드로 설계, 통합, 검증, 발표 흐름을 관리합니다.

## 과제 조건 매핑

| 조건 | 충족 방식 |
| --- | --- |
| Python 사용 | FastAPI 백엔드, RAG, Gemini 호출, 일정 계산, Supabase adapter |
| 사용자 입력 | 질문, 추천 조건, 자연어 일정 입력, 로그인/프로필 |
| 조건문 | 메모리 민감도, intent 분류, 트랙/활동 추천, 일정 parser fallback |
| 반복문 | 문서 chunk 처리, 추천 후보 평가, 일정 목록, 로그 목록 |
| 함수 | RAG 검색, 임베딩 생성, 추천, D-day 계산, Calendar event 생성 |
| 리스트/딕셔너리 | 추천 규칙, 문서 목록, evidence payload, assignments, logs |
| 의미 있는 출력 | Mini LLM Wiki, 근거 기반 답변, 추천 결과, D-day, Calendar export 상태, LLM 기록 |
| 실행 가능한 코드 | 프론트엔드와 백엔드 로컬 실행 |
| LLM 활용 기록 | `docs/llm/usage-log.md`, `docs/llm/codex-workflow.md` |

## 제출/발표 자료

| 목적 | 문서 |
| --- | --- |
| 라이브 시연 흐름 | [docs/product/live-scenario.md](docs/product/live-scenario.md) |
| 보고서 목차와 문장 초안 | [docs/report/report-outline.md](docs/report/report-outline.md) |
| 발표 구성과 시간 배분 | [docs/report/presentation-outline.md](docs/report/presentation-outline.md) |
| 제출 전 체크리스트 | [docs/report/submission-checklist.md](docs/report/submission-checklist.md) |
| 핵심 Python 로직 설명 | [docs/architecture/python-core-logic.md](docs/architecture/python-core-logic.md) |
| LLM 활용 기록 | [docs/llm/usage-log.md](docs/llm/usage-log.md) |

## 라이선스

MIT License를 사용합니다. 자세한 내용은 [LICENSE](LICENSE)를 확인하세요.
