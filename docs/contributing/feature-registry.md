# 기능 레지스트리

이 문서는 중복 작업을 막기 위한 기능 소유 영역입니다. 새 작업을 시작하기 전에 관련 feature id를 확인합니다.

상태:

- `planned`: 설계됨
- `active`: 구현 중
- `complete`: 1차 구현 완료
- `blocked`: 결정 필요
- `retired`: 산출물은 보관하지 않고 설계/기록만 유지

| Feature ID | 상태 | 소유 경로 | 설명 | 중복 방지 |
| --- | --- | --- | --- | --- |
| repo-docs-foundation | active | `README.md`, `AGENTS.md`, `docs/` | 문서 인덱스, 개발 가이드, LLM 활용 기록 구조 | 문서 구조 변경 전 `docs/README.md`를 먼저 수정 |
| backend-api-foundation | active | `backend/app/` | FastAPI 앱, `/api` 라우터, Supabase Bearer 인증 dependency, Auth API/JWT token 검증, 저장소 protocol | API 계약 변경은 schema/test/docs를 함께 갱신 |
| supabase-schema | active | `supabase/schema.sql`, `backend/app/services/supabase_stores.py`, `backend/app/scripts/check_env.py` | profiles, document_chunks, assignments, chat/memory/log/calendar token schema, profile/memory persistence adapter, env check, schema readiness probe | schema 변경은 SQL 파일과 docs를 함께 갱신하고 live DB smoke를 별도 기록 |
| mini-llm-wiki | active | `data/raw/`, `data/wiki/`, `backend/app/services/wiki_compiler.py`, `backend/app/services/markdown_chunker.py` | 원문 자료를 wiki page로 컴파일하고 RAG 우선 검색 계층으로 사용 | LangGraph/worker 없이 Python script 중심으로 유지 |
| rag-ingest | active | `backend/app/services/document_ingest.py`, `backend/app/services/embedding_service.py`, `backend/app/scripts/ingest_documents.py`, `backend/app/scripts/gemini_smoke.py`, `data/` | raw/wiki Markdown chunk payload 생성, Gemini embedding adapter, dry-run, Supabase insert script, Gemini smoke | live embedding ingest는 `GEMINI_API_KEY`와 Supabase env 설정 후 실행 |
| rag-chat | active | `backend/app/api/chat.py`, `backend/app/services/chat_contract_service.py`, `backend/app/services/retrieval_service.py`, `backend/app/services/answer_generation_service.py`, `backend/app/services/chat_store.py`, `backend/app/scripts/gemini_answer_smoke.py`, `frontend/src/` | 질문 답변 contract, local fallback retrieval, Supabase text/vector RPC retrieval evidence, Gemini answer generation, Google grounding, chat session/message 저장, recent chats 조회, 출처 표시 | live Gemini/Supabase/grounding smoke는 키 설정 후 실행 |
| frontend-ui-mockups | retired | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 로그인/메인 화면의 정적 HTML 목업 기록 | 실제 UI는 개인화 SW 내비게이터 React 구현으로 대체 |
| chatbot-evidence-visualization | retired | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 챗봇 답변 옆 출처, 로드맵, 추천 이유 시각화 목업 기록 | 근거 표시 UX는 `personalized-sw-navigator-design`에 통합 |
| personalized-sw-navigator-design | complete | `docs/superpowers/specs/2026-05-13-personalized-sw-navigator-design.md`, `docs/superpowers/plans/2026-05-13-personalized-sw-navigator-foundation.md` | 신입생 전용에서 전체 학년 개인화 SW 내비게이터로 제품 범위 확장 | 레포 이름 변경은 별도 작업으로 미루고 문서/구현 범위만 먼저 정렬 |
| user-profile-memory | complete | `backend/app/api/`, `backend/app/services/`, `backend/app/schemas/`, `supabase/schema.sql`, `frontend/src/` | 필수 프로필, 메모리 민감도 정책, memory_events, 메모리 조회/수정/삭제, chat contract 1차 구현, Supabase persistence adapter | 환경 변수가 없으면 in-memory fallback을 쓰며 live Supabase smoke는 별도 검증 필요 |
| grounded-career-advisor | active | `backend/app/services/answer_generation_service.py`, `backend/app/services/chat_contract_service.py`, `backend/app/api/chat.py`, `backend/app/scripts/gemini_grounding_smoke.py`, `frontend/src/` | 최신 진로/취업/창업 정보에 Google Search grounding 적용, live grounding smoke | 학교 내부 RAG와 웹 grounding 근거를 분리 표시 |
| google-calendar-export | active | `backend/app/api/assignments.py`, `backend/app/api/integrations.py`, `backend/app/services/calendar_service.py`, `backend/app/services/google_calendar_oauth_service.py`, `backend/app/services/google_oauth_token_service.py`, `backend/app/scripts/calendar_export_smoke.py`, `backend/app/services/supabase_stores.py`, `supabase/schema.sql`, `frontend/src/` | 저장된 과제/일정을 Google Calendar event payload로 변환하고 export 상태 저장, OAuth status/connect/callback/refresh와 server-only token 저장, token 존재 시 `events.insert` 호출, live export smoke | live smoke는 실제 Supabase/Google env 설정 후 실행 |
| navigator-home-ui | complete | `frontend/src/`, `frontend/vite.config.ts` | Claude/NotebookLM식 3-column workspace shell, sidebar navigation, mobile navigation/context drawers, chat workspace, context panel 1차 구현, assistant markdown 렌더링, 주요 액션 toast | landing/dashboard 대신 상담 workspace를 첫 화면으로 유지 |
| frontend-auth-session | complete | `frontend/src/lib/supabase.ts`, `frontend/src/lib/api.ts`, `frontend/src/App.tsx`, `backend/app/scripts/auth_api_smoke.py`, `backend/app/scripts/supabase_login_smoke.py` | Supabase browser client, 로그인/가입/로그아웃/온보딩 gate, API Bearer token forwarding, access token/API/login smoke | 로그인 세션 없이는 앱과 API를 사용하지 않으며, live auth smoke는 키와 실제 계정 설정 후 실행 |
| recommend-track-club | active | `backend/app/api/recommendations.py`, `backend/app/services/recommendation_service.py`, `backend/app/schemas/recommendation.py`, `frontend/src/` | 조건문/딕셔너리 기반 트랙/동아리/활동 추천 API, RAG 내부 출처 근거, 프로필/메모리 기반 추천 입력, 직접 입력 편집 UI, 진로/취업 화면 결과 표시 | 추천 scoring 변경은 Python 서비스 테스트와 plan 문서를 함께 갱신 |
| schedule-dday | active | `backend/app/api/assignments.py`, `backend/app/services/assignment_service.py`, `backend/app/services/supabase_stores.py`, `frontend/src/` | 자연어 일정 preview, Gemini parser fallback, Supabase/in-memory 저장, D-day 계산, 일정 탭 UI, 완료/삭제, Calendar export 버튼 | live Gemini parsing smoke는 키 설정 후 실행 |
| llm-usage-log | active | `docs/llm/`, `backend/app/api/llm_logs.py`, `backend/app/services/llm_usage_log_service.py`, `backend/app/scripts/llm_usage_smoke.py`, `frontend/src/` | 개발 과정 기록, 앱 내부 LLM 사용 로그 API, LLM 기록 화면, Supabase insert/list smoke, 에이전트 기반 코딩 활용 증거 | Codex/Gemini Code Assist 같은 개발 보조 에이전트와 Gemini API 앱 기능 사용을 구분하고 자동 기록 범위를 문서화 |
| report-presentation | planned | `docs/report/` | 보고서, 발표자료, 데모 시나리오 | 실행 결과 캡처와 검증 명령을 함께 기록 |
