# kmu-sw-navigator PRD & 개발 계획서

> 현재 프로젝트명: **kmu-sw-navigator**
> 제품 방향: **국민대학교 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터**
> 대상: 국민대학교 소프트웨어융합대학 학생. 신입생 지원은 핵심 사용 사례로 유지
> 개발 언어 핵심: **Python**  
> 제출 마감: **6월 11일**  
> 문서 버전: v1.1

---

## 0.2 2026-05-23 SaaS 완성도 재정렬 메모

현재 목표는 **Supabase Auth/Postgres와 Python FastAPI 백엔드가 실제로 연결된 SaaS형 개인화 학업 내비게이터**를 제출 수준까지 완성하는 것이다. 로컬 fallback은 발표 장애와 외부 키 누락에 대비한 안전장치일 뿐, 최종 완성 기준으로 쓰지 않는다.

이 재정렬 이후의 우선순위는 다음과 같다.

- Supabase schema, Auth, 사용자별 profile/memory/chat/assignment/LLM log 저장을 live smoke로 검증한다.
- Python 백엔드는 추천, RAG 근거 선택, 일정 파싱, 메모리 저장 정책처럼 발표에서 직접 설명해야 하는 핵심 로직을 담당한다.
- React 프론트엔드는 SaaS 사용자가 로그인하고, 입력하고, 결과와 근거를 확인하는 제품 UI로 유지한다.
- Gemini와 Google grounding은 답변 품질과 최신성 보강용이며, LLM이 임의로 만든 결과를 Python 판단 로직 대신 사용하지 않는다.
- 보고서와 발표는 “LLM을 도구로 사용해 직접 검토, 수정, 테스트한 Python 중심 웹서비스”라는 점을 증명한다.

완료 기준은 `pnpm verify:local` 통과에 더해, 가능한 live 항목은 `pnpm env:check:strict`, `pnpm supabase:smoke`, `pnpm supabase:login-smoke`, `pnpm supabase:llm-smoke`, Gemini smoke 결과로 남기는 것이다.

---

## 0.1 2026-05-13 범위 확장 메모

초기 PRD는 “소프트웨어융합대학/소프트웨어학부 신입생”을 주 대상으로 작성되었지만, 이후 설계 논의에서 제품 범위를 **소프트웨어융합대학 전체 학년을 위한 개인화 AI 내비게이터**로 확장했다. 신입생 지원은 핵심 사용 사례로 유지하되, 서비스는 학년별 학업, 진로/취업/창업, 프로젝트, 일정 관리를 함께 다룬다.

확장된 설계의 기준 문서는 `docs/superpowers/specs/2026-05-13-personalized-sw-navigator-design.md`다.

추가된 핵심 방향:

- 필수 프로필은 소속, 학년, 입학년도/적용 교과과정만 받는다.
- 관심 분야, 진로 고민, 수강 과목, 프로젝트 경험은 대화형 선택지와 직접 입력으로 메모리에 저장한다.
- 학교 내부 자료는 Mini LLM Wiki와 embedding RAG로 검색한다.
- 최신 진로/취업/창업 정보는 Google Search grounding으로 보강한다.
- 자연어 과제 등록, 앱 내부 일정 목록, D-day를 MVP 범위에 포함한다. Google Calendar 내보내기는 OAuth가 필요한 선택 확장 기능으로 두며, 제출 시연의 필수 흐름에서는 제외한다.

---

## 0. 최종 결정 요약

### 최종 주제

**국민대학교 소프트웨어융합대학 학생을 위한 SaaS형 개인화 RAG 학업 내비게이터**

소프트웨어융합대학 학생이 학업, 트랙, 진로/취업/창업, 프로젝트, 과제 일정을 한곳에서 관리할 수 있도록, Supabase Auth/Postgres와 Python FastAPI 백엔드가 연결된 도메인 특화 AI 웹앱을 개발한다. 신입생 지원은 핵심 라이브 시연 시나리오로 유지하되, 제품 구조는 로그인 사용자별 데이터가 저장되는 SaaS 형태를 목표로 한다.

### 최종 MVP 범위

이번 과제에서는 모든 학과 전체를 다루지 않고, **국민대학교 소프트웨어융합대학 또는 소프트웨어학부 중심 MVP**로 개발한다.

핵심 기능은 다음 네 가지다.

1. 국민대/학과 자료 기반 RAG 챗봇
2. 관심 분야 기반 트랙/커리큘럼 추천
3. 관심사 기반 동아리/활동 추천
4. 과제/일정 등록 및 D-day 관리

eCampus 자동 크롤링은 개발 시간이 많이 들고 인증/보안 이슈가 있으므로 향후 개선 기능으로 둔다. Google Calendar 연동은 foundation과 OAuth 경로를 구현했지만, 이번 제출의 핵심 시연은 앱 내부 일정 등록, 저장, D-day, 완료/삭제 흐름으로 진행한다.

---

## 1. 기술 스택 최종 결정

### Frontend

```txt
React + Vite + TypeScript
Tailwind CSS
lucide-react
Supabase JS Client
```

### Backend

```txt
FastAPI
Python
Pydantic
Uvicorn
google-genai
supabase-py
python-dotenv
```

### Auth

```txt
Supabase Auth
```

Better Auth는 좋은 선택지지만 TypeScript/Node 서버 중심이므로, FastAPI MVP에서는 구조가 복잡해진다. 따라서 이번 과제에서는 Supabase Auth를 사용한다.

### Database

```txt
Supabase Postgres
```

### Vector Search

```txt
Supabase pgvector
```

### LLM

