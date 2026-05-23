# 작업 상태

이 문서는 현재 계획과 진행 상태를 요약합니다. 세부 설계는 `docs/superpowers/specs/`, 실행 계획은 `docs/superpowers/plans/`를 확인합니다.

## 현재 활성 작업

| 날짜 | 작업 | 상태 | 관련 문서 |
| --- | --- | --- | --- |
| 2026-05-13 | repo와 문서 기반 세팅 | 초기 세팅 완료 | `docs/superpowers/plans/2026-05-13-repo-docs-initialization.md` |
| 2026-05-13 | Mini LLM Wiki foundation | 구현/검증 완료 | `docs/superpowers/plans/2026-05-13-mini-llm-wiki.md` |
| 2026-05-13 | 로그인/메인 HTML 목업 | 정적 파일 삭제, 설계 기록만 유지 | `docs/superpowers/plans/2026-05-13-login-main-mockup.md` |
| 2026-05-13 | 챗봇 근거 시각화 목업 | 정적 파일 삭제, 개인화 내비게이터 설계에 통합 | `docs/superpowers/plans/2026-05-13-chatbot-visualization-mockup.md` |
| 2026-05-13 | 개인화 SW 내비게이터 umbrella 설계 | 설계/계획 작성 완료 | `docs/superpowers/specs/2026-05-13-personalized-sw-navigator-design.md`, `docs/superpowers/plans/2026-05-13-personalized-sw-navigator-foundation.md` |
| 2026-05-13 | 프로필/메모리/chat contract foundation | 구현/검증 완료 | `docs/superpowers/plans/2026-05-13-personalized-sw-navigator-foundation.md` |
| 2026-05-14 | Navigator workspace UI shell | 구현/검증 완료, 모바일 navigation/context drawer 추가 | `docs/superpowers/plans/2026-05-14-navigator-workspace-ui.md` |
| 2026-05-14 | Supabase persistence adapter | 구현/검증 완료, live DB smoke/env check script 추가, 키 설정 대기 | `docs/superpowers/plans/2026-05-14-supabase-persistence-adapter.md` |
| 2026-05-14 | Supabase JWT auth dependency | 구현/검증 완료 | `docs/superpowers/plans/2026-05-14-supabase-jwt-auth.md` |
| 2026-05-14 | Frontend Supabase session token wiring | 구현/검증 완료 | `docs/superpowers/plans/2026-05-14-frontend-supabase-session-token.md` |
| 2026-05-14 | Frontend Supabase login UI | 구현/검증 완료, live auth smoke 대기 | `docs/superpowers/plans/2026-05-14-frontend-login-ui.md` |
| 2026-05-14 | RAG document ingest foundation | 구현/검증 완료, live insert 대기 | `docs/superpowers/plans/2026-05-14-rag-document-ingest.md` |
| 2026-05-14 | Gemini embedding service | 구현/검증 완료, live embedding key 대기 | `docs/superpowers/plans/2026-05-14-gemini-embedding-service.md` |
| 2026-05-14 | Local RAG retrieval chat evidence | 구현/검증 완료 | `docs/superpowers/plans/2026-05-14-local-rag-retrieval-chat.md` |
| 2026-05-14 | Supabase text retrieval adapter | 구현/검증 완료, live RPC smoke 대기 | `docs/superpowers/plans/2026-05-14-supabase-text-retrieval-adapter.md` |
| 2026-05-14 | Supabase vector retrieval adapter | 구현/검증 완료, live vector smoke 대기 | `docs/superpowers/plans/2026-05-14-supabase-vector-retrieval-adapter.md` |
| 2026-05-14 | Gemini answer generation | 구현/검증 완료, live Gemini smoke 대기 | `docs/superpowers/plans/2026-05-14-gemini-answer-generation.md` |
| 2026-05-14 | Chat session/message store | 구현/검증 완료, live DB smoke 대기 | `docs/superpowers/plans/2026-05-14-chat-session-message-store.md` |
| 2026-05-14 | Chat session list UI | 구현/검증 완료, live DB smoke 대기 | `docs/superpowers/plans/2026-05-14-chat-session-list-ui.md` |
| 2026-05-14 | Assignment D-day preview/list UI | 구현/집중 검증 완료, Supabase persistence/완료/삭제/Gemini parser fallback 추가, live DB/Gemini smoke 대기 | `docs/superpowers/plans/2026-05-14-assignment-dday.md` |
| 2026-05-14 | Google Calendar export foundation | 구현/집중 검증 완료, 실제 Google live smoke 대기 | `docs/superpowers/plans/2026-05-14-calendar-export-foundation.md` |
| 2026-05-14 | Google Calendar OAuth connect/callback/refresh | 구현/집중 검증 완료, live OAuth smoke 대기 | `docs/superpowers/plans/2026-05-14-google-calendar-oauth-connect.md` |
| 2026-05-14 | Track/activity recommendation | 구현/집중 검증 완료, RAG 출처 근거, 프로필/메모리 기반 입력 자동화, 직접 입력 편집 UI 완료 | `docs/superpowers/plans/2026-05-14-track-activity-recommendation.md` |
| 2026-05-14 | Google grounding | 구현/집중 검증 완료, live Gemini smoke 대기 | `docs/superpowers/plans/2026-05-14-google-grounding.md` |
| 2026-05-14 | 보고서/발표 데모 시나리오 보강 | 현재 구현 기준 문서 업데이트 완료 | `docs/product/demo-scenario.md`, `docs/report/report-outline.md`, `docs/report/presentation-outline.md` |
| 2026-05-14 | README 실행/제출 섹션 최신화 | 현재 명령어, 구현 상태, 제출 문서 링크 업데이트 완료 | `README.md`, `docs/contributing/dev-guide.md` |
| 2026-05-14 | 제출 전 체크리스트 | 과제 조건, 데모, 검증 명령, 제출 문서 매핑 완료 | `docs/report/submission-checklist.md` |
| 2026-05-14 | 최종 코드/문서 감사 | 오래된 API 이름과 구현 상태 불일치 문구 정리 완료 | `docs/architecture/data-flow.md`, `docs/product/prd-dev-plan.md`, `frontend/src/App.tsx` |
| 2026-05-14 | LLM usage log API/UI | 구현/검증 완료, chat answer generation/Google grounding/일정 parser 자동 기록과 embedding ingest 선택 기록 연결 | `docs/superpowers/plans/2026-05-14-llm-usage-log-api.md` |
| 2026-05-14 | 로컬 검증 명령 통합 | `pnpm verify:local` 추가 및 README/dev-guide/submission checklist 반영, 전체 로컬 검증 통과 | `package.json`, `README.md`, `docs/contributing/dev-guide.md`, `docs/report/submission-checklist.md` |
| 2026-05-14 | 로컬 dev server/CORS 점검 | `localhost` 접속 거부와 Vite fallback port CORS 문제를 확인하고 backend CORS regex, favicon, Playwright smoke로 정리 | `backend/app/main.py`, `backend/tests/test_cors.py`, `frontend/index.html`, `frontend/public/favicon.svg` |
| 2026-05-14 | Supabase publishable key 연결 | `frontend/.env`에 Framework client key를 설정하고 `VITE_SUPABASE_PUBLISHABLE_KEY` alias를 frontend/env smoke scripts에 반영 | `frontend/src/lib/supabase.ts`, `backend/app/scripts/check_env.py`, `backend/app/scripts/live_smoke_plan.py`, `backend/app/scripts/supabase_login_smoke.py` |
| 2026-05-16 | 에이전트 기반 코딩 증거 문서 보강 | 교수님 평가 포인트에 맞춰 Codex/Superpowers/Gemini Code Assist/Gemini API 역할, 하네스, 직접 검토 기준, 발표/보고서 연결 문서화 | `docs/llm/agent-coding-evidence.md`, `docs/llm/codex-workflow.md`, `docs/report/` |
| 2026-05-23 | 데모 UI polish | assistant 답변 Streamdown markdown 렌더링, CJK plugin, Sonner toast, Streamdown vendor chunk 분리 구현/검증 완료 | `docs/superpowers/specs/2026-05-23-demo-ui-polish-design.md`, `docs/superpowers/plans/2026-05-23-demo-ui-polish.md`, `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/vite.config.ts` |
| 2026-05-23 | Supabase live auth gate | 프론트/백엔드 런타임에서 `demo-user`/`X-User-Id` fallback을 제거하고 Supabase session Bearer token이 있어야 앱과 API를 사용할 수 있게 변경 | `frontend/src/App.tsx`, `frontend/src/lib/api.ts`, `backend/app/api/dependencies.py`, `backend/app/api/auth.py`, `backend/tests/api/test_auth_dependency.py` |
| 2026-05-23 | SaaS 제출 목표 재정렬 | 로컬 fallback을 보조 경로로 낮추고 Supabase live 연결, Python 핵심 로직 설명 가능성, LLM 활용 기록을 최종 제출 기준으로 문서화 | `docs/product/prd-dev-plan.md`, `docs/contributing/roadmap.md`, `docs/report/report-outline.md`, `docs/report/submission-checklist.md`, `docs/product/demo-scenario.md` |
| 2026-05-23 | Supabase/Gemini live readiness 점검 | backend Direct/frontend Framework/Gemini env는 ready, Gemini live smoke 3종은 통과. Supabase DB/login/LLM smoke는 `schema_ready=False`와 smoke user id/email/password 미준비로 blocker 유지 | `pnpm env:check:strict`, `pnpm live:smoke-plan`, `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke`, `docs/architecture/python-core-logic.md`, `docs/report/submission-checklist.md` |
| 2026-05-23 | RAG 자료 접수/정형화 경로 | 사용자가 제공할 교과과정/트랙/동아리/학교 시스템 자료를 `data/inbox`로 받고 `pnpm rag:prepare-raw`로 `data/raw` Markdown에 정형화하는 흐름 추가 | `backend/app/scripts/prepare_raw_document.py`, `data/inbox/README.md`, `data/README.md`, `docs/architecture/rag-data-intake.md` |
| 2026-05-23 | Supabase live smoke user/schema 분리 | service role로 Auth smoke user를 생성해 root `.env`에 저장하고, schema check command와 503 schema-missing API 응답을 추가. DB/login/LLM smoke는 모두 schema 미적용으로 분류 | `backend/app/scripts/create_smoke_user.py`, `backend/app/scripts/supabase_schema_check.py`, `backend/app/main.py`, `pnpm supabase:schema-check`, `pnpm supabase:create-smoke-user --write-root-env`, `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001` |
| 2026-05-23 | Supabase schema apply handoff | `search_document_chunks_text` RPC 인자 계약을 backend와 schema check에 맞추고, CLI가 없는 현재 환경에서 Dashboard SQL Editor 적용 절차를 문서화 | `supabase/schema.sql`, `backend/app/scripts/supabase_schema_check.py`, `backend/tests/test_supabase_schema_sql_contract.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase schema missing UX | backend의 `supabase_schema_missing` JSON error를 frontend API client가 파싱해 로그인/온보딩 중 schema 미적용 원인을 명확히 표시하도록 개선 | `frontend/src/lib/api.ts`, `frontend/src/App.tsx` |

## 다음 작업 후보

1. Supabase 프로젝트에 `supabase/schema.sql`을 적용하고 `profiles`, `user_memories`, `memory_events`, `chat_sessions`, `chat_messages`, `assignments`, `google_oauth_tokens`, `llm_usage_logs`, `document_chunks`, `search_document_chunks_text`, `match_document_chunks`가 생성됐는지 확인
2. Supabase live 검증: `pnpm env:check:strict`, `pnpm supabase:schema-check`, `pnpm supabase:smoke`, `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001`, `pnpm supabase:llm-smoke`
4. Gemini embedding ingest 검증: `pnpm rag:ingest:embeddings`
5. Google Calendar live 검증: OAuth 연결 후 `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>`

## 상태 기록 규칙

- 기능을 시작하면 이 문서에 한 줄을 추가합니다.
- 기능을 끝내면 검증 명령과 결과를 관련 plan 문서에 남깁니다.
- 실제 코드와 테스트 결과가 문서보다 우선합니다.
