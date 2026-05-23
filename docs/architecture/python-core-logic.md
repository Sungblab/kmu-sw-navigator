# 핵심 Python 로직 설명

이 문서는 발표와 보고서에서 설명할 수 있어야 하는 Python 판단 로직을 정리한다. 목표는 LLM이 만든 코드를 그대로 제출한 것이 아니라, 구현자가 수업에서 배운 Python 요소를 사용해 직접 설명, 수정, 검증할 수 있는 핵심 로직을 남기는 것이다.

현재 제품 목표는 단순 로컬 데모가 아니라 **Supabase Auth/Postgres에 사용자별 데이터가 저장되는 SaaS형 학업 내비게이터**다. 따라서 in-memory fallback은 외부 키 누락, live schema 미적용, 발표 장애에 대비한 보조 경로로만 설명하고, 핵심 구현 설명은 Python FastAPI 서비스가 실제 사용자 입력을 받아 Supabase 저장소와 RAG/Gemini 경로로 처리하는 흐름에 맞춘다.

## 과제 조건 충족 매핑

현재 구현에서 수업 조건을 충족하는 핵심 Python 부분은 다음과 같다.

| 과제 조건 | 직접 설명 가능한 구현 위치 | 설명 |
| --- | --- | --- |
| 사용자 입력 | `/api/chat`, `/api/profile`, `/api/memories` | 사용자가 입력한 질문, 프로필, 메모리 수정 내용을 FastAPI 요청으로 받아 Python 함수에 전달한다. |
| 조건문 | `classify_memory_sensitivity()`, `detect_intent()` | 입력 문장에 포함된 키워드에 따라 메모리 저장 여부와 채팅 상담 유형을 분기한다. |
| 반복문 | `any(...)`, list comprehension, active memory filtering | 키워드 목록과 메모리 목록을 순회해 조건에 맞는 항목을 찾는다. |
| 함수 | `create_memory_candidate()`, `confirm_memory()`, `build_chat_response()` | 기능을 설명 가능한 단위로 분리해 테스트와 발표 설명이 가능하게 했다. |
| 리스트/딕셔너리 | keyword list, status mapping dict, `value_json`, evidence payload | 추천/분류 기준과 API 응답 데이터를 구조화해서 사용한다. |
| 의미 있는 출력 | `ChatResponse`, `MemoryResponse`, `MemoryEventResponse` | 입력에 따라 상담 답변, intent, 선택지, 근거, 메모리 상태가 달라진다. |
| 실행 가능한 Python 코드 | `backend/app/services/`, `backend/app/api/`, `backend/tests/` | `pnpm test:backend`로 재현 가능한 FastAPI/Python 테스트를 실행할 수 있다. |
| LLM 활용 기록 | `docs/llm/usage-log.md` | LLM 사용 목적과 직접 검토/수정/검증한 내용을 기록한다. |
| LLM 생성 코드 그대로 사용 금지 | `AGENTS.md`, `docs/llm/agent-coding-evidence.md`, `docs/report/submission-checklist.md` | 코드 주석, 테스트, 검증 기록, 직접 수정 내역으로 LLM 출력물을 그대로 제출하지 않았음을 설명한다. |

보고서에는 이 표를 기준으로 “핵심 Python 로직은 직접 검토하고 수정했으며, 조건문/반복문/함수/리스트/딕셔너리를 사용해 사용자 입력에 따른 결과를 만들었다”고 설명한다.

## LLM 생성 코드 그대로 사용 금지 대응

교수님이 금지한 것은 LLM 사용 자체가 아니라, 생성된 코드를 이해와 수정 없이 그대로 제출하는 것이다. 이 프로젝트는 다음 방식으로 그 위험을 줄인다.

- 핵심 로직은 `service` 함수로 분리해 발표에서 입력, 분기, 반복, 출력 흐름을 설명할 수 있게 한다.
- 추천, 일정, RAG 근거 선택, 메모리 민감도처럼 판단이 들어가는 부분에는 “왜 이 기준을 쓰는지”를 주석으로 남긴다.
- `backend/tests/`와 `tests/`로 동작을 재현해, 코드가 단순 복사물이 아니라 실행 검증된 구현임을 보인다.
- `docs/llm/usage-log.md`에는 Codex가 도운 목적과 사람이 직접 검토/수정/검증한 내용을 기록한다.
- `pnpm submission:check`는 “LLM 생성 코드 그대로 사용 금지 증거” 항목까지 확인해 제출 전 누락을 잡는다.

