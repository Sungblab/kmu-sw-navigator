# 개발 가이드

이 문서는 팀원이 로컬에서 프로젝트를 실행하고 검증하는 방법을 설명합니다.

## 필수 도구

| 도구 | 권장 버전 | 확인 명령 |
| --- | --- | --- |
| Python | 3.12.x | `python --version` |
| uv | 최신 안정 버전 | `uv --version` |
| Node.js | 20.19 이상 | `node -v` |
| pnpm | 10 이상 | `pnpm -v` |
| Git | 최신 안정 버전 | `git --version` |

## 환경 변수

루트와 앱별 예시 파일을 복사합니다.

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

필수 값:

| 변수 | 위치 | 설명 |
| --- | --- | --- |
| `SUPABASE_URL` | backend | Supabase 프로젝트 URL |
| `SUPABASE_SERVICE_ROLE_KEY` | backend | 백엔드 전용 service role key |
| `SUPABASE_JWT_SECRET` | backend | Supabase JWT 검증용 secret |
| `VITE_SUPABASE_URL` | frontend | Supabase 프로젝트 URL |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | frontend | Supabase Framework 화면의 publishable client key |
| `VITE_SUPABASE_ANON_KEY` | frontend | 프론트엔드 공개 anon key |
| `GEMINI_API_KEY` | backend | Gemini API 호출 key |
| `GOOGLE_OAUTH_CLIENT_ID` | backend | Google Calendar consent URL 생성용 OAuth client id |
| `GOOGLE_OAUTH_CLIENT_SECRET` | backend | Google OAuth state 서명과 token 교환용 secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | backend | Google OAuth callback URL |
| `GOOGLE_CALENDAR_SCOPE` | backend | Calendar event 생성 권한 scope |

`SUPABASE_JWT_SECRET`이 설정된 백엔드는 `Authorization: Bearer <Supabase access token>`만 신뢰합니다. 이 값이 없을 때만 로컬 테스트용 `X-User-Id` header fallback을 허용합니다.

프론트엔드는 `VITE_SUPABASE_URL`과 `VITE_SUPABASE_PUBLISHABLE_KEY` 또는 `VITE_SUPABASE_ANON_KEY`가 있으면 Supabase session access token을 API 요청에 자동으로 붙입니다. 값이 없거나 로그인 세션이 없으면 `demo-user` fallback으로 요청합니다.

백엔드 CORS는 `FRONTEND_ORIGIN` 기본값인 `http://localhost:5173`을 허용하고, 로컬 Vite가 포트 충돌로 `127.0.0.1:5174`처럼 `51xx` 포트로 올라가는 경우도 개발 편의를 위해 허용합니다.

로그인 UI는 앱의 `설정` 화면에 있습니다. Supabase Auth에서 이메일/비밀번호 로그인을 켠 뒤 `frontend/.env`와 `backend/.env`를 채우면 같은 화면에서 가입, 로그인, 로그아웃을 확인할 수 있습니다.

Google Calendar 연결도 `설정` 화면에서 확인합니다. Google OAuth env가 없으면 연결 버튼은 비활성화되고, env가 있으면 백엔드가 consent URL을 만들어 프론트를 이동시킵니다. callback은 authorization code를 Google token endpoint로 교환하고 token을 server-only 저장소에 둡니다. token이 있으면 일정 내보내기 API가 Google `events.insert`를 호출하고, token이 없으면 로컬 데모용 synthetic event id로 앱 내부 export 상태를 저장합니다.

환경 변수 상태를 값 노출 없이 확인하려면 아래 명령을 실행합니다.

```powershell
pnpm env:check
pnpm live:smoke-plan
```

`env:check`는 Supabase Dashboard의 `Direct` 연결 값이 필요한 backend 항목과 `Framework` client 값이 필요한 frontend 항목을 분리해서 보여줍니다. CI나 배포 전처럼 누락 시 실패해야 하는 상황에서는 strict 모드를 씁니다.

```powershell
pnpm env:check:strict
```

## 백엔드 실행

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

헬스체크:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 프론트엔드 실행

```powershell
pnpm install
pnpm dev:frontend
```

브라우저에서 `http://localhost:5173`을 엽니다.

## 홈서버/Docker 운영 메모

라즈베리파이 같은 홈서버에서 장기 실행할 때는 로컬 개발 명령을 그대로 띄우기보다 Docker Compose로 고정된 실행 환경을 만든다. 기본 방향은 FastAPI backend container와 Vite build 결과를 제공하는 static frontend container 또는 Caddy/Nginx reverse proxy를 분리하는 것이다.

권장 경계:

- Supabase Auth/Postgres/pgvector는 외부 Supabase 프로젝트를 계속 사용한다.
- Raspberry Pi에는 앱 서버와 reverse proxy만 올리고, 비밀값은 서버의 `.env`에만 둔다.
- ARM64 환경에서 backend image build와 Node/Vite build가 되는지 별도로 확인한다.
- HTTPS, DDNS, 포트포워딩, 학교/발표장 네트워크 차단 가능성이 있으므로 발표 당일 주 데모 경로는 로컬 노트북 실행으로 둔다.

발표 데모 우선순위:

1. 노트북 로컬 실행: `pnpm dev:backend`, `pnpm dev:frontend`
2. 홈서버 URL: Docker Compose 배포가 미리 검증된 경우 보조 시연
3. 녹화/스크린샷: 외부 네트워크나 OAuth 문제가 생길 때의 백업

