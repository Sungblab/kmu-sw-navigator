# 제출 전 체크리스트

이 문서는 제출 직전에 “구현했다고 말할 수 있는 것”, “실제 SaaS 연결로 검증한 것”, “외부 키가 있어야 추가 검증할 것”을 분리해서 확인하기 위한 체크리스트다. 체크는 추측이 아니라 파일, 명령, 테스트 결과를 근거로 한다.

최종 설명 기준은 로컬 fallback 가능 여부가 아니라 **Python FastAPI 백엔드, Supabase Auth/Postgres, React 프론트가 연결된 개인화 학업 SaaS**다. fallback은 발표 장애 대응용 보조 경로로만 설명한다.

## 1. 과제 조건 체크

| 조건 | 근거 파일/화면 | 확인 명령 또는 설명 | 상태 |
| --- | --- | --- | --- |
| 사용자 입력 | `frontend/src/App.tsx`, `backend/app/api/chat.py`, `backend/app/api/assignments.py`, `backend/app/api/recommendations.py` | 채팅 질문, 추천 입력, 자연어 일정 입력, 프로필/로그인 입력을 받음 | 준비됨 |
| 조건문 | `backend/app/services/memory_service.py`, `backend/app/services/chat_contract_service.py`, `backend/app/services/recommendation_service.py`, `backend/app/services/assignment_service.py` | 민감도, intent, 추천 점수, 일정 parser fallback에서 분기 | 준비됨 |
| 반복문 | `backend/app/services/retrieval_service.py`, `backend/app/services/recommendation_service.py`, `backend/app/services/document_ingest.py` | 문서 chunk, 추천 후보, 검색 결과 순회 | 준비됨 |
| 함수 | `build_chat_response`, `recommend_tracks`, `recommend_activities`, `preview_assignment`, `build_calendar_event` | 기능별 함수로 분리되어 테스트 가능 | 준비됨 |
| 리스트/딕셔너리 | `TRACK_RULES`, `ACTIVITY_RULES`, evidence payload, assignment list, memory `value_json` | 구조화 데이터로 추천/근거/일정 출력 구성 | 준비됨 |
| 의미 있는 출력 | chat response, recommendation response, assignment preview/list, calendar export response | 입력에 따라 답변, 추천, D-day, 근거가 달라짐 | 준비됨 |
| 실행 가능한 Python 코드 | `backend/app/`, `backend/tests/` | `pnpm test:backend`, `pnpm lint:backend` | 준비됨 |
| LLM 활용 기록 | `docs/llm/usage-log.md`, `GET /api/llm-logs` | 개발 보조 기록과 앱 내부 채팅/grounding/일정 parser/embedding ingest 로그를 기록 | 준비됨 |
| LLM 생성 코드 그대로 사용 금지 | `AGENTS.md`, `docs/architecture/python-core-logic.md`, `docs/llm/agent-coding-evidence.md`, `docs/llm/usage-log.md` | 직접 검토/수정/테스트한 기록과 설명 가능한 Python 로직 문서를 함께 제출 | 준비됨 |

## 2. 라이브 시연 체크

| 시연 항목 | 보여줄 화면/파일 | 상태 |
| --- | --- | --- |
| 메인 workspace UI | `frontend/src/App.tsx` | 준비됨 |
| Supabase 로그인 UI | 첫 화면 로그인/가입, 온보딩 gate | 실제 session 없으면 앱과 API 사용 불가 |
| 개인화 RAG 상담 | AI 상담 화면, 오른쪽 context panel | 준비됨 |
| 내부 자료 근거 | `evidence.internal_sources` chip | 준비됨 |
| 최신 웹 grounding 근거 | `evidence.web_sources` chip | live Gemini key 필요 |
| 진로/활동 추천 | 진로/취업 화면 직접 입력 UI | 준비됨 |
| 자연어 일정 preview/save | 일정 화면 | 준비됨 |
| D-day/완료/삭제 | 일정 목록 | 준비됨 |
| Google Calendar export | 일정 목록 export 버튼 | OAuth token 없으면 409 연결 필요 오류, token 있으면 Google `events.insert` live insert |
| LLM 활용 기록 설명 | `docs/llm/usage-log.md`, LLM 기록 화면 | 준비됨 |
| SaaS 저장 구조 | Supabase Auth/Postgres, `backend/app/services/supabase_stores.py` | 사용자별 profile/memory/chat/assignment/llm log 저장. 현재 live DB smoke는 schema/user blocker 해소 후 실행 |
| 홈서버 운영 계획 | `docs/contributing/dev-guide.md`, 발표 한계/개선 설명 | Docker Compose 후속 배포 계획, 발표 주 경로는 SaaS 구조와 local/live smoke 증거 |