## 0. 사용자 인증과 user_id 결정

구현 위치:

- `backend/app/api/auth.py`
- `backend/app/api/dependencies.py`

API는 사용자가 보낸 profile id를 그대로 믿지 않는다. 프론트엔드는 Supabase session의 access token만 `Authorization` header로 보내고, 백엔드는 검증된 token의 사용자만 현재 user id로 사용한다.

| 환경 | 입력 | user id 결정 |
| --- | --- | --- |
| `SUPABASE_JWT_SECRET` 있음 | `Authorization: Bearer <token>` | 로컬 JWT 검증을 통과한 payload의 `sub` |
| `SUPABASE_JWT_SECRET` 없음, backend Supabase env 있음 | `Authorization: Bearer <token>` | Supabase Auth `/auth/v1/user` API가 반환한 `id` |
| Supabase env 없음 | 없음 | 401 응답. 테스트는 FastAPI dependency override로만 user id를 주입 |

이 분기를 둔 이유는 실제 서비스에서 사용자가 임의로 user id를 바꾸지 못하게 하고, `SUPABASE_JWT_SECRET`을 아직 받지 못한 팀원 환경에서도 service role을 가진 백엔드가 Supabase Auth API로 session을 검증할 수 있게 하기 위해서다. 예전의 `X-User-Id` 개발 fallback은 런타임에서 제거했고, 오프라인 단위 테스트만 dependency override로 user id를 주입한다.

## 1. 메모리 민감도 분류

구현 위치:

- `backend/app/services/memory_service.py`
- `classify_memory_sensitivity()`

사용자 대화에서 나온 내용을 개인화 메모리로 저장할 때, 모든 내용을 바로 저장하지 않는다. 먼저 Python 키워드 규칙으로 민감도를 나눈다.

| 분류 | 예시 | 처리 |
| --- | --- | --- |
| `low` | AI, 백엔드, 프로젝트 선호 | 자동 저장 가능 |
| `medium` | 학점, 성적, 취업 불안 | 사용자 확인 필요 |
| `high` | 비밀번호, 계좌, 주민등록 관련 정보 | 저장 거부 |

이 로직은 LLM이 메모리 후보를 제안하더라도 최종 저장 정책은 Python 코드가 통제한다는 의미가 있다. 특히 비밀번호나 계좌처럼 저장하면 안 되는 정보는 LLM 판단 전에 차단한다.

## 2. 메모리 상태와 이벤트 기록

구현 위치:

- `backend/app/services/memory_service.py`
- `create_memory_candidate()`
- `confirm_memory()`
- `reject_memory()`
- `archive_memory()`
- `update_memory()`

메모리는 민감도 분류 결과에 따라 상태가 달라진다.

| 정책 결정 | 메모리 상태 | 이유 |
| --- | --- | --- |
| `auto_save` | `active` | 일반 관심사는 상담 품질을 높이는 데 바로 사용할 수 있음 |
| `requires_confirmation` | `candidate` | 민감할 수 있어 사용자가 저장 여부를 확인해야 함 |
| `reject` | `rejected` | 저장하면 안 되는 정보라 활성 메모리로 쓰지 않음 |

모든 판단은 `memory_events`에 남길 수 있는 구조로 설계했다. 과제 제출 관점에서는 “AI가 사용자를 몰래 기억했다”가 아니라 “저장 판단과 검토 기록이 남는다”는 점을 설명할 수 있다.

## 3. 채팅 의도 분류

구현 위치:

- `backend/app/services/chat_contract_service.py`
- `detect_intent()`

채팅은 먼저 Python 키워드 규칙으로 질문 유형을 나눈다. 이 intent 값은 내부 RAG, Google grounding, 일정 관련 action을 어느 정도 붙일지 결정하는 라우팅 기준으로 쓰인다.

| intent | 주요 키워드 | 화면 행동 |
| --- | --- | --- |
| `schedule_assistant` | 과제, 마감, 시험, 일정, 제출 | 일정 탭/일정 미리보기 선택지 |
| `career_advisor` | 취업, 진로, 인턴, 포트폴리오 | 진로 탭과 최신 정보 검증 필요 표시 |
| `startup_project_mentor` | 프로젝트, 창업, 공모전, 해커톤 | 프로젝트 탭 |
| `academic_advisor` | 수강, 교과, 학업, 과목, 트랙 | 학업 탭과 내부 자료 출처 슬롯 |
| `general` | 위 기준에 걸리지 않음 | 다음 상담 방향 선택지 |