```txt
메인 답변 모델: gemini-3-flash-preview
가벼운 작업 모델: gemini-3.1-flash-lite
고급 추론/백업 모델: gemini-3.1-pro-preview
임베딩 모델: gemini-embedding-2
임베딩 차원: 768
```

---

## 2. Gemini 모델 선택 기준

### 2.1 메인 답변 모델

```txt
gemini-3-flash-preview
```

사용 위치:

- RAG 기반 신입생 Q&A
- 커리큘럼/트랙 설명
- 사용자 질문에 대한 최종 자연어 답변 생성
- 출처 기반 답변 생성

선택 이유:

- Flash 계열이라 Pro보다 상대적으로 빠른 응답을 기대할 수 있다.
- 텍스트, 이미지, PDF 등 멀티모달 입력을 지원한다.
- 구조화 출력, function calling, thinking, 긴 context를 지원한다.
- MVP의 메인 챗봇 답변 품질과 속도 균형이 좋다.

주의점:

- `gemini-3-flash-preview`는 preview 모델이므로, 실제 구현 중 API 사용 가능 여부와 과금/제한을 확인해야 한다.
- 만약 제한이 있거나 오류가 나면 `gemini-3.1-flash-lite` 또는 stable Flash 계열로 교체 가능하게 `.env`에서 모델명을 관리한다.

### 2.2 가벼운 작업 모델

```txt
gemini-3.1-flash-lite
```

사용 위치:

- 일정 문장에서 제목/과목/마감일 JSON 추출
- 질문 분류
- 추천 유형 분류
- 간단 요약
- LLM 활용 로그 정리

선택 이유:

- 저지연/저비용 작업에 적합하다.
- 구조화 출력(JSON)에 사용할 수 있다.
- 일정 추출처럼 정형화된 작업에 충분하다.
- Stable 모델로 사용하기 좋다.

### 2.3 고급 추론 모델

```txt
gemini-3.1-pro-preview
```

사용 위치:

- 복잡한 커리큘럼 상담
- 여러 조건이 섞인 질문
- 발표/보고서용 고품질 요약 생성
- 메인 모델의 답변이 부족한 경우 선택적 fallback

선택 이유:

- 더 깊은 reasoning과 안정적인 복합 작업에 적합하다.
- 다만 과제 MVP에서는 비용과 속도를 고려해 기본값으로 쓰지 않는다.

### 2.4 임베딩 모델

```txt
gemini-embedding-2
```

사용 위치:

- 국민대/학과/동아리/신입생 안내 자료 chunk embedding
- 사용자 질문 embedding
- Supabase pgvector similarity search

설정:

```txt
output_dimensionality = 768
```

선택 이유:

- 기본 3072차원도 가능하지만, MVP에서는 저장공간과 속도를 고려해 768차원으로 축소한다.
- 768차원은 RAG 검색 품질과 비용/성능 균형이 좋다.
- Supabase pgvector 테이블도 `vector(768)`로 맞춘다.

---

## 3. 제품 개요

### 3.1 문제 정의

국민대 신입생은 입학 초기에 다음과 같은 문제를 겪는다.

- 학과 커리큘럼이 어떻게 구성되어 있는지 모른다.
- 어떤 트랙이나 진로 방향을 선택해야 할지 어렵다.
- 동아리, 학교생활, 학사 일정 정보를 찾기 번거롭다.
- eCampus, 종합정보시스템, 수강신청 등 학교 시스템에 익숙하지 않다.
- 과제 마감일과 수업 일정을 관리하기 어렵다.
- 학교 공식 문서나 안내 책자가 있어도 필요한 내용을 빠르게 찾기 어렵다.

### 3.2 해결 아이디어

국민대/학과/신입생 안내 자료를 문서 데이터로 저장하고, 사용자의 질문과 관련된 문서를 pgvector로 검색한 뒤, Gemini API가 검색 결과를 바탕으로 답변한다.

즉, 단순 일반 챗봇이 아니라 **국민대 소프트웨어융합대학 신입생 전용 RAG 기반 AI 도우미**를 만든다.

### 3.3 목표 사용자

1. 국민대학교 신입생
2. 소프트웨어융합대학/소프트웨어학부 신입생
3. 수강신청과 커리큘럼 선택에 어려움을 겪는 학생
4. 동아리/학교생활 정보를 찾고 싶은 학생
5. 과제와 일정을 한 곳에서 관리하고 싶은 학생

---

## 4. 핵심 가치 제안

### 4.1 일반 챗봇과의 차이

일반 Gemini에게 질문하면 국민대의 구체적인 학과 자료나 동아리 정보를 부정확하게 답할 수 있다. 이 프로젝트는 학교/학과 자료를 먼저 검색하고, 그 검색 결과를 근거로 답변하기 때문에 더 도메인에 맞는 답변을 제공한다.

### 4.2 사용자 입장에서 얻는 가치

- 신입생이 궁금한 내용을 자연어로 질문할 수 있다.
- 커리큘럼과 트랙 정보를 쉽게 이해할 수 있다.
- 관심사에 맞는 동아리나 활동을 추천받을 수 있다.
- 과제와 일정을 자연어로 등록하고 D-day를 확인할 수 있다.
- 답변 근거가 되는 자료 출처를 확인할 수 있다.

---

## 5. 기능 요구사항

## 5.1 인증 기능

### 기능 설명

사용자는 Supabase Auth를 이용해 이메일/비밀번호 방식으로 로그인한다.

### 사용자 흐름

1. 사용자가 회원가입
2. 이메일/비밀번호로 로그인
3. Supabase에서 access token 발급
4. React가 FastAPI 요청 시 `Authorization: Bearer <token>` 헤더 추가
5. FastAPI가 토큰을 검증하고 사용자별 데이터 처리

