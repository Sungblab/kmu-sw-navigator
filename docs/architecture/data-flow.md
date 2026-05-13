# 데이터 흐름

## 1. RAG 질문 답변 흐름

```txt
사용자 질문
-> React UI
-> FastAPI /api/chat
-> Gemini embedding 생성
-> Supabase pgvector RPC 검색
-> 관련 chunk 3-5개 선택
-> Gemini 답변 생성
-> chat_logs, llm_usage_logs 저장
-> 답변과 출처 반환
```

## 2. 문서 ingest 흐름

```txt
Markdown 자료
-> 파일별 metadata 확인
-> 500-1000자 chunk 분리
-> Gemini embedding 생성, 768차원
-> Supabase document_chunks 저장
-> 검색 테스트 질문으로 품질 확인
```

## 3. 추천 흐름

```txt
사용자 관심사 입력
-> FastAPI /api/recommend/*
-> Python 딕셔너리 규칙 조회
-> 조건문으로 추천 분기
-> 필요 시 Gemini로 설명 문장 보강
-> 추천 결과 반환
-> llm_usage_logs 저장
```

## 4. 일정 흐름

```txt
자연어 일정 입력
-> FastAPI /api/assignments/parse
-> Gemini Flash-Lite JSON 추출
-> 사용자 확인
-> FastAPI /api/assignments 저장
-> due_at 기준 D-day 계산
-> 일정 목록 반환
```

## 5. LLM 기록 흐름

앱 안에서 Gemini API를 사용한 기록은 DB의 `llm_usage_logs`에 저장합니다. 개발 과정에서 Codex, ChatGPT, Claude, Gemini를 사용한 기록은 `docs/llm/usage-log.md`에 남깁니다.