일정 의도를 가장 먼저 판정하는 이유는 일정 문장이 학업 단어와 함께 등장하는 경우가 많기 때문이다. 예를 들어 “자료구조 과제 다음주까지”는 학업 주제이기도 하지만, 사용자가 기대하는 행동은 일정 저장에 가깝다.

## 4. Chat contract와 근거 슬롯

구현 위치:

- `backend/app/services/chat_contract_service.py`
- `build_chat_response()`

`/api/chat`은 프론트엔드가 사용할 응답 구조를 고정하고, 여기에 내부 RAG 근거, 개인화 메모리, 필요 시 Gemini 답변과 Google grounding 근거를 붙인다.

응답에는 다음 필드가 포함된다.

- `answer`: 사용자에게 보여줄 답변
- `intent`: 질문 분류 결과
- `actions`: 이동할 탭이나 후속 행동
- `evidence`: 개인화 근거, 내부 자료 근거, 웹 근거 슬롯
- `choices`: 다음 질문 선택지
- `memory_updates`: 생성/수정될 메모리 후보
- `needs_verification`: 최신성 검증이 필요한 항목

이 구조를 먼저 만든 이유는 RAG, Google grounding, Calendar export를 나중에 붙여도 프론트엔드 화면과 API 계약을 크게 바꾸지 않기 위해서다.

## 5. 저장소 adapter 선택

구현 위치:

- `backend/app/api/dependencies.py`
- `backend/app/services/store_protocols.py`
- `backend/app/services/supabase_stores.py`

프로필과 메모리는 `ProfileStore`, `MemoryStore` protocol을 통해 사용한다. 그래서 API와 핵심 로직은 저장소가 in-memory인지 Supabase인지 직접 알 필요가 없다.

| 실행 환경 | 저장소 | 이유 |
| --- | --- | --- |
| Supabase 환경 변수 있음 | `SupabaseProfileStore`, `SupabaseMemoryStore` | 실제 서비스에서 프로필/메모리를 영속 저장하고, schema 미적용 오류도 live blocker로 드러냄 |
| Supabase 환경 변수 없음 | `InMemoryProfileStore`, `InMemoryMemoryStore` | 외부 키가 없는 단위 테스트와 오프라인 검증용 보조 경로 |

Supabase adapter에서는 `user_id`를 request body가 아니라 인증 dependency에서 받은 값으로 붙인다. 메모리 조회도 항상 `user_id`와 `memory_id`를 함께 조건으로 걸기 때문에 다른 사용자의 메모리가 섞이지 않는다.

## 6. Embedding 생성과 차원 검증

구현 위치:

- `backend/app/services/embedding_service.py`
- `backend/app/scripts/ingest_documents.py`

RAG chunk는 후속 검색을 위해 768차원 embedding을 가질 수 있다. Gemini API가 있는 환경에서는 `GeminiEmbeddingService`가 실제 embedding을 만들고, 테스트에서는 `DeterministicEmbeddingService`로 같은 shape를 재현한다.

핵심 판단은 다음과 같다.

- embedding 입력에는 `title`, `heading_path`, `content`를 함께 넣는다.
- embedding 길이가 `GEMINI_EMBEDDING_DIM`과 다르면 즉시 오류로 처리한다.
- API key가 없으면 embedding ingest는 실행하지 않고, dry-run과 일반 chunk ingest는 계속 가능하게 둔다.

이 구조는 외부 API가 없어도 과제 테스트를 실행할 수 있게 하면서, 실제 배포에서는 같은 Python 흐름으로 Gemini embedding을 붙일 수 있게 한다.

## 7. Local RAG 근거 선택

구현 위치:

- `backend/app/services/retrieval_service.py`
- `backend/app/api/chat.py`
- `backend/app/services/chat_contract_service.py`

현재 `/api/chat`은 질문을 받으면 local retriever로 `data/wiki`, `data/raw` chunk를 검색하고, 그 결과를 `evidence.internal_sources`에 넣는다.

핵심 판단은 다음과 같다.

