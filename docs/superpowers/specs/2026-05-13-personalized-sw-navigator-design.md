# Personalized SW Navigator Design

## 1. 결정 요약

이 프로젝트의 제품 범위는 “신입생 전용 RAG 챗봇”에서 “국민대학교 소프트웨어융합대학 전체 학년을 위한 개인화 AI 내비게이터”로 확장한다. 레포 이름은 당장 바꾸지 않고, 구현과 문서가 안정된 뒤 `kmu-sw-navigator` 같은 이름으로 변경할 수 있게 둔다.

서비스의 핵심은 다음 세 가지 근거를 함께 사용하는 것이다.

1. 사용자의 기본 프로필과 대화형 메모리
2. 학교/학과 자료를 정리한 Mini LLM Wiki와 embedding RAG
3. 진로, 취업, 창업, 기술 트렌드처럼 최신성이 필요한 정보에 대한 Google Search grounding

MVP는 모든 기능을 완벽하게 만들기보다, “개인화 상담 → 근거 기반 답변 → 일정 등록 → Calendar 내보내기 → LLM 사용 기록”이 하나의 데모 흐름으로 이어지게 만든다.

## 2. 대상 사용자

기본 대상은 국민대학교 소프트웨어융합대학 학생 전체다.

| 사용자 | 주요 고민 | 제공 가치 |
| --- | --- | --- |
| 1학년 | 학교 적응, 전공 기초, 동아리, 수강신청 | 학업 로드맵과 학교생활 안내 |
| 2학년 | 트랙 탐색, 프로젝트 시작, 전공 방향 | 관심 분야별 과목/활동 추천 |
| 3학년 | 인턴, 포트폴리오, 연구실, 캡스톤 | 진로/프로젝트/취업 준비 상담 |
| 4학년 | 취업, 대학원, 창업, 졸업 준비 | 최신 진로 정보와 실행 계획 |

보고서와 데모에서는 “소프트웨어융합대학 학생 전용 도메인 특화 AI”로 설명한다. 신입생 지원은 이 서비스의 주요 사용 사례 중 하나로 유지한다.

## 3. 온보딩과 프로필

초기 설정은 필수 정보만 받는다.

| 필드 | 값 |
| --- | --- |
| 소속 | 소프트웨어학부, 인공지능학부, 아직 잘 모름/기타 |
| 학년 | 1, 2, 3, 4 |
| 입학년도/적용 교과과정 | 2023, 2024, 2025, 잘 모름 |

관심 분야, 진로 고민, 수강 중인 과목, 코딩 수준, 프로젝트 경험, 취업/창업/대학원 목표는 대화 중에 파악한다. 초기 폼을 길게 만들지 않고, AI가 필요한 순간 선택지와 직접 입력을 섞어 추가 정보를 얻는다.

## 4. 대화형 선택지 패턴

AI 답변은 필요할 때 Claude식 선택지를 제공한다.

```txt
요즘 가장 도움받고 싶은 영역이 뭐예요?

1. 수강/학업
2. 진로/취업
3. 프로젝트/창업
4. 동아리/활동
5. 일정/과제 관리
6. 직접 입력
```

사용자는 번호, 버튼, 직접 입력 중 하나로 답할 수 있다. 선택 결과는 `intent`, `preference`, `concern`, `next_action` 같은 구조화 값으로 저장한다.

대화형 선택지는 사용자를 계속 설문지에 붙잡아 두기 위한 것이 아니라, 다음 답변을 더 정확히 만들기 위한 짧은 분기 장치다.

## 5. 개인 메모리 정책

메모리는 구조화 필드와 자연어 메모리를 모두 저장한다.

```txt
structured memory
- grade: 3
- department: ai
- interests: ["AI", "backend"]
- goals: ["employment", "portfolio"]

natural memory
- "사용자는 AI와 백엔드 서비스 개발에 관심이 있다."
- "사용자는 포트폴리오 프로젝트 방향을 고민하고 있다."
```

저장 정책은 정보 민감도에 따라 나눈다.

| 정보 유형 | 예시 | 정책 |
| --- | --- | --- |
| 낮은 민감도 | 관심 분야, 학년, 선호 분야, 프로젝트 관심 | 자동 저장 후 “기억했어요” 표시 |
| 중간 민감도 | 취업 불안, 학점 고민, 진로 갈등 | 저장 전 확인 |
| 높은 민감도 | 건강, 가족, 상세 성적, 계정/개인정보 | 기본 저장 금지 또는 명시 동의 필요 |

사용자는 기록 탭에서 메모리를 보고, 수정하고, 삭제할 수 있어야 한다.

## 6. 메모리 데이터 모델

