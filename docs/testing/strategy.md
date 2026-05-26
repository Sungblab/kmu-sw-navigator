# 테스트 전략

## 테스트 목표

- 과제 조건을 코드로 충족하는지 확인합니다.
- 사용자 입력을 바탕으로 의미 있는 Python 처리 결과가 나오는지 확인합니다.
- 조건문, 반복문, 함수, 리스트/딕셔너리 사용 지점이 발표에서 설명 가능한지 확인합니다.
- 발표 시연이 실제 로그인 사용자 흐름으로 재현 가능한지 확인합니다.
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
| RAG quality evaluation | 시연 질문의 내부 출처 후보, 기대 category, 범위 밖 질문 처리 확인 |
| LLM log service | 사용 기록 저장 payload 확인 |

## 과제 조건 검증 체크리스트

- 사용자 입력: API 요청, CLI 입력, 폼 입력 중 하나 이상을 핵심 Python 로직에 전달합니다.
- 조건문: 추천 분기, 검색 결과 없음 처리, 일정 상태 판단처럼 실제 의사결정에 사용합니다.
- 반복문: 문서 chunk, 추천 후보, 일정 목록, 로그 목록을 순회하는 처리에 사용합니다.
- 함수: 추천, 검색, D-day 계산, 메모리 분류처럼 설명 가능한 단위로 분리합니다.
- 리스트/딕셔너리: 추천 규칙, 문서 목록, 출처, 로그 payload 같은 구조화 데이터에 사용합니다.
- 의미 있는 출력: 추천 결과, 출처 포함 답변, D-day, 저장된 LLM 기록처럼 입력에 따라 달라지는 결과를 반환합니다.
- LLM 활용 기록: Codex/ChatGPT/Claude/Gemini를 사용한 목적과 직접 검토/수정 내용을 `docs/llm/usage-log.md`에 기록합니다.

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

## RAG 평가

시연 전에는 live API와 별개로 로컬 자료 기준 근거 후보를 먼저 확인합니다.

```powershell
pnpm rag:evaluate
```

이 명령은 `data/raw`, `data/wiki`를 검색해 대표 질문 4개와 범위 밖 질문 1개를 평가한다. 답변 문장 자체가 아니라 답변 생성 전에 사용할 내부 근거가 충분한지 확인하는 용도다.