## Supabase 세팅

1. Supabase 프로젝트를 생성합니다.
2. SQL Editor에서 `supabase/schema.sql`을 실행합니다.
3. 데모용 샘플이 필요하면 `supabase/seed.sql`을 실행합니다.
4. `document_chunks.embedding`은 실제 ingest script가 추가된 뒤 채웁니다.
5. `SUPABASE_URL`과 `SUPABASE_SERVICE_ROLE_KEY`가 있으면 백엔드는 profile/memory를 Supabase에 저장합니다.
6. live smoke에는 Supabase Auth에서 생성된 실제 사용자 UUID가 필요합니다.

환경 변수가 없으면 백엔드는 in-memory fallback으로 실행됩니다. 이 경로는 로컬 테스트와 발표 데모용이며, 새로고침이나 서버 재시작 뒤 영속 저장을 보장하지 않습니다.

Supabase 연결 확인:

```powershell
pnpm env:check
pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>
pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>
pnpm supabase:auth-smoke -- --access-token <supabase-access-token>
pnpm supabase:login-smoke -- --email <email> --password <password>
pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>
pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>
```

성공하면 `profiles`, `user_memories`, `memory_events`에 smoke user 기준 row가 생성되고 `profile_exists=True`, `memory_status=active`가 출력됩니다.
`auth-smoke`는 실제 로그인 session access token으로 `/api/profile`을 write/read해 JWT 인증 boundary와 API Bearer token 전달을 함께 확인합니다.
`login-smoke`는 Supabase password grant로 access token을 받은 뒤 같은 API smoke를 수행하므로 수동으로 token을 복사하지 않아도 됩니다.
`llm-smoke`는 `llm_usage_logs`에 smoke row를 쓰고 같은 사용자 범위로 조회되는지 확인합니다.
`google:calendar-smoke`는 Google OAuth token이 서버 저장소에 있는 사용자로 실제 `events.insert`를 호출합니다.
`live:smoke-plan`은 비밀값을 출력하지 않고 live smoke 순서와 누락 입력을 보여줍니다.

## RAG 문서 ingest

먼저 로컬 dry-run으로 chunk 수를 확인합니다.

```powershell
pnpm rag:ingest:dry
```

Supabase env와 schema가 준비된 뒤 실제 `document_chunks` insert를 수행합니다.

```powershell
pnpm rag:ingest
```

Gemini API key까지 준비되면 embedding을 포함해 insert합니다.

```powershell
pnpm rag:ingest:embeddings
```

`rag:ingest:embeddings`는 `GEMINI_API_KEY`가 있어야 성공합니다. embedding 차원은 `GEMINI_EMBEDDING_DIM=768`을 사용합니다.

Gemini 키와 모델 설정만 먼저 검증하려면 아래 명령으로 embedding과 일정 parser를 확인합니다.

```powershell
pnpm gemini:smoke
pnpm gemini:answer-smoke
pnpm gemini:grounding-smoke
```

embedding ingest를 앱 내부 LLM 사용 기록에 남기려면 실제 Supabase user id를 명시합니다.

```powershell
cd backend
uv run python -m app.scripts.ingest_documents --raw-dir ../data/raw --wiki-dir ../data/wiki --with-embeddings --llm-log-user-id <supabase-user-id>
```

## 검증 명령

키 없이 실행 가능한 로컬 검증은 한 번에 묶어 실행할 수 있습니다.

```powershell
pnpm verify:local
```

`verify:local`은 문서 검사, Mini Wiki 생성, RAG dry-run, 제출 조건 증거 검사, 루트 테스트, 백엔드 테스트/린트, 프론트엔드 빌드를 순서대로 실행합니다.

개별 명령을 직접 실행하려면 아래 목록을 사용합니다.

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

Supabase live 검증은 키가 있을 때 별도로 실행합니다.

```powershell
pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>
pnpm supabase:auth-smoke -- --access-token <supabase-access-token>
pnpm supabase:login-smoke -- --email <email> --password <password>
pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>
pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>
```

`pnpm supabase:smoke`와 `pnpm supabase:llm-smoke`는 Supabase 키와 실제 Auth user UUID가 있어야 성공합니다. `pnpm supabase:auth-smoke`는 로컬 FastAPI 서버, `SUPABASE_JWT_SECRET`, 실제 Supabase access token이 있어야 성공합니다. `pnpm supabase:login-smoke`는 추가로 Supabase URL, anon key, 이메일/비밀번호가 필요합니다. `pnpm google:calendar-smoke`는 같은 user에 저장된 Google OAuth token이 있어야 성공합니다. 외부 키가 필요한 검증을 실행하지 못하면 PR에 이유를 적습니다.

## 일반 문제 해결

| 증상 | 확인 |
| --- | --- |
| 백엔드가 실행되지 않음 | `uv sync` 실행 여부, Python 3.12 여부 |
| 프론트엔드가 실행되지 않음 | `pnpm install` 실행 여부, Node.js 버전 |
| CORS 오류 | `FRONTEND_ORIGIN`과 프론트 포트 확인 |
| Gemini 오류 | `GEMINI_API_KEY`, 모델명, API 사용 가능 여부 확인 |
| pgvector 오류 | Supabase에서 `vector` extension 활성화 여부 확인 |
