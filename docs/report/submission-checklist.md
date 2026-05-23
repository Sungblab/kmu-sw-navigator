# 제출 전 체크리스트

이 문서는 제출 직전에 “구현했다고 말할 수 있는 것”과 “키가 있어야 추가 검증할 것”을 분리해서 확인하기 위한 체크리스트다. 체크는 추측이 아니라 파일, 명령, 테스트 결과를 근거로 한다.

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

## 2. 데모 체크

| 데모 항목 | 보여줄 화면/파일 | 상태 |
| --- | --- | --- |
| 메인 workspace UI | `frontend/src/App.tsx` | 준비됨 |
| Supabase 로그인 UI | 설정 화면 | env 없으면 demo fallback, env 있으면 실제 session |
| 개인화 RAG 상담 | AI 상담 화면, 오른쪽 context panel | 준비됨 |
| 내부 자료 근거 | `evidence.internal_sources` chip | 준비됨 |
| 최신 웹 grounding 근거 | `evidence.web_sources` chip | live Gemini key 필요 |
| 진로/활동 추천 | 진로/취업 화면 직접 입력 UI | 준비됨 |
| 자연어 일정 preview/save | 일정 화면 | 준비됨 |
| D-day/완료/삭제 | 일정 목록 | 준비됨 |
| Google Calendar export | 일정 목록 export 버튼 | token 없으면 synthetic id fallback, live insert는 OAuth env 필요 |
| LLM 활용 기록 설명 | `docs/llm/usage-log.md`, LLM 기록 화면 | 준비됨 |
| 홈서버 운영 계획 | `docs/contributing/dev-guide.md`, 발표 한계/개선 설명 | Docker Compose 후속 배포 계획, 발표 주 경로는 로컬 실행 |

## 3. 검증 명령

키 없이 바로 실행할 수 있는 기본 검증:

```powershell
pnpm verify:local
```

`verify:local`은 아래 개별 명령을 순서대로 실행하는 제출 전 기본 검증 묶음이다.

```powershell
pnpm docs:check
pnpm wiki:build
pnpm rag:ingest:dry
pnpm submission:check
python -m pytest tests
pnpm test:backend
pnpm lint:backend
pnpm build:frontend
```

최근 확인 결과:

- `pnpm verify:local`: docs/wiki/RAG dry-run/submission check/root test/backend test/backend lint/frontend build 전체 통과
- `pnpm docs:check`: 필수 문서 20개 확인 완료
- `pnpm wiki:build`: raw_documents=4, wiki_pages=4 생성 완료
- `pnpm rag:ingest:dry`: documents=8, chunks=36, wiki_chunks=24, raw_chunks=12 준비 완료
- `pnpm test:backend`: 136 passed
- `python -m pytest tests`: 1 passed
- `pnpm lint:backend`: All checks passed
- `pnpm build:frontend`: Vite production build 통과
- `pnpm submission:check`: 제출 조건 증거 9개 확인 완료
- `pnpm submission:check`: 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력, 실행 가능한 Python, LLM 활용 기록, LLM 생성 코드 그대로 사용 금지 증거 확인
- `git diff --check`: exit 0, 생성된 wiki와 기존 문서의 CRLF 경고만 있음
- Playwright smoke: `http://127.0.0.1:5173` 렌더 확인, CORS/favicon console error 없음
- 2026-05-23 local demo smoke: Supabase key는 있으나 live schema가 미적용된 상태에서 `/api/chat`이 in-memory/local fallback으로 응답하고 브라우저 채팅에서 실패 toast 없이 답변 렌더링 확인

실제 Supabase/Gemini/Google 키가 있을 때 추가로 실행할 검증:

```powershell
pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>
pnpm env:check:strict
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
| `docs/product/demo-scenario.md` | 20-25분 데모 흐름 | 준비됨 |
| `docs/report/report-outline.md` | 6-10페이지 보고서 구성 | 준비됨 |
| `docs/report/presentation-outline.md` | 발표자료 구성과 시간 배분 | 준비됨 |
| `docs/architecture/python-core-logic.md` | 발표에서 설명할 Python 핵심 로직 | 준비됨 |
| `docs/llm/agent-coding-evidence.md` | 에이전트 기반 코딩 활용 증거 | 준비됨 |
| `docs/llm/usage-log.md` | LLM 사용 목적과 직접 검토/수정/검증 기록 | 준비됨 |
| `docs/contributing/plans-status.md` | 구현 상태와 다음 작업 | 준비됨 |
| `docs/contributing/feature-registry.md` | 기능 소유 영역과 중복 방지 | 준비됨 |

## 5. 제출 전 남은 일

1. Supabase 프로젝트에 `supabase/schema.sql` 적용.
2. `backend/.env`, `frontend/.env`에 실제 키 입력.
3. `frontend/.env`에는 Supabase Framework 화면의 `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`를 입력.
4. `pnpm live:smoke-plan -- --user-id <supabase-auth-user-uuid> --email <email> --password <password>`로 누락값 확인.
5. `pnpm env:check:strict`, `pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm supabase:login-smoke -- --email <email> --password <password>`, `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>` 실행.
6. Gemini key로 `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke`, `pnpm rag:ingest:embeddings` 실행.
7. 앱에서 로그인, 질문, 추천, 일정, Calendar export를 한 번씩 녹화.
8. 발표에서 `AGENTS.md`, `docs/llm/agent-coding-evidence.md`, `docs/llm/usage-log.md`를 열어 에이전트 활용 과정을 설명.
9. 보고서에 실제 스크린샷과 검증 명령 결과를 붙임.
10. 발표영상 녹화 전 `docs/product/demo-scenario.md` 순서대로 리허설.
11. 홈서버 배포를 보여줄 경우 Docker Compose 배포 URL은 보조 시연으로만 쓰고, 노트북 로컬 실행과 녹화 백업을 함께 준비.