### MVP 기준

- 이메일/비밀번호 로그인
- 로그아웃
- 로그인 상태 유지
- 비로그인 사용자의 주요 API 접근 제한

---

## 5.2 RAG 기반 챗봇

### 기능 설명

사용자가 질문을 입력하면, 시스템은 질문과 관련된 문서 chunk를 Supabase pgvector에서 검색하고, Gemini API가 검색된 context를 바탕으로 답변을 생성한다.

### 예시 질문

```txt
AI 쪽 관심 있는데 어떤 트랙을 보면 좋아?
소프트웨어학부 1학년은 어떤 과목을 중요하게 봐야 해?
동아리 추천해줘. 나는 운동이랑 개발 둘 다 관심 있어.
신입생이 처음에 알아야 할 학교 시스템 알려줘.
수강신청할 때 주의할 점 알려줘.
```

### 입력

```json
{
  "question": "AI에 관심 있으면 어떤 트랙이 좋아?"
}
```

### 출력

```json
{
  "answer": "AI와 데이터 분석에 관심이 있다면 빅데이터/머신러닝 관련 트랙을 우선적으로 살펴보는 것을 추천합니다...",
  "sources": [
    {
      "title": "소프트웨어학부 교과과정",
      "category": "curriculum",
      "similarity": 0.82
    }
  ]
}
```

### 내부 처리 흐름

```txt
사용자 질문
↓
Gemini Embedding 생성
↓
Supabase pgvector 유사도 검색
↓
상위 문서 chunk 3~5개 추출
↓
Gemini 3 Flash에 context + question 전달
↓
출처 포함 답변 반환
↓
chat_logs / llm_usage_logs 저장
```

---

## 5.3 트랙/커리큘럼 추천 기능

### 기능 설명

사용자가 관심 분야, 목표, 코딩 경험, 선호 학습 방식을 입력하면 조건문과 딕셔너리 기반으로 추천 트랙과 학습 방향을 제시한다.

### 입력 예시

```json
{
  "interest": "AI",
  "goal": "취업",
  "coding_level": "초급",
  "preference": "프로젝트"
}
```

### 출력 예시

```json
{
  "recommended_track": "빅데이터/머신러닝",
  "reason": "AI와 데이터 분석에 관심이 있고 프로젝트 기반 학습을 선호하므로...",
  "recommended_actions": [
    "Python 기초를 먼저 다지기",
    "수학/통계 관련 기초 과목 챙기기",
    "AI 관련 동아리나 스터디 탐색하기"
  ]
}
```

### 과제 조건 연결

이 기능은 다음 조건을 충족한다.

- 사용자 입력
- 조건문
- 함수
- 딕셔너리
- 리스트
- 의미 있는 결과 출력

---

## 5.4 동아리/활동 추천 기능

### 기능 설명

사용자의 관심사를 기반으로 학교 동아리 또는 추천 활동 유형을 안내한다.

### 입력 예시

```json
{
  "interests": ["개발", "운동", "친목"],
  "activity_style": "팀 활동 선호"
}
```

### 출력 예시

```json
{
  "recommendations": [
    {
      "type": "개발/IT",
      "reason": "개발에 관심이 있으므로 프로젝트형 개발 동아리나 스터디를 추천합니다."
    },
    {
      "type": "운동",
      "reason": "운동과 친목을 함께 원한다면 스포츠 동아리도 적합합니다."
    }
  ]
}
```

---

## 5.5 과제/일정 관리 기능

### 기능 설명

사용자가 자연어로 과제나 일정을 입력하면 Gemini가 일정 정보를 JSON으로 추출하고, FastAPI가 Supabase에 저장한다.

### 입력 예시

```txt
자료구조 과제 다음주 금요일 밤 11시 59분까지 제출해야 해
```

### Gemini 추출 결과 예시

```json
{
  "title": "자료구조 과제",
  "course": "자료구조",
  "due_at": "2026-05-22T23:59:00+09:00",
  "type": "assignment",
  "memo": "제출 필요"
}
```

### 출력 예시

```json
{
  "message": "일정이 등록되었습니다.",
  "assignment": {
    "title": "자료구조 과제",
    "course": "자료구조",
    "due_at": "2026-05-22T23:59:00+09:00",
    "dday": 9
  }
}
```

### 주요 기능

- 일정 등록
- 일정 목록 조회
- D-day 계산
- 마감 임박 일정 표시
- 상태 변경: todo / done

---

## 5.6 LLM 활용 기록 자동 저장

### 기능 설명

과제 요구사항에 맞춰 LLM을 어떤 목적으로 사용했는지 기록한다.

### 저장 항목

- 사용 기능
- 사용자 입력
- 모델명
- 출력 결과
- 활용 목적
- 생성 시간

### 예시

```json
{
  "feature": "rag_chat",
  "model": "gemini-3-flash-preview",
  "purpose": "국민대 자료 기반 신입생 질문 답변 생성",
  "input_text": "AI 관심 있으면 어떤 트랙이 좋아?",
  "output_text": "AI와 데이터 분석에 관심이 있다면..."
}
```

---

## 6. 비기능 요구사항

### 6.1 성능

- 일반 질문 응답 시간: 3~8초 이내 목표
- 일정 추출: 1~3초 이내 목표
- RAG 검색 chunk 수: 기본 5개
- 문서 chunk 크기: 500~1000자 내외

### 6.2 보안

- Gemini API Key는 프론트엔드에 노출하지 않는다.
- Supabase service role key는 FastAPI 서버에서만 사용한다.
- 프론트엔드에는 Supabase anon key만 사용한다.
- 사용자별 데이터는 Supabase Auth user id 기준으로 분리한다.

