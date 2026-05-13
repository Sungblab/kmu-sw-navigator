# 로드맵

## 현재 제품 형태

국민대 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터입니다. 사용자는 자연어로 질문하고, 시스템은 사용자 프로필/메모리, 학교/학부 자료, 최신 웹 grounding을 함께 활용해 학업, 진로/취업/창업, 프로젝트, 일정 관리 답변을 제공합니다.

## 1차 목표

| 영역 | 상태 | 설명 |
| --- | --- | --- |
| Repo와 문서 기반 | 완료 | README, 기여 가이드, 문서 인덱스, LLM 활용 기록 구조 |
| FastAPI 기반 | 진행 중 | `/health`, `/api`, service, script, 테스트 구조 |
| Supabase schema | 진행 중 | Auth, Postgres, pgvector, raw/wiki/chunk/log/calendar token 테이블 |
| Mini LLM Wiki | 진행 중 | raw markdown을 신입생용 wiki page로 컴파일 |
| 개인화 프로필/메모리 | 1차 구현 완료 | 필수 프로필, 대화형 메모리, 메모리 이벤트/투명성 |
| RAG ingest | 1차 구현 완료 | Markdown chunking, embedding, document_chunks 저장 script |
| RAG chat API | 1차 구현 완료 | local/text/vector retrieval, Gemini 답변, 출처, session 저장 |
| Google grounding | 1차 구현 완료 | 최신 진로/취업/창업/공모전 정보 보강, live smoke 대기 |
| 추천 기능 | 1차 구현 완료 | 조건문/딕셔너리 기반 트랙/활동 추천, RAG 출처, 메모리 입력 |
| 일정 관리 | 1차 구현 완료 | 자연어 일정 추출, 저장, D-day 계산, Google Calendar 내보내기 |
| React UI | 1차 구현 완료 | Claude/NotebookLM식 workspace, 모바일 drawer, 기능 탭 |
| 보고서/발표 | 시작 전 | 6-10페이지 보고서, 20-25분 발표영상 |

## 우선순위

1. repo와 문서 체계
2. 제품 범위 확장 spec과 문서 정리
3. 프로필/메모리 foundation
4. Mini LLM Wiki와 Supabase schema
5. Gemini 연결과 RAG ingest
6. RAG chat API와 Google grounding
7. 추천/일정/Calendar 기능
8. React UI
9. 테스트, 보고서, 발표자료, 데모 영상

## 완료 기준

- 팀원이 README와 dev guide만 보고 로컬 실행을 시작할 수 있습니다.
- 사용자가 소속, 학년, 교과과정을 설정하고 개인 메모리를 확인/수정/삭제할 수 있습니다.
- RAG 답변에 출처가 표시됩니다.
- 답변에는 개인화 근거, 내부 자료 근거, 최신 웹 근거가 분리 표시됩니다.
- 추천과 일정 기능이 Python 코드로 설명 가능합니다.
- 자연어 과제 등록 후 D-day와 Google Calendar 내보내기를 데모할 수 있습니다.
- LLM 활용 기록이 개발 과정과 함께 남아 있습니다.
- 발표 데모가 sample data로 재현 가능합니다.