## 3. 검증 명령

키 없이 바로 실행할 수 있는 기본 검증:

```powershell
pnpm verify:local
```

`verify:local`은 아래 개별 명령을 순서대로 실행하는 제출 전 기본 검증 묶음이다.

```powershell
pnpm docs:check
pnpm product:check
pnpm supabase:sql-bundle
pnpm rag:intake-check
pnpm wiki:build
pnpm rag:source-check
pnpm rag:ingest:dry
pnpm submission:check
python -m pytest tests
pnpm test:backend
pnpm lint:backend
pnpm build:frontend
```

최근 확인 결과:

- `pnpm env:check`: Backend Supabase Direct, Backend Supabase Auth Verification, Frontend Supabase Framework, Gemini는 ready. Google OAuth 값은 missing
- `pnpm live:smoke-plan`: Supabase env strict, schema check command, smoke user create, DB/login/API/LLM smoke, Gemini smoke는 ready. Google Calendar smoke는 OAuth/token blocker를 표시
- `pnpm env:check:strict`: 통과
- `pnpm supabase:create-smoke-user --write-root-env`: Supabase Auth 테스트 유저 생성 성공, password는 출력하지 않고 gitignored root `.env`에 저장
- `pnpm supabase:schema-check`: `profiles`, `raw_documents`, `wiki_pages`, `wiki_logs`, `document_chunks`, `assignments`, `chat_sessions`, `chat_messages`, `chat_logs`, `llm_usage_logs`, `user_memories`, `memory_events`, `google_oauth_tokens`, `search_document_chunks_text`, `match_document_chunks` 모두 missing
- `pnpm supabase:smoke`: schema 미적용으로 실패. 원인: `profiles` table 없음
- `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001`: Supabase login 후 FastAPI profile write에서 503 `supabase_schema_missing`
- `pnpm supabase:llm-smoke`: schema 미적용으로 실패. 원인: `llm_usage_logs` table 없음
- Supabase CLI: 현재 로컬에 설치되어 있지 않아 schema 적용은 Dashboard SQL Editor에서 수행 필요
- Schema contract check: `search_document_chunks_text(search_query, match_count, filter_source_type)` 인자명이 backend adapter와 schema check에 맞게 정렬됨
- `pnpm gemini:smoke`: 실제 Gemini API로 embedding 768차원과 일정 parser 호출 통과
- `pnpm gemini:answer-smoke`: 실제 Gemini 답변 생성 통과
- `pnpm gemini:grounding-smoke`: 실제 Gemini Google Search grounding 통과
- Browser smoke: `http://127.0.0.1:5173`에서 로그인 세션 없을 때 로그인 화면으로 gate 확인, Gemini key 설정 뒤 채팅 응답이 live Gemini 문구로 렌더링되는 것 확인
- Python 핵심 로직 주석 점검: `recommendation_service.py`, `retrieval_service.py`, `assignment_service.py`, `memory_service.py`, `chat_contract_service.py`의 판단 기준 주석은 충분해 코드 주석 변경은 하지 않음
- `pnpm verify:local`: docs/product/Supabase SQL bundle/wiki/RAG source/RAG dry-run/submission check/root test/backend test/backend lint/frontend build 전체 통과
- `pnpm docs:check`: 필수 문서 20개 확인 완료
- `pnpm product:check`: `frontend/src`, `backend/app` 런타임에 `demo-user`, `X-User-Id`, `mock`, `목업`, `데모` fallback 표현이 남아 있지 않음
- `pnpm supabase:sql-bundle`: SQL Editor 적용용 `supabase/live-schema-bundle.sql` 생성 전 필수 schema marker와 비밀값 marker 검증 후 생성 완료. 생성 파일은 gitignored
- `pnpm rag:intake-check`: `data/inbox`의 사용자 제공 자료가 출처/category/개인정보 위험 검사를 통과해야 raw/wiki 변환으로 진행
- `pnpm rag:intake-stub`: PDF/사진/캡처/텍스트 원본을 받으면 `data/inbox/*-intake.md` 접수 stub을 생성해 출처/category/전사 상태를 먼저 기록
- `pnpm live:readiness -- --include-seed --api-base http://127.0.0.1:8001`: env, SQL bundle, Supabase schema 상태를 비밀값 없이 한 번에 요약. 현재 live blocker는 schema 미적용
- `pnpm live:smoke-run --api-base http://127.0.0.1:8001`: schema 적용 뒤 개별 smoke 실패 시 `schema`/`auth`/`env`/`code` 분류와 다음 액션 출력
- 앱 설정 화면 live runtime status: 로그인 후 Supabase backend, Supabase schema, Gemini, Google Calendar readiness를 비밀값 없이 표시. 일반 app data 로딩이 schema 503으로 실패해도 runtime status는 별도로 반영되며, Supabase schema는 SQL 적용 전 `schema_sql_not_applied` blocker로 분리됨
- 로그인 화면 live readiness: 로그인 전에도 비인증 runtime status로 Supabase backend/schema/Gemini readiness를 확인할 수 있어, Gemini key ready와 Supabase schema blocker를 같은 화면에서 구분 가능
- Supabase schema blocker가 표시되면 앱 안에서도 `pnpm supabase:sql-bundle -- --include-seed`, SQL Editor 적용, `pnpm live:smoke-run --api-base http://127.0.0.1:8001` 순서를 확인 가능
- `pnpm wiki:build`: raw_documents=8, wiki_pages=6 생성 완료
- `pnpm rag:source-check`: `data/raw`, `data/wiki`, `supabase/seed.sql`에 demo/mock 출처 표현 없음
- `pnpm rag:ingest:dry`: documents=14, chunks=80, wiki_chunks=50, raw_chunks=30 준비 완료
- `pnpm test:backend`: 166 passed
- `python -m pytest tests`: 30 passed
- `pnpm lint:backend`: All checks passed
- `pnpm build:frontend`: Vite production build 통과
- `pnpm submission:check`: 제출 조건 증거 9개 확인 완료
- `pnpm submission:check`: 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력, 실행 가능한 Python, LLM 활용 기록, LLM 생성 코드 그대로 사용 금지 증거 확인
- `git diff --check`: exit 0, 생성된 wiki와 기존 문서의 CRLF 경고만 있음
- Playwright smoke: `http://127.0.0.1:5173` 렌더 확인, CORS/favicon console error 없음
- 2026-05-23 live auth gate smoke: 프론트는 로그인 세션 없으면 API를 호출하지 않고 로그인 화면에서 멈춘다. 백엔드는 `Authorization: Bearer` Supabase token만 허용하며 `X-User-Id` 런타임 fallback은 제거했다.

