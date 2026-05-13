# 협업 방식

## 기본 흐름

```txt
아이디어 또는 요구사항
-> spec 작성
-> plan 작성
-> issue 생성
-> branch 생성
-> 구현
-> 검증
-> PR
-> 리뷰
-> merge
-> LLM 활용 기록 갱신
```

## 작업 단위

작업은 너무 크게 잡지 않습니다. 한 PR은 하나의 주제를 다룹니다.

좋은 예:

- RAG 검색 API 추가
- 일정 D-day 계산 함수 추가
- 챗봇 화면 UI 추가
- LLM 활용 기록 페이지 추가

나쁜 예:

- 백엔드와 프론트와 보고서를 전부 한 PR에서 수정
- schema와 UI와 발표자료를 이유 없이 함께 수정

## 리뷰 기준

- 실행 가능한가
- 과제 조건을 설명 가능하게 충족하는가
- LLM 생성물을 그대로 붙인 것이 아니라 이해하고 수정했는가
- README나 관련 문서가 최신인가
- API 키나 개인 정보가 포함되지 않았는가

## 검증 기록

PR에는 실행한 명령을 적습니다.

```txt
pnpm docs:check
pnpm wiki:build
cd backend && uv run pytest
cd backend && uv run ruff check .
pnpm build:frontend
```
