# Frontend Supabase Session Token Wiring Plan

> **For agentic workers:** 이 plan은 React API client가 Supabase session access token을 백엔드로 전달하게 만든 기록이다.

**Goal:** Supabase 로그인 세션이 있으면 API 요청에 `Authorization: Bearer <access_token>`을 붙이고, 세션이 없거나 Supabase env가 없으면 기존 demo user fallback으로 로컬 실행을 유지한다.

## Implemented Scope

- `frontend/src/lib/supabase.ts`를 추가했다.
- `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`가 있을 때만 Supabase browser client를 생성한다.
- `frontend/src/lib/api.ts`가 요청 전 Supabase session access token을 확인한다.
- access token이 있으면 `Authorization` header를 사용한다.
- access token이 없으면 기존 `X-User-Id: demo-user` fallback을 사용한다.

## Core Logic Notes

- 프론트는 임의 user id보다 Supabase session token을 우선한다.
- Supabase env가 없는 발표/로컬 환경에서는 demo fallback으로 앱 shell과 API contract를 계속 시연할 수 있다.
- 실제 로그인 UI는 아직 추가하지 않았다. 다음 slice에서 Supabase email/social login 화면과 session 상태 표시를 붙인다.

## Verification

```powershell
pnpm build:frontend
pnpm test:backend
```

결과:

- `pnpm build:frontend`: Vite production build 통과
- `pnpm test:backend`: 29 passed

## Remaining Work

- 로그인 UI와 로그아웃 버튼을 추가한다.
- Supabase session 상태를 sidebar/settings에 표시한다.
- 실제 Supabase anon key, backend JWT secret, 계정 정보를 넣고 `pnpm supabase:login-smoke -- --email <email> --password <password>`로 login -> Bearer API 인증 smoke를 수행한다.