- 질문에서 한글/영문/숫자 토큰을 뽑는다.
- 제목, category, heading path, content에 토큰이 포함되면 점수를 준다.
- 점수가 같으면 `wiki_page`를 `raw_document`보다 먼저 둔다.
- 근거가 없으면 evidence note에 내부 근거 부족을 표시한다.

이 로직은 수업시간에 배운 조건문, 반복문, 리스트/딕셔너리를 사용해 사용자 입력에 따라 의미 있는 출력이 달라지는 부분으로 설명할 수 있다.

Supabase 환경 변수가 있으면 같은 `RetrievalResult` 형태를 유지하면서 `search_document_chunks_text` RPC를 호출한다. Gemini key까지 있으면 질문을 `RETRIEVAL_QUERY` embedding으로 바꾼 뒤 `match_document_chunks` vector RPC를 호출한다. 즉, local/text/vector 검색의 출력 구조가 같아서 frontend evidence 표시를 바꾸지 않아도 된다.

## 8. Gemini 답변 생성 prompt 구성

구현 위치:

- `backend/app/services/answer_generation_service.py`
- `backend/app/services/chat_contract_service.py`
- `backend/app/api/chat.py`

Gemini key가 있는 환경에서는 Python 코드가 사용자 질문, intent, 개인화 메모리, 내부 검색 근거를 prompt로 구성한다. 이때 근거가 없으면 “내부 자료 근거 없음”을 명시해 LLM이 없는 근거를 지어내지 않게 한다.

핵심 판단은 다음과 같다.

- 검색 근거는 최대 5개까지만 prompt에 넣는다.
- content가 너무 길면 500자에서 자른다.
- 최신 취업/공모전 정보는 Google grounding 전까지 확정 답변하지 않도록 규칙에 넣는다.
- `GEMINI_API_KEY`가 없으면 기존 deterministic answer를 사용한다.

## 9. Google grounding 기반 최신 웹 근거

구현 위치:

- `backend/app/services/answer_generation_service.py`
- `backend/app/services/chat_contract_service.py`
- `backend/app/api/chat.py`

진로, 취업, 창업, 공모전처럼 최신성이 필요한 질문은 내부 RAG만으로 확정하기 어렵다. 그래서 `career_advisor`, `startup_project_mentor` intent에서만 Gemini Google Search grounding을 호출한다.

핵심 판단은 다음과 같다.

- 학업/학교 자료 질문은 내부 RAG 근거를 우선한다.
- 진로/취업/창업 질문은 `types.Tool(google_search=types.GoogleSearch())`를 사용한 Gemini grounding generator를 호출한다.
- grounding 응답의 `grounding_metadata.grounding_chunks[].web`에서 title, uri, domain을 추출한다.
- 추출한 웹 근거는 `evidence.web_sources`에 넣어 내부 자료 근거와 분리한다.
- grounding이 실패하면 기존 deterministic 답변과 검증 필요 메시지를 유지한다.

이 구조는 최신 웹 검색 여부를 Python intent 조건문으로 통제하고, LLM이 만든 답변과 출처를 API 응답에서 분리해 검토할 수 있게 한다.

## 10. Chat session/message 저장

구현 위치:

- `backend/app/services/chat_store.py`
- `backend/app/services/supabase_stores.py`
- `backend/app/api/chat.py`

채팅 API는 답변을 만든 뒤 사용자 메시지와 assistant 메시지를 한 쌍으로 저장한다. 새 대화이면 `session_id`를 만들고, 이어지는 대화이면 요청의 `session_id`를 재사용한다.

핵심 판단은 다음과 같다.

- session title은 첫 질문 앞부분으로 만든다.
- assistant message에는 답변뿐 아니라 evidence와 memory update snapshot을 함께 저장한다.
- Supabase env가 없으면 in-memory store로 테스트와 발표 실행을 유지한다.

이 로직은 사용자 입력을 저장 가능한 대화 기록으로 바꾸고, 이후 recent chat 목록과 LLM 사용 기록으로 확장할 수 있게 한다.

## 11. 자연어 일정과 D-day 계산

구현 위치:

- `backend/app/services/assignment_service.py`
- `backend/app/api/assignments.py`
- `backend/app/services/supabase_stores.py`

