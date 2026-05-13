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
| backend-api-foundation | planned | `backend/app/` | FastAPI 앱, 라우터, 설정, 인증 | API 라우트는 resource별 파일로 분리 |
| supabase-schema | planned | `supabase/schema.sql` | profiles, document_chunks, assignments, logs | schema 변경은 SQL 파일과 docs를 함께 갱신 |
| mini-llm-wiki | active | `data/raw/`, `data/wiki/`, `backend/app/services/wiki_compiler.py`, `backend/app/services/markdown_chunker.py` | 원문 자료를 wiki page로 컴파일하고 RAG 우선 검색 계층으로 사용 | LangGraph/worker 없이 Python script 중심으로 유지 |
| rag-ingest | planned | `backend/app/services/`, `data/` | Markdown chunking, embedding, Supabase insert | embedding 차원은 768로 유지 |
| rag-chat | planned | `backend/app/api/`, `frontend/src/` | 질문 답변, 출처 표시, chat log | 답변은 검색된 문서 근거가 부족하면 제한적으로 답변 |
| frontend-ui-mockups | retired | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 로그인/메인 화면의 정적 HTML 목업 기록 | 실제 UI는 개인화 SW 내비게이터 React 구현으로 대체 |
| chatbot-evidence-visualization | retired | `docs/superpowers/specs/`, `docs/superpowers/plans/` | 챗봇 답변 옆 출처, 로드맵, 추천 이유 시각화 목업 기록 | 근거 표시 UX는 `personalized-sw-navigator-design`에 통합 |
| personalized-sw-navigator-design | complete | `docs/superpowers/specs/2026-05-13-personalized-sw-navigator-design.md`, `docs/superpowers/plans/2026-05-13-personalized-sw-navigator-foundation.md` | 신입생 전용에서 전체 학년 개인화 SW 내비게이터로 제품 범위 확장 | 레포 이름 변경은 별도 작업으로 미루고 문서/구현 범위만 먼저 정렬 |
| user-profile-memory | planned | `backend/app/api/`, `backend/app/services/`, `backend/app/schemas/`, `supabase/schema.sql`, `frontend/src/` | 필수 프로필, 대화형 메모리, memory_events, 메모리 수정/삭제 | `profiles`, `user_memories`, `memory_events`, `chat_messages` 관계를 유지 |
| grounded-career-advisor | planned | `backend/app/services/`, `docs/architecture/`, `frontend/src/` | 최신 진로/취업/창업 정보에 Google grounding 적용 | 학교 내부 RAG와 웹 grounding 근거를 분리 표시 |
| google-calendar-export | planned | `backend/app/api/`, `backend/app/services/`, `supabase/schema.sql`, `frontend/src/` | 저장된 과제/일정을 Google Calendar event로 내보내기 | 앱 로그인과 Calendar OAuth consent를 분리하고 토큰은 server-only 처리 |
| navigator-home-ui | planned | `frontend/src/` | 홈, 학업, 진로, 프로젝트, 일정, 기록 탭 기반 개인화 UI | AI 입력창을 홈 중심에 두고 탭은 intent 힌트로 사용 |
| recommend-track-club | planned | `backend/app/services/`, `frontend/src/` | 트랙/동아리/활동 추천 | 조건문/딕셔너리 기반 로직을 발표 가능하게 유지 |
| schedule-dday | planned | `backend/app/services/`, `frontend/src/` | 자연어 일정 추출, 저장, D-day | 저장 전 미리보기 흐름을 우선 |
| llm-usage-log | planned | `docs/llm/`, `backend/app/services/` | 개발 과정 기록과 앱 사용 로그 | Codex 사용과 Gemini API 사용을 구분 |
| report-presentation | planned | `docs/report/` | 보고서, 발표자료, 데모 시나리오 | 실행 결과 캡처와 검증 명령을 함께 기록 |