### 6.3 안정성

- Gemini API 실패 시 에러 메시지를 사용자에게 반환한다.
- RAG 검색 결과가 부족하면 “자료에서 충분한 근거를 찾지 못했다”고 답한다.
- 발표 전 live RAG seed와 공식 출처 기반 질문 세트를 미리 준비한다.

### 6.4 확장성

- 향후 다른 학과 자료를 추가할 수 있도록 `category`, `department`, `source` 필드를 둔다.
- Google Calendar 연동은 별도 모듈로 확장 가능하게 설계하되, 제출 필수 기능은 앱 내부 일정 관리로 한정한다.
- eCampus 연동은 보안 이슈를 고려해 향후 기능으로 분리한다.

---

## 7. 시스템 아키텍처

```txt
[React + Vite + TypeScript]
  ├─ Supabase Auth 로그인
  ├─ 챗봇 UI
  ├─ 추천 UI
  └─ 일정 관리 UI

        ↓ Authorization: Bearer <Supabase Access Token>

[FastAPI Backend]
  ├─ Auth Middleware
  ├─ RAG Service
  ├─ Gemini Service
  ├─ Recommendation Service
  ├─ Schedule Service
  └─ Log Service

        ↓

[Supabase]
  ├─ Auth
  ├─ Postgres
  ├─ pgvector
  ├─ document_chunks
  ├─ assignments
  ├─ chat_logs
  └─ llm_usage_logs

        ↓

[Gemini API]
  ├─ gemini-3-flash-preview
  ├─ gemini-3.1-flash-lite
  ├─ gemini-3.1-pro-preview
  └─ gemini-embedding-2
```

---

## 8. 데이터 설계

## 8.1 Supabase extension

```sql
create extension if not exists vector;
```

---

## 8.2 profiles

Supabase Auth의 `auth.users`와 연결되는 사용자 프로필 테이블이다.

```sql
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  student_id text,
  department text default '소프트웨어융합대학',
  major text,
  created_at timestamp with time zone default now()
);
```

---

## 8.3 document_chunks

RAG 검색 대상 문서 chunk를 저장한다.

```sql
create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source text,
  category text,
  department text default '소프트웨어융합대학',
  content text not null,
  embedding vector(768),
  created_at timestamp with time zone default now()
);
```

### category 예시

```txt
curriculum
track
club
freshman_guide
school_system
course_registration
faq
```

---

## 8.4 assignments

사용자별 과제/일정 저장 테이블이다.

```sql
create table assignments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  course text,
  due_at timestamp with time zone not null,
  memo text,
  status text default 'todo',
  created_at timestamp with time zone default now()
);
```

---

## 8.5 chat_logs

사용자 질문과 AI 답변을 저장한다.

```sql
create table chat_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  question text not null,
  answer text not null,
  sources jsonb,
  created_at timestamp with time zone default now()
);
```

---

## 8.6 llm_usage_logs

LLM 활용 기록을 저장한다.

```sql
create table llm_usage_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  feature text not null,
  input_text text not null,
  output_text text,
  model text,
  purpose text,
  created_at timestamp with time zone default now()
);
```

---

## 8.7 pgvector 검색 함수

```sql
create or replace function match_document_chunks (
  query_embedding vector(768),
  match_count int default 5
)
returns table (
  id uuid,
  title text,
  source text,
  category text,
  content text,
  similarity float
)
language sql stable
as $$
  select
    document_chunks.id,
    document_chunks.title,
    document_chunks.source,
    document_chunks.category,
    document_chunks.content,
    1 - (document_chunks.embedding <=> query_embedding) as similarity
  from document_chunks
  order by document_chunks.embedding <=> query_embedding
  limit match_count;
$$;
```

---

## 9. API 설계

## 9.1 Auth

인증은 Supabase Auth가 담당한다. FastAPI는 프론트엔드에서 전달받은 Supabase JWT를 검증한다.

### 요청 헤더

```txt
Authorization: Bearer <supabase_access_token>
```

---

## 9.2 POST /api/chat

RAG 기반 질문 답변 API.

### Request

```json
{
  "question": "AI에 관심 있으면 어떤 트랙이 좋아?"
}
```

### Response

```json
{
  "answer": "AI와 데이터 분석에 관심이 있다면...",
  "sources": [
    {
      "title": "소프트웨어학부 교과과정",
      "source": "kmu_sw_curriculum",
      "category": "curriculum",
      "similarity": 0.82
    }
  ]
}
```

---

## 9.3 POST /api/recommend/track

트랙 추천 API.

### Request

```json
{
  "interest": "AI",
  "goal": "취업",
  "coding_level": "초급",
  "preference": "프로젝트"
}
```

### Response

```json
{
  "recommended_track": "빅데이터/머신러닝",
  "reason": "AI와 데이터 분석에 관심이 있으므로...",
  "actions": [
    "Python 기초 학습",
    "수학/통계 기초 보강",
    "AI 관련 프로젝트 경험 쌓기"
  ]
}
```

---

## 9.4 POST /api/recommend/activity

동아리/활동 추천 API.

### Request

```json
{
  "interests": ["개발", "운동", "친목"],
  "activity_style": "팀 활동"
}
```

### Response

```json
{
  "recommendations": [
    {
      "category": "개발/IT",
      "reason": "개발 프로젝트 경험을 쌓기 좋습니다."
    },
    {
      "category": "운동",
      "reason": "친목과 건강 관리를 함께 할 수 있습니다."
    }
  ]
}
```

---

## 9.5 POST /api/assignments/preview

자연어 일정 추출 API.

### Request

```json
{
  "text": "자료구조 과제 다음주 금요일 밤 11시 59분까지 제출"
}
```

