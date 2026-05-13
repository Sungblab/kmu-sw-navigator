# 작업 상태

이 문서는 현재 계획과 진행 상태를 요약합니다. 세부 설계는 `docs/superpowers/specs/`, 실행 계획은 `docs/superpowers/plans/`를 확인합니다.

## 현재 활성 작업

| 날짜 | 작업 | 상태 | 관련 문서 |
| --- | --- | --- | --- |
| 2026-05-13 | repo와 문서 기반 세팅 | 초기 세팅 완료 | `docs/superpowers/plans/2026-05-13-repo-docs-initialization.md` |
| 2026-05-13 | Mini LLM Wiki foundation | 구현/검증 완료 | `docs/superpowers/plans/2026-05-13-mini-llm-wiki.md` |

## 다음 작업 후보

1. FastAPI 설정 분리와 `/api` 라우터 구조 생성
2. Supabase schema 적용과 RLS 검토
3. Gemini service와 embedding service 구현
4. raw/wiki chunk embedding ingest script 구현
5. RAG chat API와 wiki-first retrieval 구현
6. React 앱 shell과 탭 UI 구현

## 상태 기록 규칙

- 기능을 시작하면 이 문서에 한 줄을 추가합니다.
- 기능을 끝내면 검증 명령과 결과를 관련 plan 문서에 남깁니다.
- 실제 코드와 테스트 결과가 문서보다 우선합니다.
