# 로드맵

## 현재 제품 형태

국민대 소프트웨어융합대학 신입생을 위한 RAG 기반 AI 웹앱입니다. 사용자는 자연어로 질문하고, 시스템은 학교/학부 자료를 검색한 뒤 출처와 함께 답변합니다. 추천과 일정 관리 기능은 과제 조건을 명확히 충족하면서 실제 사용자 가치도 제공합니다.

## 1차 목표

| 영역 | 상태 | 설명 |
| --- | --- | --- |
| Repo와 문서 기반 | 진행 중 | README, 기여 가이드, 문서 인덱스, LLM 활용 기록 구조 |
| FastAPI 기반 | 시작 전 | `/health`, API 라우터, schema, service 분리 |
| Supabase schema | 시작 전 | Auth, Postgres, pgvector, 로그 테이블 |
| RAG ingest | 시작 전 | Markdown chunking, embedding, document_chunks 저장 |
| RAG chat API | 시작 전 | 질문 embedding, pgvector RPC, Gemini 답변, 출처 |
| 추천 기능 | 시작 전 | 조건문/딕셔너리 기반 트랙/활동 추천 |
| 일정 관리 | 시작 전 | 자연어 일정 추출, 저장, D-day 계산 |
| React UI | 시작 전 | 로그인, 챗봇, 추천, 일정, 로그 탭 |
| 보고서/발표 | 시작 전 | 6-10페이지 보고서, 20-25분 발표영상 |

## 우선순위

1. repo와 문서 체계
2. Supabase schema와 백엔드 skeleton
3. Gemini 연결과 RAG ingest
4. RAG chat API
5. 추천/일정 기능
6. React UI
7. 테스트, 보고서, 발표자료, 데모 영상

## 완료 기준

- 팀원이 README와 dev guide만 보고 로컬 실행을 시작할 수 있습니다.
- RAG 답변에 출처가 표시됩니다.
- 추천과 일정 기능이 Python 코드로 설명 가능합니다.
- LLM 활용 기록이 개발 과정과 함께 남아 있습니다.
- 발표 데모가 sample data로 재현 가능합니다.