일정 preview는 사용자가 입력한 문장에서 제목, 과목, 마감일을 추출한다. `GEMINI_API_KEY`가 있으면 Gemini parser가 JSON 구조화를 먼저 시도하고, 실패하거나 키가 없으면 Python 규칙 parser로 fallback한다.

핵심 판단은 다음과 같다.

- `오늘`, `내일`, `다음주 금요일` 같은 상대 날짜를 조건문으로 처리한다.
- `2026-05-20`, `5월 20일` 같은 날짜 패턴은 정규식으로 처리한다.
- Gemini parser 결과는 `ParsedAssignment` dataclass로 변환하고, D-day 계산과 최종 응답 생성은 Python 함수가 맡는다.
- parser가 예외를 내거나 필수 제목이 비어 있으면 기존 Python 규칙으로 다시 처리한다.
- preview 응답의 `parser` 필드로 `gemini`와 `python_rules` 경로를 구분한다.
- D-day는 마감일과 기준 날짜의 차이로 계산한다.
- 필수 정보가 부족하면 `missing_fields`와 낮은 confidence를 반환한다.
- 저장/완료/삭제는 `AssignmentStore` protocol을 통해 in-memory와 Supabase adapter를 같은 API로 사용한다.
- Supabase adapter는 `user_id`와 `assignment_id`를 함께 조건으로 걸어 사용자별 일정 소유권을 유지한다.

이 로직은 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력 조건을 발표에서 설명하기 좋은 Python 핵심 로직이다.

## 12. Google Calendar export payload

구현 위치:

- `backend/app/services/calendar_service.py`
- `backend/app/api/assignments.py`

Calendar export는 저장된 assignment를 Google Calendar event 형식으로 바꾼다. Google Calendar event 생성에는 시작과 종료 시간이 필요하므로, 과제 마감 시각을 종료 시간으로 두고 시작 시간은 30분 전으로 계산한다.

핵심 판단은 다음과 같다.

- 과목이 있으면 event summary를 `과목 · 제목`으로 만들고, 없으면 제목만 사용한다.
- memo는 description에 넣어 Calendar에서 원문 맥락을 볼 수 있게 한다.
- 이미 `calendar_event_id`와 `calendar_synced_at`이 있으면 다시 내보내지 않고 `already_exported=true`를 반환한다.
- token이 없으면 export 성공으로 표시하지 않는다. live 제품 기준에서는 실제 Google `events.insert`가 성공했을 때만 일정에 `calendar_event_id`를 남긴다.
- token이 있으면 보호 저장된 access token을 server-side에서만 복원해 `Authorization: Bearer` header로 Google `events.insert`를 호출한다.

이 로직은 날짜 계산, 조건문, 딕셔너리 형태의 Google event payload, 저장소 protocol 호출이 모두 포함되어 발표에서 “외부 API 연동 전 핵심 Python 처리”로 설명할 수 있다.

## 13. Google Calendar OAuth connect

구현 위치:

- `backend/app/services/google_calendar_oauth_service.py`
- `backend/app/services/google_oauth_token_service.py`
- `backend/app/api/integrations.py`

Calendar OAuth는 앱 로그인과 분리한다. Supabase Auth는 앱 사용자 식별을 맡고, Google OAuth는 Calendar event 생성 권한만 받는다.

핵심 판단은 다음과 같다.

- Google OAuth env가 없으면 `configured=false`를 반환해 로컬 실행을 막지 않는다.
- env가 있으면 백엔드가 consent URL을 만들고, 프론트는 그 URL로 이동만 한다.
- OAuth `state`에는 raw user id를 그대로 넣지 않고 signed opaque payload를 넣어 URL에서 사용자 id가 직접 노출되지 않게 한다.
- 기본 scope는 Calendar event 생성에 필요한 `https://www.googleapis.com/auth/calendar.events`로 제한한다.
- callback에서는 `state` 서명을 검증해 user id를 복원하고, authorization code를 Google token endpoint로 교환한다.
- access/refresh token은 프론트로 반환하지 않고 in-memory 또는 Supabase token store에 저장한다.
- access token이 만료되었으면 refresh token으로 새 access token을 발급받고 저장소를 갱신한 뒤 Calendar API를 호출한다.

이 로직은 외부 인증을 바로 호출하지 않아도 설정 여부, 권한 범위, URL 생성, 사용자 정보 노출 방지, token 저장 경계를 테스트할 수 있게 만든다.