MVP는 `profiles`, `user_memories`, `memory_events`를 분리한다.

```txt
profiles
- user_id
- department
- grade
- curriculum_year
- created_at
- updated_at
```

```txt
user_memories
- id
- user_id
- category
- key
- value_json
- natural_text
- embedding vector(768)
- embedding_status: ready | pending | failed
- embedding_model
- embedded_at
- confidence
- sensitivity
- status: active | archived | deleted
- created_at
- updated_at
```

```txt
memory_events
- id
- memory_id
- user_id
- source_message_id
- event_type: created | updated | deleted | confirmed | rejected
- decision: auto_saved | confirmed_by_user | session_only | rejected
- summary
- created_at
```

`memory_events.source_message_id`는 `chat_messages.id`와 연결한다. 사용자가 “왜 이걸 기억하고 있어?”라고 물으면 어떤 대화에서 생긴 메모리인지 설명할 수 있다.

## 7. 메모리 검색과 주입

메모리는 카테고리와 embedding 유사도 검색을 함께 사용한다.

```txt
사용자 질문
-> intent classifier
-> 관련 memory category 후보 선택
-> user_memories embedding 검색
-> 관련 메모리 top-k 선택
-> 답변 prompt에 주입
```

메모리 embedding은 저장 시 생성한다. Gemini embedding 호출이 실패하면 메모리 자체는 저장하고 `embedding_status = pending`으로 둔다. 이후 retry script나 background job에서 pending 메모리를 다시 embedding할 수 있다.

## 8. 채팅과 persona 라우팅

UI에는 하나의 AI 상담 경험을 제공하되, 내부적으로 persona를 라우팅한다.

| persona | 담당 |
| --- | --- |
| `academic_advisor` | 교과과정, 수강 방향, 교수/연구분야, 졸업요건 |
| `career_advisor` | 진로, 취업, 인턴, 포트폴리오, 대학원 |
| `startup_project_mentor` | 창업, 과제 주제, 캡스톤, PRD, MVP |
| `activity_advisor` | 동아리, 소모임, 학교생활 |
| `schedule_assistant` | 과제, 시험, D-day, Calendar 내보내기 |

사용자는 별도 챗봇을 고르지 않아도 된다. 홈에서 질문하면 intent classifier가 persona를 고르고, 각 탭은 intent 힌트로만 사용한다.

## 9. 화면 구조

메인 탭은 사용자 목적 기준으로 구성한다.

```txt
홈 | 학업 | 진로 | 프로젝트 | 일정 | 기록
```

홈은 AI 입력창을 중심에 두고 개인 대시보드 요약을 함께 보여준다.

| 영역 | 내용 |
| --- | --- |
| 상단 | “무엇을 도와드릴까요?”와 큰 AI 입력창 |
| 추천 질문 | 학년/전공/메모리 기반 질문 칩 |
| 개인 요약 | 소속, 학년, 최근 기억된 관심사 |
| 일정 요약 | 오늘/이번 주 D-day |
| 최근 기록 | 최근 상담, 추천 액션, Calendar 연결 상태 |

기록 탭은 메모리 투명성을 담당한다.

```txt
기록
- 기본 프로필
- 관심 분야
- 진로 고민
- 수강/학업 메모리
- 프로젝트 관심
- 일정/과제
- 최근 저장된 메모리
- LLM 활용 기록
```

## 10. 지식 소스

지식 소스는 세 종류로 분리한다.

| 지식 종류 | 예시 | 처리 방식 |
| --- | --- | --- |
| 학교/학과 내부 정보 | 교과과정, 교수진, 동아리, 학교 시스템 | raw 자료 -> Mini Wiki -> chunk -> embedding |
| 최신 외부 정보 | 채용 트렌드, 창업 지원사업, 공모전, 기술 스택 | Google Search grounding |
| 개인 정보 | 학년, 관심사, 진로 고민, 일정 | profile + memory RAG |

파인튜닝은 하지 않는다. 대신 직접 수집한 자료를 Markdown/JSON으로 정리하고, Mini LLM Wiki와 embedding RAG로 검색한다.

## 11. 자료 수집 포맷

사용자가 직접 자료를 넣을 수 있게 raw 자료 규칙을 단순하게 유지한다.

```txt
data/raw/
  curriculum-sw-2025.md
  curriculum-ai-2025.md
  professors-cs.md
  clubs-sw.md
  career-faq.md
  school-systems.md

data/raw-json/
  curriculum-sw-2025.json
  curriculum-ai-2025.json
```

Markdown metadata:

```md
---
title: 소프트웨어학부 2025 교과과정
category: curriculum
department: software
source_url: https://cs.kookmin.ac.kr/major/curriculum2025
collected_at: 2026-05-13
updated_at: 2026-05-13
freshness_status: stable
---
```

