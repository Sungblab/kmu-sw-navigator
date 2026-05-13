# 기능 레지스트리

이 문서는 중복 작업을 막기 위한 기능 소유 영역입니다. 새 작업을 시작하기 전에 관련 feature id를 확인합니다.

상태:

- `planned`: 설계됨
- `active`: 구현 중
- `complete`: 1차 구현 완료
- `blocked`: 결정 필요

| Feature ID | 상태 | 소유 경로 | 설명 | 중복 방지 |
| --- | --- | --- | --- | --- |
| repo-docs-foundation | active | `README.md`, `AGENTS.md`, `docs/` | 문서 인덱스, 개발 가이드, LLM 활용 기록 구조 | 문서 구조 변경 전 `docs/README.md`를 먼저 수정 |
| backend-api-foundation | planned | `backend/app/` | FastAPI 앱, 라우터, 설정, 인증 | API 라우트는 resource별 파일로 분리 |
| supabase-schema | planned | `supabase/schema.sql` | profiles, document_chunks, assignments, logs | schema 변경은 SQL 파일과 docs를 함께 갱신 |
| mini-llm-wiki | active | `data/raw/`, `data/wiki/`, `backend/app/services/wiki_compiler.py`, `backend/app/services/markdown_chunker.py` | 원문 자료를 wiki page로 컴파일하고 RAG 우선 검색 계층으로 사용 | LangGraph/worker 없이 Python script 중심으로 유지 |
| rag-ingest | planned | `backend/app/services/`, `data/` | Markdown chunking, embedding, Supabase insert | embedding 차원은 768로 유지 |
| rag-chat | planned | `backend/app/api/`, `frontend/src/` | 질문 답변, 출처 표시, chat log | 답변은 검색된 문서 근거가 부족하면 제한적으로 답변 |
| recommend-track-club | planned | `backend/app/services/`, `frontend/src/` | 트랙/동아리/활동 추천 | 조건문/딕셔너리 기반 로직을 발표 가능하게 유지 |
| schedule-dday | planned | `backend/app/services/`, `frontend/src/` | 자연어 일정 추출, 저장, D-day | 저장 전 미리보기 흐름을 우선 |
| llm-usage-log | planned | `docs/llm/`, `backend/app/services/` | 개발 과정 기록과 앱 사용 로그 | Codex 사용과 Gemini API 사용을 구분 |
| report-presentation | planned | `docs/report/` | 보고서, 발표자료, 데모 시나리오 | 실행 결과 캡처와 검증 명령을 함께 기록 |