## 14. 트랙/활동 추천 규칙

구현 위치:

- `backend/app/services/recommendation_service.py`
- `backend/app/api/recommendations.py`

트랙/활동 추천은 LLM이 임의로 생성하지 않고 Python 규칙으로 후보를 만든다.

핵심 판단은 다음과 같다.

- 추천 후보는 `TRACK_RULES`, `ACTIVITY_RULES` 같은 리스트/딕셔너리 구조로 둔다.
- 관심사, 목표, 선호 문구를 정규화해 keyword와 비교한다.
- 학년, 코딩 경험, 학습 선호, 활동 성향, 주간 가능 시간을 조건문으로 점수에 더한다.
- 점수순으로 정렬해 1순위 추천과 대안 후보, 다음 행동 목록을 반환한다.
- 추천 점수를 계산한 뒤에는 최상위 추천 제목과 사용자 입력을 query로 만들어 내부 RAG retriever에서 Mini Wiki/raw/Supabase 근거를 조회한다.
- RAG 근거는 점수 계산에 섞지 않고 `evidence.internal_sources`로만 붙여, 규칙 기반 판단과 출처 설명을 분리한다.

이 로직은 수업 조건인 사용자 입력, 조건문, 반복문, 함수, 리스트/딕셔너리, 의미 있는 출력이 모두 드러나는 핵심 Python 로직이다.

## 15. 환경 점검과 live smoke 분리

구현 위치:

- `backend/app/scripts/check_env.py`
- `backend/app/scripts/supabase_smoke.py`

외부 서비스 키는 과제 repo에 커밋할 수 없으므로, 구현 검증과 live 검증을 분리한다.

| 명령 | 역할 |
| --- | --- |
| `pnpm env:check` | backend/frontend/env 누락 여부를 비밀값 출력 없이 확인 |
| `pnpm env:check:strict` | Supabase core 값이 없으면 실패해 배포 전 gate로 사용 |
| `pnpm supabase:schema-check` | live Supabase에 `schema.sql`의 table/function이 적용됐는지 확인 |
| `pnpm supabase:create-smoke-user --write-root-env` | service role로 Auth 테스트 유저를 만들고 root `.env`에 smoke 값 저장 |
| `pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>` | 실제 Supabase에 profile/memory/event를 write/read |
| `pnpm supabase:auth-smoke -- --access-token <supabase-access-token>` | 실제 Supabase access token으로 FastAPI Bearer 인증과 profile API write/read |
| `pnpm supabase:login-smoke -- --email <email> --password <password>` | Supabase email/password login 후 받은 access token으로 FastAPI profile API write/read |
| `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>` | 실제 Supabase `llm_usage_logs` insert/list |
| `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>` | 저장된 Google OAuth token으로 실제 Calendar event insert |
| `pnpm gemini:smoke` | 실제 Gemini embedding과 일정 parser 호출 |
| `pnpm gemini:answer-smoke` | 실제 Gemini 답변 생성 호출 |
| `pnpm gemini:grounding-smoke` | 실제 Gemini Google Search grounding 호출 |

현재 구조에서는 Supabase Dashboard의 Direct/backend 값과 Framework/frontend 값을 분리해서 사용한다. `SUPABASE_SERVICE_ROLE_KEY`는 backend 전용이며 frontend env에 넣지 않는다.

2026-05-23 live 점검에서는 backend Supabase Direct 값, frontend Supabase Framework 값, Gemini API key가 존재해 `pnpm env:check:strict`, `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke`가 통과했다. service role로 Supabase Auth smoke user를 생성해 UUID/email/password를 gitignored root `.env`에 저장했고, `pnpm supabase:schema-check`는 live 프로젝트에서 `schema.sql`의 table/function이 schema cache에 없다고 확인했다. `pnpm supabase:smoke`, `pnpm supabase:llm-smoke`, `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001`은 입력/env가 아니라 schema 미적용 때문에 실패한다. 필요한 schema 구성은 `profiles`, `raw_documents`, `wiki_pages`, `wiki_logs`, `document_chunks`, `assignments`, `chat_sessions`, `chat_messages`, `chat_logs`, `llm_usage_logs`, `user_memories`, `memory_events`, `google_oauth_tokens`, `search_document_chunks_text`, `match_document_chunks`다.