실제 Supabase/Gemini/Google 키가 있을 때 추가로 실행할 검증:

```powershell
pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>
pnpm env:check:strict
pnpm live:readiness -- --include-seed --api-base http://127.0.0.1:8001
pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>
pnpm supabase:auth-smoke -- --access-token <supabase-access-token>
pnpm supabase:login-smoke -- --email <email> --password <password>
pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>
pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>
pnpm gemini:smoke
pnpm gemini:answer-smoke
pnpm gemini:grounding-smoke
pnpm rag:ingest
pnpm rag:ingest:embeddings
```

Google Calendar OAuth와 Gemini grounding은 UI/API 경로에서 live smoke를 별도로 기록한다.

## 4. 제출 문서 체크

| 문서 | 목적 | 상태 |
| --- | --- | --- |
| `README.md` | 실행 방법, 구현 상태, 제출 자료 링크 | 준비됨 |
| `docs/product/demo-scenario.md` | 20-25분 라이브 시연 흐름 | 준비됨 |
| `docs/report/report-outline.md` | 6-10페이지 보고서 구성 | 준비됨 |
| `docs/report/presentation-outline.md` | 발표자료 구성과 시간 배분 | 준비됨 |
| `docs/architecture/python-core-logic.md` | 발표에서 설명할 Python 핵심 로직 | 준비됨 |
| `docs/llm/agent-coding-evidence.md` | 에이전트 기반 코딩 활용 증거 | 준비됨 |
| `docs/llm/usage-log.md` | LLM 사용 목적과 직접 검토/수정/검증 기록 | 준비됨 |
| `docs/contributing/plans-status.md` | 구현 상태와 다음 작업 | 준비됨 |
| `docs/contributing/feature-registry.md` | 기능 소유 영역과 중복 방지 | 준비됨 |