`freshness_status` 값은 `stable`, `semester_sensitive`, `time_sensitive`, `manual`을 사용한다.

## 12. Retrieval Router

모든 질문에 Google Search를 붙이지 않고 질문 유형별로 선택한다.

| 라우팅 | 사용 조건 |
| --- | --- |
| 내부 RAG | 교과과정, 교수, 동아리, 학교 시스템, 수강신청, 졸업요건 |
| Google grounding | 최신 채용 트렌드, 공모전, 창업 지원사업, 최신 기술 |
| 내부 RAG + Google grounding | 학교 맥락과 최신 진로 정보가 함께 필요한 질문 |
| 메모리 검색 | “내가 전에 뭐라고 했지?”, 개인 이력 요약 |
| 일정 parser | 과제/시험/마감일 등록 |

복합 질문 예시:

```txt
AI학부 3학년인데 백엔드도 같이 준비해도 될까?
```

이 경우 profile/memory, 내부 교과과정 RAG, 최신 직무 정보 grounding을 함께 사용한다.

## 13. 답변 구조와 근거 표시

답변은 본문, 추천 액션, 근거 보기, 확인 필요를 분리한다.

```txt
답변
- 선배 멘토 톤의 자연어 조언

추천 액션
- 지금 할 일 2~4개

근거 보기
- 내부 자료 근거
- 개인화 근거
- 최신 웹 근거

확인 필요
- 공식 공지나 수강신청 시스템에서 재확인할 항목
```

답변 metadata:

```json
{
  "answer": "...",
  "actions": ["...", "..."],
  "evidence": {
    "internal_sources": [],
    "personalization": [],
    "web_sources": []
  },
  "needs_verification": []
}
```

정책은 “확실한 것 / 추정 또는 제안 / 확인 필요”로 나눈다. 졸업요건, 학기별 개설 과목, 장학, 행정 정보는 공식 공지 확인 필요로 표시한다.

## 14. 답변 톤

기본 본문은 선배 멘토 톤을 사용한다.

```txt
지금 3학년이고 AI랑 백엔드 둘 다 관심 있으면,
AI 기능을 가진 백엔드 서비스 프로젝트를 하나 잡는 게 좋아 보여요.
```

근거, 출처, 주의사항은 조교 톤으로 정확하게 쓴다.

```txt
다음 자료를 근거로 판단했습니다.
실제 이번 학기 개설 여부는 수강신청 시스템에서 다시 확인해야 합니다.
```

## 15. 추천 로직

추천은 “Python 규칙 기반 + RAG + LLM 문장화” 구조로 만든다.

```txt
사용자 프로필/메모리
-> Python 추천 규칙으로 후보 생성
-> 내부 RAG로 학교 자료 근거 보강
-> 필요 시 Google grounding으로 최신 정보 보강
-> Gemini가 자연어 답변 생성
```

Python 규칙은 발표에서 설명 가능한 조건문, 반복문, 함수, 리스트/딕셔너리 형태로 둔다.

```txt
if grade >= 3 and interests include AI and backend:
    recommend "AI 서비스 백엔드/RAG 프로젝트"

if grade <= 2 and coding_level is beginner:
    recommend "전공 기초 + 작은 웹 프로젝트"

if goals include startup:
    recommend "문제 정의 + MVP + 사용자 검증 중심 프로젝트"
```

## 16. 일정과 Google Calendar

일정 등록은 대화형 입력 중심으로 만든다.

```txt
사용자:
문제해결코딩 기말 프로젝트 6월 10일 23:59까지야. 저장해줘.

AI:
다음 일정으로 저장할까요?

제목: 문제해결코딩 기말 프로젝트
과목: 문제해결코딩
마감: 2026-06-10 23:59
메모: 기말 프로젝트 제출
D-day: 28
```

MVP는 K-Class/eCampus 자동 로그인이나 크롤링을 하지 않는다. 사용자가 자연어로 말하거나 K-Class 공지 텍스트를 복붙하면 AI가 일정 정보를 추출한다. 스크린샷/OCR과 eCampus 직접 연동은 향후 기능으로 둔다.

Google Calendar는 내보내기만 MVP에 포함한다.

```txt
MVP 포함
- 앱 내부 일정 저장
- D-day 계산
- Google Calendar event 생성
- calendar_event_id 저장
- 중복 내보내기 방지

MVP 제외
- 양방향 동기화
- Google Calendar에서 앱으로 가져오기
- 반복 일정 고도화
```

OAuth는 앱 로그인과 분리한다. Supabase Auth는 앱 로그인, Google OAuth는 Calendar 접근 권한만 담당한다.

