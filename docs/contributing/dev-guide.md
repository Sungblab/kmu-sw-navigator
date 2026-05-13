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
| `SUPABASE_URL` | backend, frontend | Supabase 프로젝트 URL |
| `SUPABASE_SERVICE_ROLE_KEY` | backend | 백엔드 전용 service role key |
| `SUPABASE_ANON_KEY` | frontend | 프론트엔드 공개 anon key |
| `SUPABASE_JWT_SECRET` | backend | Supabase JWT 검증용 secret |
| `GEMINI_API_KEY` | backend | Gemini API 호출 key |

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

## Supabase 세팅

1. Supabase 프로젝트를 생성합니다.
2. SQL Editor에서 `supabase/schema.sql`을 실행합니다.
3. 데모용 샘플이 필요하면 `supabase/seed.sql`을 실행합니다.
4. `document_chunks.embedding`은 실제 ingest script가 추가된 뒤 채웁니다.

## 검증 명령

```powershell
pnpm docs:check
pnpm wiki:build
cd backend
uv run pytest
uv run ruff check .
cd ..
pnpm build:frontend
```

외부 키가 필요한 검증을 실행하지 못하면 PR에 이유를 적습니다.

## 일반 문제 해결

| 증상 | 확인 |
| --- | --- |
| 백엔드가 실행되지 않음 | `uv sync` 실행 여부, Python 3.12 여부 |
| 프론트엔드가 실행되지 않음 | `pnpm install` 실행 여부, Node.js 버전 |
| CORS 오류 | `FRONTEND_ORIGIN`과 프론트 포트 확인 |
| Gemini 오류 | `GEMINI_API_KEY`, 모델명, API 사용 가능 여부 확인 |
| pgvector 오류 | Supabase에서 `vector` extension 활성화 여부 확인 |