### Response

```json
{
  "title": "자료구조 과제",
  "course": "자료구조",
  "due_at": "2026-05-22T23:59:00+09:00",
  "memo": "제출"
}
```

---

## 9.6 POST /api/assignments

일정 저장 API.

### Request

```json
{
  "title": "자료구조 과제",
  "course": "자료구조",
  "due_at": "2026-05-22T23:59:00+09:00",
  "memo": "제출"
}
```

### Response

```json
{
  "message": "일정이 등록되었습니다.",
  "id": "uuid",
  "dday": 9
}
```

---

## 9.7 GET /api/assignments

일정 목록 조회 API.

### Response

```json
{
  "assignments": [
    {
      "id": "uuid",
      "title": "자료구조 과제",
      "course": "자료구조",
      "due_at": "2026-05-22T23:59:00+09:00",
      "status": "todo",
      "dday": 9
    }
  ]
}
```

---

## 9.8 PATCH /api/assignments/{assignment_id}

일정 상태 수정 API.

### Request

```json
{
  "status": "done"
}
```

---

## 9.9 GET /api/llm-logs

LLM 활용 기록 조회 API.

### Response

```json
{
  "logs": [
    {
      "feature": "rag_chat",
      "model": "gemini-3-flash-preview",
      "purpose": "국민대 자료 기반 답변 생성",
      "created_at": "2026-05-13T12:00:00+09:00"
    }
  ]
}
```

---

## 10. 프론트엔드 화면 설계

## 10.1 Login Page

### 요소

- 이메일 입력
- 비밀번호 입력
- 로그인 버튼
- 회원가입 버튼
- 에러 메시지

---

## 10.2 Main App Layout

### 탭 구성

```txt
[AI 챗봇] [트랙 추천] [동아리 추천] [일정 관리] [LLM 기록]
```

라우터를 쓰면 다음 경로로 구성한다.

```txt
/login
/app/chat
/app/recommend-track
/app/recommend-club
/app/schedule
/app/logs
```

---

## 10.3 Chat Page

### 요소

- 질문 입력창
- 전송 버튼
- 답변 카드
- 출처 카드
- “근거 자료 부족” 표시

### 라이브 질문 버튼

```txt
AI 관심 있으면 어떤 트랙이 좋아?
수강신청 전에 뭘 확인해야 해?
신입생이 처음 알아야 할 학교 시스템 알려줘.
동아리 추천해줘.
```

---

## 10.4 Track Recommend Page

### 입력

- 관심 분야
- 목표
- 코딩 경험
- 학습 성향

### 출력

- 추천 트랙
- 추천 이유
- 추천 액션 리스트

---

## 10.5 Club Recommend Page

### 입력

- 관심사 체크박스
- 활동 성향
- 원하는 분위기

### 출력

- 추천 활동 카테고리
- 추천 이유
- RAG 기반 참고 자료

---

## 10.6 Schedule Page

### 요소

- 자연어 일정 입력창
- 일정 추출 결과 미리보기
- 저장 버튼
- 일정 리스트
- D-day 뱃지
- 완료 처리 버튼

---

## 10.7 LLM Logs Page

### 요소

- 사용 기능
- 모델명
- 활용 목적
- 시간
- 입력/출력 요약

보고서에 넣을 LLM 활용 기록을 캡처하기 좋다.

---

## 11. 백엔드 폴더 구조

```txt
backend/
  app/
    main.py

    api/
      chat.py
      recommend.py
      assignments.py
      logs.py

    core/
      config.py
      security.py

    services/
      gemini_service.py
      embedding_service.py
      rag_service.py
      recommend_service.py
      assignment_service.py
      log_service.py

    db/
      supabase_client.py

    schemas/
      chat.py
      recommend.py
      assignment.py
      logs.py

    data/
      kmu_sw_curriculum.md
      kmu_sw_tracks.md
      kmu_clubs.md
      freshman_guide.md

    scripts/
      ingest_documents.py
      seed_initial_data.py

  requirements.txt
  .env.example
```

---

## 12. 프론트엔드 폴더 구조

```txt
frontend/
  src/
    main.tsx
    App.tsx

    lib/
      supabase.ts
      api.ts

    pages/
      LoginPage.tsx
      ChatPage.tsx
      TrackRecommendPage.tsx
      ClubRecommendPage.tsx
      SchedulePage.tsx
      LogsPage.tsx

    components/
      AppLayout.tsx
      ChatMessage.tsx
      SourceCard.tsx
      AssignmentCard.tsx
      DdayBadge.tsx

    types/
      api.ts

  package.json
  .env.example
```

---

## 13. 환경변수 설계

## 13.1 Backend .env

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=

GEMINI_API_KEY=

GEMINI_MAIN_MODEL=gemini-3-flash-preview
GEMINI_SCHEDULE_MODEL=gemini-3.1-flash-lite
GEMINI_LIGHT_MODEL=gemini-3.1-flash-lite
GEMINI_PRO_MODEL=gemini-3.1-pro-preview
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
GEMINI_EMBEDDING_DIM=768

FRONTEND_ORIGIN=http://localhost:5173
```

## 13.2 Frontend .env

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=http://localhost:8000
```

---

## 14. 핵심 로직 의사코드

## 14.1 RAG 답변 생성

```python
def answer_question(user_id: str, question: str):
    query_embedding = create_embedding(question)

    chunks = match_document_chunks(
        query_embedding=query_embedding,
        match_count=5
    )

    if not chunks:
        return "관련 자료를 찾지 못했습니다."

    context = build_context(chunks)

    answer = generate_answer_with_gemini(
        question=question,
        context=context
    )

    save_chat_log(user_id, question, answer, chunks)
    save_llm_usage_log(
        user_id=user_id,
        feature="rag_chat",
        input_text=question,
        output_text=answer,
        model="gemini-3-flash-preview",
        purpose="국민대 자료 기반 질문 답변 생성"
    )

    return answer
```

