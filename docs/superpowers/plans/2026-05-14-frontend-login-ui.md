# Frontend Supabase Login UI Plan

> **For agentic workers:** 이 plan은 설정 화면에 Supabase 로그인/가입/로그아웃 UI를 붙인 기록이다.

**Goal:** 사용자가 앱 안에서 Supabase 이메일/비밀번호 로그인 세션을 만들고, 이후 API 요청이 Bearer token을 사용하도록 한다.

## Implemented Scope

- `frontend/src/lib/supabase.ts`에 session 조회, 이메일/비밀번호 로그인, 가입, 로그아웃 helper를 추가했다.
- `frontend/src/App.tsx`에서 Supabase auth session을 읽고 `onAuthStateChange`로 상태를 갱신한다.
- 상단 bar에 `Supabase session` 또는 `demo user` 상태 배지를 표시한다.
- 설정 화면에 이메일/비밀번호 입력, 로그인, 가입, 로그아웃 버튼을 추가했다.
- 로그인/가입/로그아웃 후 profile/memory 데이터를 다시 불러오도록 연결했다.

## Core Logic Notes

- Supabase env가 없으면 로그인 helper가 명확한 오류를 보여주고, API 요청은 기존 demo fallback을 유지한다.
- Supabase session이 생기면 `frontend/src/lib/api.ts`가 access token을 Bearer header로 보내므로 백엔드 JWT dependency와 연결된다.
- 실제 이메일 확인 정책은 Supabase Auth 설정에 따라 달라질 수 있으므로 UI 문구에 이를 반영했다.

## Verification

```powershell
pnpm build:frontend
pnpm docs:check
```

결과:

- `pnpm build:frontend`: Vite production build 통과
- `pnpm docs:check`: 필수 문서 19개 확인 완료

## Remaining Work

- Supabase env를 채운 뒤 실제 가입/로그인 smoke를 수행한다.
- 로컬 FastAPI 서버를 켠 뒤 실제 Supabase session access token으로 `pnpm supabase:auth-smoke -- --access-token <supabase-access-token>`을 실행한다.
- 수동 token 복사 없이 확인할 때는 `pnpm supabase:login-smoke -- --email <email> --password <password>`를 실행한다.
- 로그인 상태를 sidebar에도 더 작게 노출할지 결정한다.
- Google OAuth 로그인은 Calendar consent 분리 설계와 함께 별도 slice로 진행한다.