Python 핵심 로직 주석은 이번 점검에서 `recommendation_service.py`, `retrieval_service.py`, `assignment_service.py`, `memory_service.py`, `chat_contract_service.py`를 다시 확인했다. 추천 점수, Mini Wiki 우선 RAG 검색, Gemini 일정 parser fallback, 메모리 민감도 차단, 일정 intent 우선 분류처럼 발표에서 질문받을 판단 기준에는 이미 의도 주석이 있고, 단순 문법 설명 주석은 추가하지 않았다.

## 16. LLM usage log 저장

구현 위치:

- `backend/app/schemas/llm_usage.py`
- `backend/app/services/llm_usage_log_service.py`
- `backend/app/api/llm_logs.py`
- `backend/app/api/chat.py`

앱 내부에서 Gemini 답변 생성, Google grounding, Gemini 일정 parser 경로를 사용하면 Python 코드가 사용자 입력, 출력, 모델명, 사용 목적, metadata를 `llm_usage_logs` store에 저장한다. embedding ingest CLI는 `--llm-log-user-id`가 명시된 경우 실행 요약을 같은 store에 저장한다.

핵심 판단은 다음과 같다.

- 로그의 `user_id`는 인증 dependency에서 받은 값으로만 붙인다.
- 로그 조회는 `GET /api/llm-logs`에서 현재 사용자 기록만 반환한다.
- Supabase env가 없으면 in-memory fallback으로 발표 화면을 유지한다.
- 채팅 답변은 `rag_chat`, grounding은 `google_grounding`, 일정 parser는 `schedule_parser` feature로 구분한다.
- embedding ingest는 `embedding_ingest` feature로 구분하되, CLI에서 임의 user id를 만들지 않는다.
- 개발 과정에서 LLM을 사용한 기록은 별도로 `docs/llm/usage-log.md`에 남긴다.

이 기능은 과제 조건 중 LLM 활용 기록을 앱 기능과 제출 문서 양쪽에서 보여주기 위한 연결 지점이다.

## 17. 현재 한계와 다음 구현

현재 구현은 Supabase 로그인 세션이 있어야 프론트 앱과 API를 사용할 수 있고, 키가 있으면 Supabase/Gemini/Google adapter가 live 경로를 사용하도록 설계되어 있다. in-memory와 deterministic 경로는 외부 키가 없는 테스트 보조 수단이며, 제출 목표는 live 연결이 가능한 항목을 실제 smoke로 확인하고 결과를 문서에 남기는 것이다.

아직 live 환경에서 검증해야 하는 부분:

- 실제 Supabase 프로젝트에 `supabase/schema.sql` 적용 후 `pnpm supabase:schema-check`, `pnpm supabase:smoke`, `pnpm supabase:llm-smoke`, `pnpm supabase:login-smoke --api-base http://127.0.0.1:8001`
- 로컬 FastAPI 서버 실행 후 실제 Supabase session token으로 `pnpm supabase:auth-smoke -- --access-token <supabase-access-token>` 실행. `SUPABASE_JWT_SECRET`이 있으면 로컬 JWT 검증, 없으면 Supabase Auth API 검증 경로를 쓴다.
- 수동 token 복사 없이 확인하려면 `SUPABASE_SMOKE_EMAIL`, `SUPABASE_SMOKE_PASSWORD` 또는 CLI 인자로 실제 Supabase 계정을 제공한 뒤 `pnpm supabase:login-smoke -- --email <email> --password <password>`
- 실제 Supabase DB에서 `llm_usage_logs` 기록을 확인하려면 `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>`
- 저장된 Google Calendar token으로 실제 event insert를 확인하려면 `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>`
- 실제 Gemini key를 넣은 `pnpm gemini:smoke`, embedding ingest
- Supabase text/vector retrieval live RPC smoke
- 실제 Gemini key를 넣은 `pnpm gemini:answer-smoke`
- chat session/message live DB smoke
- assignment live DB smoke
- 실제 Google OAuth consent와 Calendar event insert live smoke
- 실제 Gemini key를 넣은 일정 parsing live smoke
- 실제 Gemini key를 넣은 `pnpm gemini:grounding-smoke`
- Gemini 일정 parser, Google grounding, embedding ingest의 feature별 LLM usage log 세분화

다음 단계에서는 이 문서의 Python 규칙을 유지하면서 live key가 필요한 검증을 순서대로 수행한다.
