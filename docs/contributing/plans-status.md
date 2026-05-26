# 작업 상태

이 문서는 현재 계획과 진행 상태를 요약합니다. 세부 설계는 `docs/superpowers/specs/`, 실행 계획은 `docs/superpowers/plans/`를 확인합니다.

## 현재 활성 작업

| 날짜 | 작업 | 상태 | 관련 문서 |
| --- | --- | --- | --- |
| 2026-05-13 | repo와 문서 기반 세팅 | 초기 세팅 완료 | `docs/superpowers/plans/2026-05-13-repo-docs-initialization.md` |
| 2026-05-13 | Mini LLM Wiki foundation | 구현/검증 완료 | `docs/superpowers/plans/2026-05-13-mini-llm-wiki.md` |
| 2026-05-13 | 로그인/메인 초기 정적 화면 | 정적 파일 삭제, 설계 기록만 유지 | `docs/superpowers/plans/` archived screen plan |
| 2026-05-13 | 챗봇 근거 시각화 초기 정적 화면 | 정적 파일 삭제, 개인화 내비게이터 설계에 통합 | `docs/superpowers/plans/` archived visualization plan |
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
| 2026-05-14 | 보고서/발표 라이브 시연 시나리오 보강 | 현재 구현 기준 문서 업데이트 완료 | `docs/product/live-scenario.md`, `docs/report/report-outline.md`, `docs/report/presentation-outline.md` |
| 2026-05-14 | README 실행/제출 섹션 최신화 | 현재 명령어, 구현 상태, 제출 문서 링크 업데이트 완료 | `README.md`, `docs/contributing/dev-guide.md` |
| 2026-05-14 | 제출 전 체크리스트 | 과제 조건, 라이브 시연, 검증 명령, 제출 문서 매핑 완료 | `docs/report/submission-checklist.md` |
| 2026-05-14 | 최종 코드/문서 감사 | 오래된 API 이름과 구현 상태 불일치 문구 정리 완료 | `docs/architecture/data-flow.md`, `docs/product/prd-dev-plan.md`, `frontend/src/App.tsx` |
| 2026-05-14 | LLM usage log API/UI | 구현/검증 완료, chat answer generation/Google grounding/일정 parser 자동 기록과 embedding ingest 선택 기록 연결 | `docs/superpowers/plans/2026-05-14-llm-usage-log-api.md` |
| 2026-05-14 | 로컬 검증 명령 통합 | `pnpm verify:local` 추가 및 README/dev-guide/submission checklist 반영, 전체 로컬 검증 통과 | `package.json`, `README.md`, `docs/contributing/dev-guide.md`, `docs/report/submission-checklist.md` |
| 2026-05-14 | 로컬 dev server/CORS 점검 | `localhost` 접속 거부와 Vite fallback port CORS 문제를 확인하고 backend CORS regex, favicon, Playwright smoke로 정리 | `backend/app/main.py`, `backend/tests/test_cors.py`, `frontend/index.html`, `frontend/public/favicon.svg` |
| 2026-05-14 | Supabase publishable key 연결 | `frontend/.env`에 Framework client key를 설정하고 `VITE_SUPABASE_PUBLISHABLE_KEY` alias를 frontend/env smoke scripts에 반영 | `frontend/src/lib/supabase.ts`, `backend/app/scripts/check_env.py`, `backend/app/scripts/live_smoke_plan.py`, `backend/app/scripts/supabase_login_smoke.py` |
| 2026-05-16 | 에이전트 기반 코딩 증거 문서 보강 | 교수님 평가 포인트에 맞춰 Codex/Superpowers/Gemini Code Assist/Gemini API 역할, 하네스, 직접 검토 기준, 발표/보고서 연결 문서화 | `docs/llm/agent-coding-evidence.md`, `docs/llm/codex-workflow.md`, `docs/report/` |
| 2026-05-23 | Live UI polish | assistant 답변 Streamdown markdown 렌더링, CJK plugin, Sonner toast, Streamdown vendor chunk 분리 구현/검증 완료 | `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/vite.config.ts` |
| 2026-05-23 | Supabase live auth gate | 프론트/백엔드 런타임에서 예전 우회 인증 fallback을 제거하고 Supabase session Bearer token이 있어야 앱과 API를 사용할 수 있게 변경 | `frontend/src/App.tsx`, `frontend/src/lib/api.ts`, `backend/app/api/dependencies.py`, `backend/app/api/auth.py`, `backend/tests/api/test_auth_dependency.py` |
| 2026-05-23 | SaaS 제출 목표 재정렬 | 로컬 fallback을 보조 경로로 낮추고 Supabase live 연결, Python 핵심 로직 설명 가능성, LLM 활용 기록을 최종 제출 기준으로 문서화 | `docs/product/prd-dev-plan.md`, `docs/contributing/roadmap.md`, `docs/report/report-outline.md`, `docs/report/submission-checklist.md`, `docs/product/live-scenario.md` |
| 2026-05-23 | Supabase/Gemini live readiness 점검 | backend Direct/frontend Framework/Gemini env는 ready, Gemini live smoke 3종은 통과. Supabase DB/login/LLM smoke는 `schema_ready=False`와 smoke user id/email/password 미준비로 blocker 유지 | `pnpm env:check:strict`, `pnpm live:smoke-plan`, `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke`, `docs/architecture/python-core-logic.md`, `docs/report/submission-checklist.md` |
| 2026-05-23 | RAG 자료 접수/정형화 경로 | 사용자가 제공할 교과과정/트랙/동아리/학교 시스템 자료를 `data/inbox`로 받고 `pnpm rag:prepare-raw`로 `data/raw` Markdown에 정형화하는 흐름 추가 | `backend/app/scripts/prepare_raw_document.py`, `data/inbox/README.md`, `data/README.md`, `docs/architecture/rag-data-intake.md` |
| 2026-05-23 | Supabase live smoke user/schema 분리 | service role로 Auth smoke user를 생성해 root `.env`에 저장하고, schema check command와 503 schema-missing API 응답을 추가. DB/login/LLM smoke는 모두 schema 미적용으로 분류 | `backend/app/scripts/create_smoke_user.py`, `backend/app/scripts/supabase_schema_check.py`, `backend/app/main.py`, `pnpm supabase:schema-check`, `pnpm supabase:create-smoke-user --write-root-env`, `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001` |
| 2026-05-23 | Supabase schema apply handoff | `search_document_chunks_text` RPC 인자 계약을 backend와 schema check에 맞추고, CLI가 없는 현재 환경에서 Dashboard SQL Editor 적용 절차를 문서화 | `supabase/schema.sql`, `backend/app/scripts/supabase_schema_check.py`, `backend/tests/test_supabase_schema_sql_contract.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase schema missing UX | backend의 `supabase_schema_missing` JSON error를 frontend API client가 파싱해 로그인/온보딩 중 schema 미적용 원인을 명확히 표시하도록 개선 | `frontend/src/lib/api.ts`, `frontend/src/App.tsx` |
| 2026-05-23 | Live smoke runner | schema 적용 직후 `pnpm live:smoke-run --api-base http://127.0.0.1:8001` 하나로 Supabase DB/LLM/login, Gemini, embedding ingest를 순차 검증하도록 runner 추가 | `backend/app/scripts/live_smoke_run.py`, `backend/tests/test_live_smoke_run_script.py`, `package.json` |
| 2026-05-23 | RAG embedding ingest idempotency | live smoke runner와 자료 보강을 반복 실행해도 `document_chunks`가 중복되지 않도록 schema unique index와 upsert ingest로 변경 | `supabase/schema.sql`, `backend/app/scripts/ingest_documents.py`, `backend/tests/test_ingest_documents_script.py` |
| 2026-05-23 | RAG source intake template | 사용자가 PDF/사진/캡처/텍스트로 주는 교과과정, 트랙, 동아리, 학사 자료를 출처/category/핵심 필드 기준으로 접수하는 템플릿 추가 | `data/inbox/source-intake-template.md`, `data/inbox/README.md`, `docs/architecture/rag-data-intake.md` |
| 2026-05-23 | Runtime product mode gate | 프론트/백엔드 런타임에 예전 우회 인증이나 샘플 전용 fallback 표현이 재도입되지 않도록 `pnpm product:check` 추가 | `scripts/check_runtime_product_mode.py`, `package.json`, `docs/report/submission-checklist.md` |
| 2026-05-23 | Supabase schema check coverage | `schema.sql`에 정의된 모든 table을 `pnpm supabase:schema-check` readiness 대상에 포함해 partial schema 적용을 놓치지 않도록 보강 | `backend/app/scripts/supabase_schema_check.py`, `backend/tests/test_supabase_schema_sql_contract.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | RAG source product mode gate | raw/wiki/seed 자료의 샘플 전용 출처 표현을 제거하고 `pnpm rag:source-check`로 회귀를 막음 | `data/raw/`, `data/wiki/`, `supabase/seed.sql`, `scripts/check_rag_source_mode.py`, `package.json` |
| 2026-05-23 | Calendar live export gate | Google OAuth token이 없으면 Calendar export를 synthetic id로 성공 처리하지 않고 409 연결 필요 오류로 막음 | `backend/app/services/calendar_service.py`, `backend/app/api/assignments.py`, `backend/tests/services/test_calendar_service.py`, `backend/tests/api/test_assignments_api.py` |
| 2026-05-23 | Official KMU RAG source expansion | 공개 공식 페이지 기반으로 인공지능학부 개요, 소프트웨어학부 교육 구조, 동아리 활동, 교학팀 문의 경로 raw 문서를 추가 | `data/raw/kmu-ai-major-official.md`, `data/raw/kmu-sw-curriculum-official.md`, `data/raw/kmu-sw-clubs-official.md`, `data/raw/kmu-sw-office-contact-official.md` |
| 2026-05-23 | Supabase seed idempotency | 초기 확인용 `supabase/seed.sql`의 `document_chunks` insert를 `content_hash`와 unique conflict key 기준으로 중복 방지 | `supabase/seed.sql`, `backend/tests/test_supabase_seed_sql_contract.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase SQL Editor bundle | Dashboard SQL Editor에 붙여넣을 schema-only 또는 schema+seed bundle 생성 명령 추가 | `scripts/build_supabase_sql_bundle.py`, `tests/test_build_supabase_sql_bundle.py`, `package.json`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Live smoke schema blocker next actions | schema 미적용으로 live smoke가 멈출 때 SQL bundle 생성, SQL Editor 적용, 재실행 명령을 바로 출력 | `backend/app/scripts/live_smoke_run.py`, `backend/tests/test_live_smoke_run_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase SQL bundle validation gate | SQL Editor 적용 bundle에 필수 schema/seed marker가 포함되고 비밀값 marker가 섞이지 않도록 검증을 추가하고 `verify:local`에 포함 | `scripts/build_supabase_sql_bundle.py`, `tests/test_build_supabase_sql_bundle.py`, `package.json` |
| 2026-05-23 | Live readiness report | env, SQL bundle validation, live Supabase schema 상태와 next action을 비밀값 없이 한 번에 출력하는 `pnpm live:readiness` 추가 | `scripts/live_readiness_report.py`, `tests/test_live_readiness_report_script.py`, `package.json` |
| 2026-05-23 | Live smoke failure classification | schema 적용 뒤 개별 live smoke가 실패할 때 첫 실패를 `schema`/`auth`/`env`/`code`로 분류하고 다음 점검 명령을 출력 | `backend/app/scripts/live_smoke_run.py`, `backend/tests/test_live_smoke_run_script.py` |
| 2026-05-23 | RAG intake validation gate | 사용자 제공 PDF/사진/텍스트 전사 자료를 raw 변환하기 전에 출처/category/개인정보 위험을 검사하는 `pnpm rag:intake-check` 추가 | `scripts/check_rag_intake.py`, `tests/test_rag_intake_check_script.py`, `data/inbox/README.md` |
| 2026-05-23 | RAG intake prepare command hint | intake 검사를 통과한 파일에 대해 title/category/source/collected_at 기반 `pnpm rag:prepare-raw` 명령을 자동 출력 | `scripts/check_rag_intake.py`, `tests/test_rag_intake_check_script.py` |
| 2026-05-23 | RAG intake stub generator | 사용자가 PDF/사진/캡처/텍스트 파일을 주면 원본 파일명, 제목, category, 출처로 `data/inbox/*-intake.md` 접수 stub을 생성하는 `pnpm rag:intake-stub` 추가 | `scripts/create_rag_intake_stub.py`, `tests/test_create_rag_intake_stub_script.py`, `data/inbox/README.md` |
| 2026-05-23 | RAG intake placeholder gate | 접수 stub의 `확인 필요`, `TODO`, 기본 전사 안내문이 남아 있으면 `pnpm rag:intake-check`가 raw 변환을 막도록 보강 | `scripts/check_rag_intake.py`, `tests/test_rag_intake_check_script.py`, `docs/architecture/rag-data-intake.md` |
| 2026-05-23 | 앱 내 live runtime status | 로그인 후 설정 화면에서 Supabase backend, Supabase schema, Gemini, Google Calendar readiness를 비밀값 없이 표시. 일반 app data 로딩이 schema 503으로 실패해도 runtime status는 별도로 반영 | `backend/app/api/runtime.py`, `backend/app/services/runtime_status_service.py`, `frontend/src/App.tsx`, `backend/tests/api/test_runtime_status_api.py` |
| 2026-05-23 | 로그인 전 live readiness 표시 | 로그인 화면에서도 비인증 `/api/runtime/public-status`로 Supabase backend/schema/Gemini readiness를 보여줘 키와 schema blocker를 바로 확인 가능하게 보강 | `backend/app/api/runtime.py`, `frontend/src/App.tsx`, `frontend/src/lib/api.ts`, `backend/tests/api/test_runtime_status_api.py` |
| 2026-05-23 | Runtime schema blocker next action | Supabase schema blocker가 있을 때 runtime status API와 로그인/설정 화면에 SQL bundle 생성, SQL Editor 적용, live smoke 재실행 순서를 표시 | `backend/app/services/runtime_status_service.py`, `backend/app/schemas/runtime_status.py`, `frontend/src/App.tsx` |
| 2026-05-23 | Live app data failure recovery | Supabase Auth 로그인은 성공했지만 app data 로딩이 schema 503 등으로 실패할 때 무한 로딩 대신 live 상태, schema 다음 액션, 새로고침/로그아웃을 표시 | `frontend/src/App.tsx` |
| 2026-05-23 | Official KMU RAG source expansion 2 | 공식 페이지 기반으로 인공지능학부 2025 교과과정, 소프트웨어학부 트랙 선택 구조, 졸업요건 상담 기준, K-StarTrack 현장실습 자료를 추가하고 초기 raw 자료의 출처도 공식 확인 경로로 정리 | `data/raw/`, `data/wiki/` |
| 2026-05-23 | Runtime missing detail UI | 로그인/복구/설정 화면의 live status에서 Supabase schema missing table/function 전체와 Google Calendar missing env 이름을 비밀값 없이 펼쳐 표시 | `frontend/src/App.tsx` |
| 2026-05-23 | Live smoke API health preflight | schema 적용 뒤 login/API smoke 전에 `--api-base`의 `/health`를 먼저 확인하고 서버 미실행 시 8001 backend 실행 명령을 안내 | `backend/app/scripts/live_smoke_run.py`, `backend/tests/test_live_smoke_run_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Live readiness API health report | `pnpm live:readiness`가 schema 준비 뒤 `--api-base` `/health` 상태까지 보여주고 서버 미실행 시 backend 실행 명령을 다음 액션으로 안내 | `scripts/live_readiness_report.py`, `tests/test_live_readiness_report_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase schema cache reload marker | SQL Editor 적용 직후 PostgREST RPC/table schema cache 반영을 유도하도록 `notify pgrst, 'reload schema'`를 schema와 bundle validation gate에 추가 | `supabase/schema.sql`, `scripts/build_supabase_sql_bundle.py`, `backend/tests/test_supabase_schema_sql_contract.py`, `tests/test_build_supabase_sql_bundle.py` |
| 2026-05-23 | Live smoke schema retry | SQL Editor 적용 직후 PostgREST schema cache 반영 지연으로 table/RPC가 잠깐 missing일 때 `live:smoke-run`이 schema check를 짧게 재시도 | `backend/app/scripts/live_smoke_run.py`, `backend/tests/test_live_smoke_run_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase schema-check retry option | 적용 직후 `pnpm supabase:schema-check`도 기본 3회 retry를 수행하고 `--retries`, `--retry-delay`로 조정 가능하게 보강 | `backend/app/scripts/supabase_schema_check.py`, `backend/tests/test_supabase_schema_check_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase SQL Editor copy helper | Supabase CLI/psql 없이 Dashboard SQL Editor에 붙여넣을 schema+seed bundle을 검증 후 클립보드로 복사하고 다음 smoke 명령을 출력 | `scripts/copy_supabase_sql_bundle.py`, `tests/test_copy_supabase_sql_bundle.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Live onboarding memory | 첫 로그인 온보딩에서 관심 분야, 목표, 코딩 경험, 학습 선호, 활동 방식을 받아 기존 `user_memories`에 active memory로 저장하고 첫 채팅/추천 입력에 연결 | `backend/app/api/memories.py`, `backend/app/schemas/memory.py`, `backend/tests/api/test_memory_api.py`, `frontend/src/App.tsx`, `frontend/src/lib/api.ts` |
| 2026-05-23 | Login smoke onboarding memory | Supabase login/API smoke가 profile write/read뿐 아니라 onboarding memory 생성까지 검증하도록 확장 | `backend/app/scripts/auth_api_smoke.py`, `backend/app/scripts/supabase_login_smoke.py`, `backend/tests/test_auth_api_smoke_script.py`, `backend/tests/test_supabase_login_smoke_script.py` |
| 2026-05-23 | Login smoke API contract preflight | 오래된 FastAPI 서버가 같은 port에 떠 있을 때 auth/schema 문제처럼 보이지 않도록 `/api/runtime/public-status` contract를 먼저 확인 | `backend/app/scripts/auth_api_smoke.py`, `backend/tests/test_auth_api_smoke_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Active docs live language gate | 제출/제품/아키텍처/기여 활성 문서가 샘플 중심 표현이 아니라 실제 live 로그인, 온보딩, 채팅 흐름을 기준으로 설명되도록 검사 추가 | `scripts/check_live_language.py`, `tests/test_live_language_script.py`, `package.json`, `docs/product/prd-dev-plan.md`, `docs/report/submission-checklist.md` |
| 2026-05-23 | Live readiness API contract preflight | schema 적용 전에도 `live:readiness`가 `/api/runtime/public-status`를 확인해 Supabase schema blocker와 stale backend blocker를 분리 | `scripts/live_readiness_report.py`, `tests/test_live_readiness_report_script.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | SQL copy api-base hint | `supabase:sql-copy`가 현재 backend port에 맞는 `live:smoke-run --api-base`를 출력하도록 `--api-base` 옵션 추가 | `scripts/copy_supabase_sql_bundle.py`, `tests/test_copy_supabase_sql_bundle.py`, `docs/contributing/supabase-live-apply.md` |
| 2026-05-23 | Supabase Dashboard access blocker | Chrome 로그인 계정이 `abbwnqwvvtxrizutswws` 프로젝트에 접근 권한이 없어 SQL Editor 적용을 project owner/member 계정 작업으로 분리 | `docs/contributing/supabase-live-apply.md`, `docs/report/submission-checklist.md` |
| 2026-05-23 | Supabase live smoke passed | schema+seed 적용 뒤 Supabase DB/LLM/login, Gemini, grounding, embedding ingest live smoke 전체 통과. Google Calendar OAuth는 제출 필수가 아니라 선택 확장으로 분리 | `pnpm supabase:schema-check`, `pnpm live:readiness -- --include-seed --api-base http://127.0.0.1:8001`, `pnpm live:smoke-run --api-base http://127.0.0.1:8001`, `docs/report/submission-checklist.md` |
| 2026-05-24 | 제출 범위 재정리 | Google Calendar OAuth live 연동은 제외하고, 내부 일정 관리와 D-day를 제출 시연의 일정 기능으로 확정 | `docs/product/live-scenario.md`, `docs/report/submission-checklist.md`, `docs/contributing/roadmap.md` |
| 2026-05-25 | Chat UX service polish | 최근 상담 삭제, intent 기반 자동 제목, 새 상담 empty state, 사용자 메시지 우측 정렬, 답변 완료 상태, 중복 제거된 번호형 근거 표시, SSE 종료 버퍼 처리 보강 | `frontend/src/App.tsx`, `frontend/src/components/navigation.tsx`, `frontend/src/lib/api.ts`, `backend/app/api/chat.py`, `backend/app/services/chat_store.py`, `backend/app/services/supabase_stores.py` |
| 2026-05-25 | Chat hardcoded follow-up 제거 | 상담 답변 아래의 `학업 상담`/`진로 상담`/`일정 관리` 고정 후속 칩과 입력창 하단 고정 칩을 제거해 Gemini/RAG 답변과 근거만 표시하도록 정리 | `backend/app/services/chat_contract_service.py`, `frontend/src/App.tsx`, `backend/tests/api/test_chat_contract_api.py` |
| 2026-05-25 | Chat composer controls | 하단 composer에 상담 모드, 응답 품질 선택, 파일 첨부, 답변 중지 버튼을 추가하고 Gemini `generate_content_stream` 기반 실제 SSE 스트리밍으로 변경 | `frontend/src/App.tsx`, `frontend/src/lib/api.ts`, `frontend/src/types/api.ts`, `backend/app/schemas/chat.py`, `backend/app/api/chat.py`, `backend/app/services/answer_generation_service.py` |
| 2026-05-26 | Chat stream cutoff recovery | Gemini 스트리밍 답변이 `MAX_TOKENS` 등으로 중간 종료될 때 최종 `done` 응답과 저장본을 재생성된 완성 답변으로 교체 | `backend/app/services/answer_generation_service.py`, `backend/app/api/chat.py`, `backend/tests/api/test_chat_contract_api.py` |
| 2026-05-26 | Chat stream output budget fix | Gemini 채팅 출력 제한을 768에서 4096 토큰으로 올리고, 빈 종료 chunk의 `finishReason`도 보존해 스트리밍 답변이 정상 완료처럼 잘려 확정되는 문제를 줄임 | `backend/app/services/answer_generation_service.py`, `backend/app/api/chat.py`, `backend/tests/services/test_answer_generation_service.py`, `backend/tests/api/test_chat_contract_api.py` |
| 2026-05-26 | Recommendation input default removal | 진로/활동 추천 화면에서 `AI/백엔드/AI 서비스 개발` 같은 기본값을 제거하고, 정보가 부족하면 AI 상담에서 관심사와 목표를 먼저 정리하도록 유도 | `frontend/src/lib/navigator.ts`, `frontend/src/App.tsx`, `frontend/src/types/navigator.ts` |
| 2026-05-26 | Chat navigation cleanup | 사이드바 최근 상담과 중복되는 `상담 기록` 페이지 진입점을 제거하고 앱 root/grid overflow를 고정해 브라우저 문서 스크롤이 생기지 않도록 정리 | `frontend/src/App.tsx`, `frontend/src/components/navigation.tsx`, `frontend/src/styles.css`, `frontend/src/types/navigator.ts` |
| 2026-05-26 | Advisor-first recommendation UX | `진로/취업` 탭을 `내 추천`으로 낮추고, 사용자가 폼을 먼저 채우는 대신 AI 상담의 진로 페르소나가 부족한 정보를 물어본 뒤 추천 현황을 보여주도록 전환 | `frontend/src/App.tsx`, `frontend/src/components/navigation.tsx`, `frontend/src/components/TopBar.tsx`, `frontend/src/lib/navigator.ts` |
| 2026-05-26 | Conversation learning memory extraction | AI 상담 문장에서 관심 트랙, 목표, 코딩 경험, 학습 선호, 주간 가능 시간을 Python 규칙으로 추출해 `conversation / learning_context` 메모리로 자동 저장 | `backend/app/services/memory_service.py`, `backend/app/api/chat.py`, `backend/tests/api/test_chat_contract_api.py`, `frontend/src/App.tsx`, `docs/architecture/python-core-logic.md` |
| 2026-05-26 | Settings modal management | 설정을 별도 페이지에서 모달로 전환하고 계정, 내 정보, 메모리 보관, AI 상담 모드/모델 설정을 한곳에서 관리하도록 정리 | `frontend/src/App.tsx` |
| 2026-05-26 | Interactive context panel | 우측 참고 패널의 내 정보, 답변 근거, 다음 행동을 클릭 가능한 상담 진입점으로 바꿔 설정 수정과 후속 질문 입력을 바로 이어갈 수 있게 정리 | `frontend/src/App.tsx` |
| 2026-05-26 | Resizable workspace side panels | 데스크톱에서 왼쪽 내비게이션과 오른쪽 참고 패널을 접거나 경계선 드래그로 폭을 조절할 수 있게 정리 | `frontend/src/App.tsx`, `frontend/src/components/navigation.tsx` |
| 2026-05-26 | Recommendation board and calendar workspace | `내 추천`을 `추천 보드`로 바꾸고 상담 기반 추천 현황/로드맵을 보여주며, 일정 화면을 월간 캘린더와 다가오는 일정 보드 중심으로 재구성 | `frontend/src/App.tsx`, `frontend/src/components/navigation.tsx`, `frontend/src/lib/navigator.ts` |
| 2026-05-27 | RAG quality evaluation gate | 제출 시연 질문의 내부 근거 후보를 로컬 raw/wiki 자료로 자동 점검하는 `pnpm rag:evaluate` 추가. AI/트랙, 수강신청, 개발/활동, 교학팀 문의, 범위 밖 질문 5개 평가 통과 | `backend/app/scripts/rag_quality_eval.py`, `backend/tests/test_rag_quality_eval_script.py`, `docs/testing/rag-evaluation.md` |
| 2026-05-25 | RAG 과목/수강신청 데이터 수집 기준 | 공식 과목/제도 데이터와 비공식 수강신청 팁/과목 후기를 분리해 수집하는 템플릿과 팀원 요청 항목을 문서화 | `docs/architecture/rag-course-data-collection.md`, `docs/product/team-data-request.md` |

## 팀원 공유용 개발 현황

처음에는 국민대 소프트웨어융합대학 신입생을 위한 정보 탐색 도우미로 시작했고, 이후 범위를 전체 학년을 지원하는 개인화 RAG 학업 내비게이터로 확장했다.

지금까지 구현한 핵심 흐름은 다음과 같다.

1. 문서/과제 기반: PRD, 로드맵, 기능 레지스트리, LLM 사용 기록, 제출 체크리스트를 만들었다.
2. 데이터 기반: Supabase schema에 profile, memory, chat, assignment, document chunk, LLM log 테이블과 RAG 검색 RPC를 준비했다.
3. RAG 기반: 국민대/학부 공식 자료를 `data/raw`와 Mini LLM Wiki로 정리하고, Gemini embedding과 Supabase pgvector 검색으로 연결했다.
4. 백엔드: FastAPI에서 로그인 사용자 기준 profile, memory, chat, recommendation, assignment, LLM log API를 구현했다.
5. 프론트엔드: Supabase 로그인, 온보딩, AI 상담, 진로/활동 추천, 일정 관리, 설정/live status 화면을 구현했다.
6. 개인화: 온보딩에서 관심 분야, 목표, 코딩 경험, 학습 선호를 받아 `user_memories`에 저장하고 채팅/추천 입력에 반영한다.
7. 일정 관리: 자연어로 과제/시험 일정을 입력하면 제목, 과목, 마감일을 추출하고 Supabase에 저장하며, 앱 내부에서 D-day, 완료, 삭제를 제공한다.
8. LLM 기록: 채팅 답변, Google grounding, 일정 parser, embedding ingest 같은 앱 내부 LLM 사용을 로그로 남기고, 개발 과정의 Codex/Gemini 활용도 문서화했다.
9. 검증: `pnpm verify:local` 기준 문서 검사, RAG dry-run, RAG quality evaluation, 제출 조건 검사, backend 194 tests, root 42 tests, lint, frontend build가 통과한다.

현재 제출 시연의 중심은 Supabase 로그인, 온보딩, 개인화 RAG 채팅, 추천, 내부 일정 관리, LLM 활용 기록이다. Google Calendar OAuth는 구현 기반은 있지만 외부 OAuth 설정 부담이 커서 이번 제출에서는 선택 확장 기능으로만 설명한다.

## 다음 작업 후보

1. 앱에서 실제 로그인, 온보딩, 채팅, 추천, 일정 저장, 완료/삭제, LLM 로그 조회를 화면 기준으로 리허설하고 캡처
2. 보고서/발표자료에 위 구현 범위와 검증 결과를 반영
3. 시간이 남으면 Google Calendar OAuth는 선택 확장 기능으로만 추가 검증

## 상태 기록 규칙

- 기능을 시작하면 이 문서에 한 줄을 추가합니다.
- 기능을 끝내면 검증 명령과 결과를 관련 plan 문서에 남깁니다.
- 실제 코드와 테스트 결과가 문서보다 우선합니다.