## 4.1 RAG 공식 출처 보강

현재 RAG raw 문서는 팀 정리 초안 4개와 공식 공개 페이지 기반 문서 4개로 구성한다. 공식 출처 기반 문서는 인공지능학부 전공 개요, 소프트웨어학부 교육 구조, 소프트웨어융합대학 동아리 활동, 교학팀 문의 경로를 다룬다. 이 자료는 원문 전체 복사가 아니라 출처 URL과 상담용 판단 기준 중심으로 요약해 `data/raw`에 저장한다.

## 5. 제출 전 남은 일

1. `docs/contributing/supabase-live-apply.md` 순서대로 Supabase Dashboard SQL Editor에서 `supabase/schema.sql`을 적용하고 결과를 기록. 현재 schema check는 `schema.sql`의 table/function 전체 missing이므로 `profiles`, `raw_documents`, `wiki_pages`, `wiki_logs`, `document_chunks`, `assignments`, `chat_sessions`, `chat_messages`, `chat_logs`, `llm_usage_logs`, `user_memories`, `memory_events`, `google_oauth_tokens`, `search_document_chunks_text`, `match_document_chunks`가 필요하다.
2. Supabase Auth 테스트 유저의 UUID/email/password는 root `.env`에 준비됨. repo에 커밋하지 않고 `SUPABASE_SMOKE_USER_ID`, `SUPABASE_SMOKE_EMAIL`, `SUPABASE_SMOKE_PASSWORD` 또는 CLI 인자로만 사용.
3. `frontend/.env`의 Supabase Framework 값으로 실제 가입/로그인 세션 생성 확인.
4. `SUPABASE_JWT_SECRET`을 확보하면 백엔드 로컬 JWT 검증 경로도 추가 확인. 값이 없으면 현재처럼 Supabase Auth API 검증 경로를 사용.
5. `pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>`로 누락값 확인.
6. `pnpm env:check:strict`, `pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm supabase:login-smoke -- --email <email> --password <password>`, `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>` 실행.
7. Gemini key로 `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke`, `pnpm rag:ingest:embeddings` 실행.
8. 앱에서 로그인, 질문, 추천, 일정, Calendar export를 한 번씩 녹화.
9. 발표에서 `AGENTS.md`, `docs/llm/agent-coding-evidence.md`, `docs/llm/usage-log.md`를 열어 에이전트 활용 과정을 설명.
10. 보고서에 실제 스크린샷과 검증 명령 결과를 붙임.
11. 발표영상 녹화 전 `docs/product/demo-scenario.md` 순서대로 라이브 시연 리허설.
12. 홈서버 배포를 보여줄 경우 Docker Compose 배포 URL은 보조 시연으로만 쓰고, 노트북 로컬 실행과 녹화 백업을 함께 준비.
