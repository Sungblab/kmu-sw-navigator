# 데모 시나리오

발표영상은 20-25분을 목표로 한다. 데모는 실제 앱 화면을 먼저 보여주고, 각 기능 뒤에 짧게 Python 핵심 로직과 LLM 활용 기록을 설명한다.

## 0. 데모 전 준비

```powershell
pnpm env:check
pnpm dev:backend
pnpm dev:frontend
```

- Supabase/Gemini/Google 키가 없으면 앱은 in-memory fallback과 deterministic 응답으로 실행한다.
- live 검증을 할 때는 `backend/.env`, `frontend/.env`를 채우고 Supabase Auth user를 만든 뒤 `pnpm env:check:strict`, `pnpm supabase:smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm supabase:login-smoke -- --email <email> --password <password>`, `pnpm supabase:llm-smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm google:calendar-smoke -- --user-id <supabase-auth-user-uuid>`, `pnpm gemini:smoke`, `pnpm gemini:answer-smoke`, `pnpm gemini:grounding-smoke` 순서로 확인한다.
- 발표에서는 외부 키가 없는 경우도 과제 평가자가 실행할 수 있도록 fallback 경로를 먼저 보여준다.
- 라즈베리파이 홈서버 배포는 Docker Compose 기반 후속 운영 경로로 설명하되, 발표 당일 주 데모는 네트워크 변수에 덜 흔들리는 노트북 로컬 실행으로 한다.
- 홈서버 URL을 보여줄 경우에는 로컬 데모와 화면이 같다는 보조 시연으로만 사용하고, 장애 시 녹화/스크린샷 백업으로 전환한다.

## 1. 프로젝트 소개

- 프로젝트명: `kmu-sw-navigator`
- 주제: 국민대학교 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터
- 문제: 커리큘럼, 트랙, 진로/취업, 프로젝트, 과제 일정을 한곳에서 보기 어렵다.
- 해결: React UI, FastAPI Python backend, Supabase 저장소, Mini LLM Wiki/RAG, Gemini API, Google grounding을 조합한다.

말할 핵심:

```txt
일반 챗봇이 아니라 학교 자료, 사용자 메모리, 일정 정보를 함께 보는 개인화 상담 앱입니다.
신입생 데모를 중심으로 하지만 구조는 전체 학년까지 확장할 수 있게 설계했습니다.
```

## 2. 메인 화면과 Supabase 연결 구조

보여줄 화면:

- 왼쪽 사이드바: AI 상담, 학업 로드맵, 진로/취업, 프로젝트, 일정, 설정
- 가운데: 현재 작업 화면
- 오른쪽 패널: 프로필, 메모리, 근거, 일정, 추천 액션
- 설정 화면: Supabase 로그인, Google Calendar 연결 상태

설명할 코드/구조:

- frontend는 Supabase `Framework/client` 값으로 로그인 세션을 만든다.
- backend는 Supabase `Direct`/service-role 값으로 DB 저장소에 접근한다.
- service role key는 브라우저에 넣지 않는다.

## 3. 개인화 RAG 상담

질문 예시:

```txt
AI 쪽 관심 있는데 1학년 때 뭘 먼저 보면 좋아?
```

보여줄 것:

- 채팅 입력과 assistant 답변
- 오른쪽 context panel의 개인화 근거
- 내부 자료 근거 chip
- 진로/취업/창업 질문일 때 웹 근거 슬롯
- 최근 대화 목록

설명할 Python 로직:

- `detect_intent()`가 질문 키워드로 학업/일정/진로/프로젝트 의도를 나눈다.
- `retrieval_service.py`가 raw/wiki 문서에서 관련 chunk를 찾고 `evidence.internal_sources`에 넣는다.
- Gemini key가 있으면 `answer_generation_service.py`가 검색 근거와 메모리 context로 답변을 생성한다.
- 최신성이 필요한 intent만 Google Search grounding을 사용한다.

## 4. 진로/활동 추천

입력 예시:

