# GitHub 저장소 설정

## 기본 설정

| 항목 | 값 |
| --- | --- |
| 저장소 이름 | `kmu-sw-navigator` |
| 공개 여부 | Public |
| 기본 브랜치 | `main` |
| 설명 | 국민대학교 소프트웨어융합대학 학생을 위한 개인화 RAG 기반 AI 내비게이터 |

## 권장 설정

- Issues 활성화
- Pull Requests 활성화
- Wiki는 사용하지 않고 repo의 `docs/`를 사용
- Discussions는 필요 시 활성화
- 브랜치 보호는 초기 개발 속도를 위해 첫 기능 구현 후 적용
- PR 템플릿은 `.github/pull_request_template.md`를 사용
- 이슈 템플릿은 기능 작업과 버그 리포트로 구분
- GitHub Actions는 문서 누락과 Python syntax를 먼저 검사

## 첫 push 후 확인할 것

1. README가 GitHub 첫 화면에 잘 보이는지 확인
2. `.env`가 올라가지 않았는지 확인
3. `docs/README.md` 링크가 정상인지 확인
4. 팀원이 clone 후 dev guide를 따라 실행할 수 있는지 확인
5. `verify` workflow가 정상 실행되는지 확인
