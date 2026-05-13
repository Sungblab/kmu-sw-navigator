# 보안 정책

이 프로젝트는 수업 과제용 공개 저장소입니다. 실제 서비스 운영 전에는 별도 보안 검토가 필요합니다.

## 비밀값 관리

- `.env`, `backend/.env`, `frontend/.env`는 커밋하지 않습니다.
- Gemini API Key, Supabase service role key, Supabase JWT secret은 공개하지 않습니다.
- 프론트엔드에는 Supabase anon key만 사용합니다.
- service role key는 FastAPI 백엔드에서만 사용합니다.

## 데이터 범위

- 실제 학생 개인정보를 저장하지 않습니다.
- 데모 계정과 sample data를 사용합니다.
- 제출 자료에는 민감한 토큰, 쿠키, 개인 계정 정보를 포함하지 않습니다.

## 취약점 보고

팀원은 보안 문제가 의심되면 GitHub Issue에 비밀값을 쓰지 말고 김성빈에게 직접 공유합니다.