```txt
트랙 관심사: AI, 백엔드
활동 관심사: 개발, 알고리즘
목표: 취업 포트폴리오 준비
코딩 경험: 중급
학습 선호: 프로젝트
활동 방식: 팀
주간 가능 시간: 6
```

보여줄 것:

- 진로/취업 화면의 직접 입력 편집 UI
- 추천 실행 버튼
- 트랙 추천 결과, 점수, 이유
- 활동 추천 결과, 다음 행동
- 내부 자료 근거 chip
- `자동값으로 되돌리기` 버튼

설명할 Python 로직:

- `TRACK_RULES`, `ACTIVITY_RULES` 리스트/딕셔너리에 후보를 둔다.
- 관심사, 목표, 코딩 경험, 학습 선호, 활동 성향을 조건문으로 점수화한다.
- 반복문으로 후보를 평가하고 점수순으로 정렬한다.
- 추천 점수와 RAG 근거는 분리해서, 추천은 설명 가능한 Python 규칙으로 유지한다.

## 5. 일정 관리와 D-day

입력 예시:

```txt
자료구조 과제 다음주 금요일 밤 11시 59분까지 제출해야 해
```

보여줄 것:

- 일정 탭 자연어 입력
- 미리보기 결과: 제목, 과목, 마감일, confidence, parser
- 저장 후 일정 목록과 D-day
- 완료/삭제 버튼
- Calendar 내보내기 버튼

설명할 Python 로직:

- Gemini key가 있으면 일정 JSON parser를 먼저 시도한다.
- 실패하거나 key가 없으면 Python 규칙 parser가 `오늘`, `내일`, `다음주 금요일`, `5월 20일` 같은 표현을 처리한다.
- D-day는 마감일과 기준 날짜 차이로 계산한다.
- Calendar export는 event payload를 만들고, OAuth token이 있으면 Google `events.insert`를 호출한다.
- token이 없으면 로컬 데모용 synthetic id로 export 상태만 저장한다.

## 6. LLM 활용 기록과 제출 증거

보여줄 문서:

- `docs/llm/usage-log.md`
- `docs/architecture/python-core-logic.md`
- `docs/contributing/plans-status.md`
- 관련 `docs/superpowers/plans/*.md`

말할 핵심:

```txt
LLM은 주제 구체화, 설계 문서, 구현 보조, 코드 리뷰 관점 정리에 사용했습니다.
제출 코드는 그대로 복사한 것이 아니라 Python 로직을 직접 설명할 수 있게 함수, 조건문, 테스트, 주석, 문서로 정리했습니다.
```

## 7. 과제 조건 매핑

| 과제 조건 | 데모에서 보여줄 위치 |
| --- | --- |
| 사용자 입력 | 채팅, 추천 입력, 자연어 일정 입력 |
| 조건문 | intent 분류, 메모리 민감도, 추천 점수, 일정 parser fallback |
| 반복문 | 문서 chunk 검색, 추천 후보 평가, 일정/대화 목록 표시 |
| 함수 | `build_chat_response`, `recommend_tracks`, `preview_assignment`, `build_calendar_event` |
| 리스트/딕셔너리 | 추천 규칙, evidence payload, assignment list, memory value_json |
| 의미 있는 출력 | 답변, 추천 결과, D-day, Calendar export 상태, LLM 활용 기록 |
| 실행 가능한 Python | `pnpm test:backend`, `pnpm lint:backend`, FastAPI local server |
| LLM 활용 기록 | `docs/llm/usage-log.md` |

## 8. 한계와 다음 개선

- Supabase/Gemini/Google live smoke는 실제 키 설정 후 검증해야 한다.
- 자료 범위는 현재 raw/wiki 샘플 중심이라 더 많은 학교 공식 문서를 추가해야 한다.
- eCampus 자동 연동은 보안 검토가 필요해 MVP 밖으로 둔다.
- Calendar는 단방향 event insert 중심이며, 양방향 sync는 후속 기능이다.
- 라즈베리파이 홈서버 배포는 Docker Compose로 앱 서버와 정적 프론트/reverse proxy를 묶는 후속 운영 과제로 남긴다.