---

## 14.2 트랙 추천

```python
TRACK_RULES = {
    "AI": {
        "track": "빅데이터/머신러닝",
        "actions": ["Python 기초 학습", "수학/통계 기초 보강", "AI 프로젝트 경험 쌓기"]
    },
    "보안": {
        "track": "웹·정보보호",
        "actions": ["네트워크 기초 학습", "웹 기초 학습", "보안 동아리/스터디 탐색"]
    },
    "IoT": {
        "track": "IoT융합",
        "actions": ["임베디드 기초 학습", "센서/하드웨어 프로젝트 경험"]
    }
}

def recommend_track(interest, goal, coding_level, preference):
    if interest in TRACK_RULES:
        result = TRACK_RULES[interest]
    else:
        result = {
            "track": "기초 전공 탐색",
            "actions": ["프로그래밍 기초", "전공 소개 자료 확인", "관심 분야 탐색"]
        }

    return result
```

---

## 14.3 D-day 계산

```python
from datetime import datetime

def calculate_dday(due_at: datetime):
    now = datetime.now(due_at.tzinfo)
    diff = due_at - now
    return diff.days
```

---

## 15. 문서 수집 계획

### 15.1 수집할 자료

1. 국민대학교 소프트웨어학부/소프트웨어융합대학 교과과정
2. 트랙 소개 자료
3. 신입생 안내 자료
4. 수강신청 관련 안내 자료
5. 동아리 목록/활동 자료
6. 학교 시스템 안내 자료
7. 자주 묻는 질문 직접 작성

### 15.2 데이터 파일 예시

```txt
kmu_sw_curriculum.md
kmu_sw_tracks.md
kmu_clubs.md
freshman_guide.md
course_registration_guide.md
school_system_guide.md
```

### 15.3 chunking 기준

- 문서 제목과 category를 metadata로 저장
- 500~1000자 단위로 chunk 분리
- chunk마다 embedding 생성
- Supabase `document_chunks`에 저장

---

## 16. 개발 일정

## 16.1 전체 일정

제출 마감이 6월 11일이므로, 5월 중순부터 개발한다고 가정한다.

```txt
1주차: 기획 확정, DB 설계, Supabase 설정
2주차: FastAPI + Gemini + pgvector RAG 구현
3주차: React UI 구현, Auth 연결
4주차: 추천/일정 기능 구현, LLM 로그 저장
5주차: 테스트, 발표자료, 보고서, 발표영상 제작
```

---

## 16.2 세부 개발 계획

### Phase 1. 프로젝트 세팅

기간: 1~2일

작업:

- GitHub repository 생성
- frontend/backend 폴더 구성
- React + Vite 세팅
- FastAPI 세팅
- Supabase 프로젝트 생성
- 환경변수 구성
- 기본 README 작성

완료 기준:

- 프론트 로컬 실행 가능
- 백엔드 로컬 실행 가능
- `/health` API 응답 가능

---

### Phase 2. Supabase DB/Auth 세팅

기간: 1~2일

작업:

- Supabase Auth 이메일 로그인 활성화
- profiles 테이블 생성
- assignments 테이블 생성
- chat_logs 테이블 생성
- llm_usage_logs 테이블 생성
- document_chunks 테이블 생성
- pgvector extension 활성화
- match function 생성

완료 기준:

- Supabase Auth 로그인 가능
- DB insert/select 가능
- pgvector 검색 함수 실행 가능

---

### Phase 3. Gemini API 연결

기간: 1일

작업:

- `google-genai` 설치
- Gemini API key 설정
- main model 호출 함수 작성
- light model 호출 함수 작성
- embedding 생성 함수 작성

완료 기준:

- 질문을 보내면 Gemini 응답 반환
- 텍스트를 보내면 768차원 embedding 반환

---

### Phase 4. RAG ingest 구현

기간: 2~3일

작업:

- markdown/txt 문서 로더 작성
- chunking 함수 작성
- embedding 생성
- Supabase document_chunks insert
- seed script 작성

완료 기준:

- 국민대 관련 sample 문서 30개 이상 chunk 저장
- 검색 질문에 대해 관련 chunk가 반환됨

---

### Phase 5. RAG Chat API 구현

기간: 2~3일

작업:

- `/api/chat` 구현
- JWT 검증
- embedding 생성
- pgvector RPC 호출
- Gemini 답변 생성
- chat_logs 저장
- llm_usage_logs 저장

완료 기준:

- 로그인한 사용자가 질문 가능
- 답변과 출처가 함께 반환됨
- 로그가 DB에 저장됨

---

### Phase 6. 추천 기능 구현

기간: 1~2일

작업:

- 트랙 추천 규칙 작성
- 동아리 추천 규칙 작성
- 추천 API 구현
- 추천 결과를 Gemini로 자연스럽게 설명하는 기능 추가

완료 기준:

- 관심 분야 입력 시 추천 결과 반환
- 조건문/딕셔너리/리스트/함수 사용 흔적 명확

---

### Phase 7. 일정 관리 구현

기간: 2~3일

작업:

- 자연어 일정 추출 프롬프트 작성
- JSON schema 응답 처리
- 일정 저장 API 구현
- 일정 목록 API 구현
- D-day 계산 구현
- 상태 변경 API 구현

완료 기준:

- “자료구조 과제 다음주 금요일 23:59까지” 입력 시 일정 정보 추출
- 저장 후 목록에서 D-day 표시

