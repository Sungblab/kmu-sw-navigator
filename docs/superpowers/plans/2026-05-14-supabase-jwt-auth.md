# Supabase JWT Auth Implementation Plan

> **For agentic workers:** 이 plan은 테스트용 `X-User-Id` 인증에서 Supabase JWT 검증 경로로 넘어간 구현 기록이다.

**Goal:** `SUPABASE_JWT_SECRET`이 설정된 환경에서는 `Authorization: Bearer <token>`을 검증해 Supabase user id를 사용한다. 키가 없는 로컬 테스트 환경에서는 기존 `X-User-Id` dev fallback을 유지한다.

## Implemented Scope

- `backend/app/api/auth.py`에 Supabase JWT 검증 함수를 추가했다.
- `backend/app/api/dependencies.py`의 `get_current_user_id()`가 다음 순서로 동작하게 했다.
  - `SUPABASE_JWT_SECRET` 있음: Bearer token 서명과 `aud=authenticated`를 검증하고 `sub`를 user id로 사용
  - `SUPABASE_JWT_SECRET` 없음: 로컬 테스트용 `X-User-Id` header 사용
- `backend/pyproject.toml`에 `PyJWT`를 명시 dependency로 추가하고 `uv.lock`을 갱신했다.
- `backend/tests/api/test_auth_dependency.py`에 JWT 검증, missing bearer rejection, dev fallback, dependency override 테스트를 추가했다.

## Core Logic Notes

- 사용자의 신원은 request body에서 받지 않는다.
- Supabase JWT secret이 있으면 `X-User-Id`는 무시하고, 서명 검증이 끝난 token의 `sub`만 신뢰한다.
- dev fallback은 과제 테스트와 오프라인 발표 실행을 위한 경로이므로, 배포 환경에서는 `SUPABASE_JWT_SECRET`을 반드시 설정한다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\api\test_auth_dependency.py -q
cd ..
pnpm test:backend
pnpm lint:backend
pnpm docs:check
```

결과:

- `tests\api\test_auth_dependency.py`: 4 passed
- `pnpm test:backend`: 29 passed
- `pnpm lint:backend`: All checks passed
- `pnpm docs:check`: 필수 문서 19개 확인 완료

## Remaining Work

- Supabase client 로그인과 frontend session token 전달을 연결한다.
- 실제 Supabase project secret으로 API 요청 smoke를 수행한다.
