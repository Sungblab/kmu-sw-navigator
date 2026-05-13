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

## 다음 작업 후보

1. FastAPI 설정 분리와 `/api` 라우터 구조 생성
2. Supabase schema에 profile/memory/chat/calendar token 테이블과 RLS 추가
3. 프로필/메모리 API와 메모리 이벤트 기록 구현
4. 홈 AI 상담 shell과 대화형 선택지 UX 구현
5. Gemini service, embedding service, raw/wiki ingest script 구현
6. RAG chat API, retrieval router, Google grounding 구현
7. 일정 D-day와 Google Calendar 내보내기 구현

## 상태 기록 규칙

- 기능을 시작하면 이 문서에 한 줄을 추가합니다.
- 기능을 끝내면 검증 명령과 결과를 관련 plan 문서에 남깁니다.
- 실제 코드와 테스트 결과가 문서보다 우선합니다.