---

### Phase 8. React UI 구현

기간: 3~5일

작업:

- Login Page
- App Layout
- Chat Page
- Track Recommend Page
- Club Recommend Page
- Schedule Page
- Logs Page
- Tailwind CSS 기반 카드, 버튼, input 적용

완료 기준:

- 사용자가 웹에서 모든 MVP 기능 사용 가능
- 발표 시연 가능한 UI 완성

---

### Phase 9. 테스트 및 발표 준비

기간: 5~7일

작업:

- 라이브 시연 시나리오 작성
- 예시 질문 준비
- 오류 처리 보완
- 보고서 6~10페이지 작성
- 발표자료 제작
- 20~25분 발표영상 녹화

완료 기준:

- 제출물 4종 준비 완료
- 라이브 시연 중 API 오류 대비 백업 데이터 준비

---

## 17. 발표영상 구성안: 20~25분

### 1. 주제 소개: 2분

- 프로젝트명 소개
- 국민대 신입생 정보 탐색 문제 설명
- 왜 RAG가 필요한지 설명

### 2. 문제 정의: 3분

- 신입생이 어려워하는 것
- 수강신청/커리큘럼/동아리/학교 시스템/과제 관리 문제
- 일반 챗봇의 한계

### 3. 시스템 구조 설명: 4분

- React
- FastAPI
- Supabase Auth
- Supabase Postgres + pgvector
- Gemini API
- RAG 흐름

### 4. 라이브 기능 시연: 8~10분

추천 시연 순서:

1. 로그인
2. RAG 챗봇 질문
3. 출처 확인
4. 트랙 추천
5. 동아리 추천
6. 자연어 일정 입력
7. D-day 확인
8. LLM 활용 기록 확인

### 5. 코드 구조 설명: 4분

- `main.py`
- `rag_service.py`
- `gemini_service.py`
- `recommend_service.py`
- `assignment_service.py`
- React page 구조
- DB 테이블 설명

### 6. 과제 조건 충족 설명: 2분

- Python 사용
- 사용자 입력
- 조건문
- 반복문
- 함수
- 리스트/딕셔너리
- 의미 있는 출력
- LLM 활용 기록

### 7. 한계 및 개선 방향: 2분

- 현재는 소프트웨어융합대학 중심
- 자료 최신화 필요
- Google Calendar 연동 가능
- eCampus 자동 연동은 보안 검토 필요
- 전체 학과 확장 가능

---

## 18. 최종보고서 구성: 6~10페이지

### 1. 프로젝트 개요

- 프로젝트명
- 개발 배경
- 대상 사용자
- 문제 정의

### 2. 개발 목적

- 신입생 정보 탐색 문제 해결
- 도메인 특화 RAG 챗봇 구현
- 일정 관리와 추천 기능 제공

### 3. 기술 스택

- React
- FastAPI
- Supabase Auth
- Supabase Postgres
- pgvector
- Gemini API

### 4. 주요 기능

- RAG 챗봇
- 트랙 추천
- 동아리 추천
- 일정 관리
- LLM 활용 기록

### 5. 시스템 구조

- 전체 아키텍처 그림
- API 흐름
- DB 구조

### 6. 코드 구조 및 주요 코드 설명

전체 코드를 붙여넣지 말고 주요 부분만 설명한다.

- 사용자 입력 처리
- 조건문 기반 추천
- 문서 검색 함수
- Gemini 호출 함수
- D-day 계산 함수
- 로그 저장 함수

### 7. 실행 결과

- 로그인 화면
- 챗봇 질문/답변
- 추천 결과
- 일정 등록 결과
- LLM 활용 기록 화면

### 8. LLM 활용 방식

- Gemini API 사용 위치
- ChatGPT/LLM을 개발 보조로 사용한 방식
- 직접 수정/테스트한 내용

### 9. 한계 및 개선 방향

- 자료 범위 한계
- 다른 학과 확장
- eCampus/Calendar 연동
- 검색 품질 개선

---

## 19. 과제 조건 충족 매핑

| 과제 조건 | 프로젝트에서 충족하는 방식 |
|---|---|
| 언어는 Python | FastAPI 백엔드, RAG, Gemini 호출, 일정 계산을 Python으로 구현 |
| 사용자 입력 | 질문, 관심 분야, 일정 자연어 입력 |
| 조건문 | 관심 분야별 트랙/동아리 추천 |
| 반복문 | 문서 chunk 처리, 일정 목록 처리, 로그 목록 처리 |
| 함수 | RAG 검색, Gemini 호출, 추천, D-day 계산 함수 |
| 리스트/딕셔너리 | 추천 규칙, 문서 목록, 일정 목록, sources |
| 의미 있는 처리 결과 | 답변, 추천, 일정 D-day, 로그 출력 |
| 실행 가능한 코드 | React + FastAPI 로컬 실행 |
| LLM 활용 기록 | llm_usage_logs 테이블과 Logs Page 제공 |

---

## 20. LLM 활용 기록 예시

```txt
LLM 활용 기록

1. 활용 도구
- ChatGPT: 프로젝트 주제 구체화, PRD 작성, 코드 구조 설계, 오류 해결 보조
- Gemini API: 사용자 질문 답변 생성, 일정 정보 추출, RAG 기반 답변 생성

2. 활용 목적
- RAG 구조 설계 참고
- FastAPI/Supabase/pgvector 구현 방법 정리
- 자연어 일정 추출 프롬프트 작성
- 발표자료와 보고서 문장 정리

3. 직접 수행한 부분
- 프로젝트 주제 선정
- 국민대 관련 자료 수집
- Supabase DB 설계 및 SQL 작성
- FastAPI API 구현
- React UI 구현
- Gemini 응답 검토 및 수정
- 테스트 및 발표 시연 구성

4. 주의한 점
- LLM 활용 목적과 직접 확인한 내용을 기록하고 테스트함
- 제출 코드의 주요 함수와 동작 원리를 직접 설명할 수 있도록 정리함
- LLM이 생성한 답변은 국민대 자료 기반 검색 결과와 함께 검토함
```