## 17. Google OAuth 토큰

토큰은 프론트엔드에 노출하지 않는다. 백엔드에서만 복호화한다.

```txt
google_oauth_tokens
- id
- user_id
- provider: google
- access_token_encrypted
- refresh_token_encrypted
- expires_at
- scope
- created_at
- updated_at
```

환경변수:

```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
TOKEN_ENCRYPTION_KEY=
```

MVP에서는 서버 환경변수 키로 토큰을 암호화해 DB에 저장한다. Supabase Vault나 별도 secret manager는 향후 개선으로 둔다.

## 18. 개인정보와 권한

MVP 보안 범위:

```txt
- Supabase Auth 사용자별 데이터 분리
- user_id 기준 RLS
- 개인 메모리 수정/삭제
- 일정 수정/삭제
- Google Calendar 토큰 server-only 처리
- 프론트에는 Calendar 연결 상태만 표시
```

MVP 제외:

```txt
- 계정 전체 데이터 내보내기
- 계정 전체 삭제 자동화
- eCampus 로그인 정보 저장
```

## 19. LLM 사용 경계

하이브리드 방식으로 구현한다.

Gemini 사용:

```txt
- intent classification
- memory extraction 후보 생성
- 일정/과제 JSON 추출
- RAG 답변 생성
- Google grounding 기반 최신 정보 답변
- embedding 생성
```

Python 사용:

```txt
- 라우팅 fallback
- 메모리 저장 정책 판단
- sensitivity 분류 보정
- D-day 계산
- 추천 규칙/점수 계산
- API schema validation
- 중복 Calendar export 방지
- 로그 저장
```

이렇게 해야 AI 서비스답게 동작하면서도 과제에서 요구하는 Python 로직을 명확히 설명할 수 있다.

## 20. API 초안

```txt
POST /api/profile
GET /api/profile
PATCH /api/profile

GET /api/memories
PATCH /api/memories/{memory_id}
DELETE /api/memories/{memory_id}

POST /api/chat
GET /api/chat/sessions
GET /api/chat/sessions/{session_id}

POST /api/assignments/preview
POST /api/assignments
GET /api/assignments
PATCH /api/assignments/{assignment_id}
POST /api/assignments/{assignment_id}/export-calendar

GET /api/integrations/google-calendar/connect
GET /api/integrations/google-calendar/callback
GET /api/integrations/google-calendar/status
```

## 21. 데모 흐름

발표 데모는 다음 순서로 구성한다.

1. 온보딩과 개인 메모리
2. 학업/진로 RAG 답변
3. 일정 등록과 Google Calendar 내보내기
4. LLM 사용 기록

예시 데모:

```txt
1. 인공지능학부 3학년, 2025 교과과정으로 설정
2. 진로/프로젝트 고민 선택
3. “AI학부 3학년인데 백엔드도 같이 준비해도 될까?” 질문
4. 개인 메모리 + 교과과정 RAG + 최신 웹 grounding 근거 확인
5. “문제해결코딩 기말 프로젝트 6월 10일 23:59까지야” 입력
6. 일정 추출, D-day 확인, Google Calendar 내보내기
7. 기록 탭에서 메모리와 LLM 사용 기록 확인
```

## 22. 구현 phase

이 spec은 하나의 제품 방향을 설명하지만, 구현은 다음 phase로 나눈다.

| Phase | 목표 |
| --- | --- |
| 1 | 제품 범위와 문서 정리 |
| 2 | profile/memory DB와 API foundation |
| 3 | 홈 AI 상담과 대화형 선택지 |
| 4 | 내부 RAG와 개인화 근거 표시 |
| 5 | 일정 등록과 D-day |
| 6 | Google Calendar 내보내기 |
| 7 | Google grounding |
| 8 | 기록 탭과 LLM 사용 기록 |

가장 먼저 구현할 vertical slice는 `profile + memory foundation`이다. 이 slice가 있어야 이후 학업/진로/RAG/일정 답변이 개인화될 수 있다.

## 23. 성공 기준

MVP 성공 기준:

- 사용자가 필수 프로필 3개를 설정할 수 있다.
- 대화 중 관심사/진로 고민이 메모리로 저장된다.
- 사용자는 저장된 메모리를 보고 수정/삭제할 수 있다.
- AI 답변은 개인화 근거, 내부 자료 근거, 최신 웹 근거를 분리해 보여준다.
- 사용자는 자연어로 과제를 등록하고 D-day를 볼 수 있다.
- 사용자는 저장된 일정을 Google Calendar로 내보낼 수 있다.
- LLM 사용 기록과 개발 과정 기록이 제출 문서에 남는다.
