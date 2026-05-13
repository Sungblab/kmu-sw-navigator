# 테스트 전략

## 테스트 목표

- 과제 조건을 코드로 충족하는지 확인합니다.
- 발표 데모가 재현 가능한지 확인합니다.
- RAG 답변이 출처를 포함하고 근거 부족 상황을 처리하는지 확인합니다.

## 백엔드 테스트

| 대상 | 테스트 |
| --- | --- |
| `/health` | API 서버가 실행 가능한지 확인 |
| markdown chunker | heading path, content hash, 긴 문단 분리 확인 |
| wiki compiler | raw metadata 파싱, category별 wiki page, `_index.md` 생성 확인 |
| 추천 service | 조건문/딕셔너리 추천 결과 확인 |
| D-day service | 날짜 차이 계산 확인 |
| RAG service | 검색 결과 없음/있음 분기 확인 |
| LLM log service | 사용 기록 저장 payload 확인 |

## 프론트엔드 테스트

초기에는 수동 검증과 build 검증을 우선합니다.

```powershell
pnpm build:frontend
```

## 문서 검증

```powershell
pnpm docs:check
```

문서 검증은 제출 자료 누락을 막기 위한 최소 안전장치입니다.