---

## 21. 리스크 및 대응 전략

### 21.1 Gemini API 오류

대응:

- `.env`로 모델명 교체 가능하게 설계
- 메인 모델 실패 시 lite 모델로 fallback
- live smoke 결과와 장애 시 설명할 검증 캡처 준비

### 21.2 RAG 검색 품질 낮음

대응:

- chunk 크기 조절
- 문서 제목/category metadata 추가
- 검색 결과 5개 이상 확보
- 질문 예시를 라이브 시연 전에 테스트

### 21.3 Supabase Auth/JWT 검증 문제

대응:

- 초반에는 로그인 없이 개발
- 핵심 기능 완성 후 Auth 붙이기
- 토큰 검증이 어려우면 Supabase `get_user` API 방식 사용

### 21.4 일정 날짜 파싱 오류

대응:

- Gemini structured output 사용
- 날짜 기준 timezone을 Asia/Seoul로 고정
- 추출 결과를 저장 전에 사용자에게 미리보기

### 21.5 개발 범위 과다

대응:

- eCampus 크롤링 제외
- Google Calendar 연동 제외 또는 선택 기능화
- 모든 학과 확장 제외
- 소프트웨어융합대학 중심으로 범위 제한

---

## 22. 구현 우선순위

### Must Have

- Supabase Auth 로그인
- RAG 챗봇
- pgvector 검색
- Gemini 답변 생성
- 트랙 추천
- 일정 등록/D-day
- LLM 활용 기록 저장

### Should Have

- 동아리 추천
- 출처 표시
- 로그 조회 화면
- 문서 ingest script

### Could Have

- Google Calendar 연동은 선택 확장 기능
- PDF 업로드 후 자동 ingest
- 관리자용 문서 관리 페이지
- 모델 라우팅 기능

### Won't Have in MVP

- eCampus 로그인 크롤링
- 전체 학과 지원
- 자동 수강신청 최적화
- 모바일 앱
- 실시간 학교 공지 크롤링

---

## 23. 라이브 시연 시나리오

### 라이브 시연 1. 로그인

1. 사용자가 이메일로 로그인한다.
2. 메인 대시보드로 이동한다.

### 라이브 시연 2. RAG 챗봇

질문:

```txt
AI에 관심이 많은 신입생인데 어떤 트랙을 보면 좋을까?
```

예상 결과:

- 관련 커리큘럼/트랙 문서 검색
- AI/데이터 관련 트랙 추천
- 출처 카드 표시

### 라이브 시연 3. 수강신청 질문

질문:

```txt
신입생이 첫 수강신청 전에 뭘 확인해야 해?
```

예상 결과:

- 신입생 안내 자료 기반 답변
- 체크리스트 형태 출력

### 라이브 시연 4. 동아리 추천

입력:

```txt
관심사: 개발, 운동, 친목
활동 성향: 팀 활동 선호
```

예상 결과:

- 개발/IT 활동 추천
- 운동 동아리 유형 추천
- 친목 활동 추천

### 라이브 시연 5. 일정 등록

입력:

```txt
자료구조 과제 다음주 금요일 밤 11시 59분까지 제출해야 해
```

예상 결과:

- Gemini가 일정 JSON 추출
- 사용자가 확인 후 저장
- 일정 목록에 D-day 표시

### 라이브 시연 6. LLM 활용 기록

- 사용한 기능
- 모델명
- 활용 목적
- 입력/출력 요약 확인

---

## 24. README 구성

```md
# kmu-sw-navigator

국민대학교 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터입니다.

## Features

- Supabase Auth 기반 로그인
- 국민대/학과 자료 기반 RAG 챗봇
- 관심 분야 기반 트랙 추천
- 동아리/활동 추천
- 자연어 과제 일정 등록
- D-day 계산
- LLM 활용 기록 저장

## Tech Stack

- React + Vite + TypeScript
- FastAPI
- Supabase Auth
- Supabase Postgres
- Supabase pgvector
- Gemini API

## Run Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Frontend

```bash
pnpm install
pnpm dev:frontend
```
```

---

## 25. 참고 자료

- Google AI Gemini API Models: https://ai.google.dev/gemini-api/docs/models
- Gemini 3 Flash Preview: https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview
- Gemini 3.1 Flash-Lite: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite
- Gemini 3.1 Pro Preview: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- Gemini Embeddings: https://ai.google.dev/gemini-api/docs/embeddings
- Supabase Auth: https://supabase.com/docs/guides/auth
- Supabase JWT: https://supabase.com/docs/guides/auth/jwts
- Supabase Vector Columns: https://supabase.com/docs/guides/ai/vector-columns
- Supabase pgvector: https://supabase.com/docs/guides/database/extensions/pgvector
- FastAPI: https://fastapi.tiangolo.com/

---

## 26. 최종 한 줄 정리

이 프로젝트는 **React + FastAPI + Supabase Auth/Postgres/pgvector + Gemini API**를 사용해, 국민대학교 소프트웨어융합대학 신입생이 학교생활, 커리큘럼, 동아리, 과제 일정을 쉽게 관리할 수 있도록 돕는 **RAG 기반 도메인 특화 AI 도우미**를 구현하는 프로젝트다.
