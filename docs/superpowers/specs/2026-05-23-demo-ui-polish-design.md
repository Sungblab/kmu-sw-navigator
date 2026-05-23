# Demo UI Polish Design

## 목표

발표 데모에서 AI 답변과 사용자 액션 결과가 더 읽기 쉽게 보이도록 프론트엔드 표시 품질을 보강한다. 외부 키가 필요한 Supabase/Gemini/Google live smoke는 현재 환경 변수 부족으로 막혀 있으므로, 이번 slice는 외부 서비스 계약을 바꾸지 않는 UI 개선으로 제한한다.

## 범위

- assistant 답변은 plain paragraph 대신 `streamdown`으로 렌더링한다.
- 한국어/CJK 줄바꿈 품질을 위해 `@streamdown/cjk`를 함께 설치한다.
- 로그인, 로그아웃, 일정 미리보기/저장/완료/삭제, Calendar export, 추천, 프로필 저장, 채팅 전송 결과를 `sonner` toast로 보여준다.
- 기존 `error` 영역은 유지해 발표자가 실패 원인을 화면에서 계속 볼 수 있게 한다.
- FastAPI API 계약, Python 핵심 로직, Supabase schema는 변경하지 않는다.

## 제외

- SSE/token streaming 구현은 이번 범위에서 제외한다.
- TanStack Query 리팩터링은 App 상태 구조 변경이 커서 후속 slice로 둔다.
- Docker Compose 홈서버 배포 구현은 후속 운영 과제로 둔다.

## 검증

- `pnpm build:frontend`
- `pnpm docs:check`

프론트엔드 전용 테스트 러너가 아직 없으므로 이번 slice는 TypeScript/Vite build와 문서 검증으로 확인한다.
