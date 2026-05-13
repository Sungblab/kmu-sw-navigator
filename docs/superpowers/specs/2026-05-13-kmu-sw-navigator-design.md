# kmu-sw-navigator Design

Status: approved for initial repo setup
Date: 2026-05-13
Owner: 김성빈

## 목표

국민대학교 소프트웨어융합대학 신입생이 학교생활, 커리큘럼, 트랙, 활동, 과제 일정을 쉽게 탐색할 수 있도록 돕는 RAG 기반 AI 웹앱을 만든다.

## 범위

MVP는 아래 기능으로 제한한다.

1. 국민대/소프트웨어학부 자료 기반 RAG 챗봇
2. 관심 분야 기반 트랙/활동 추천
3. 자연어 일정 입력과 D-day 관리
4. LLM 활용 기록 조회와 제출용 개발 기록

eCampus 자동 로그인, Google Calendar 완전 연동, 전체 학과 확장은 MVP 범위에서 제외한다.

## 아키텍처

```txt
React + Vite + TypeScript
-> FastAPI Python backend
-> Supabase Auth/Postgres/pgvector
-> Gemini API
```

FastAPI가 Gemini API Key와 Supabase service role key를 보유한다. 프론트엔드는 Supabase anon key와 FastAPI API base URL만 사용한다.

## 문서 운영

`docs/README.md`를 문서 인덱스로 사용한다. 작업은 spec, plan, implementation, verification, LLM usage log 순서로 남긴다. 이 구조는 제출물에서 LLM 활용 방식과 협업 과정을 설명하는 근거가 된다.

## 팀 운영

김성빈은 PM / 개발 리드로 전체 구조, repo 운영, 통합, 검증을 담당한다. 나머지 팀원의 역할은 실제 분담이 정해진 뒤 `docs/collaboration/team-roles.md`에 기록한다.

## 검증 기준

- 문서 체크가 통과한다.
- 백엔드 헬스체크가 동작한다.
- Supabase schema가 SQL Editor에서 실행 가능하다.
- RAG 답변은 출처를 포함한다.
- LLM 활용 기록이 개발 과정과 앱 사용 기록 양쪽에 남는다.
