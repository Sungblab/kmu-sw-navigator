# Codex와 Superpowers 활용 방식

이 문서는 “LLM을 어떤 목적으로 사용했는지”를 설명하기 위한 핵심 자료입니다. 본 프로젝트는 Codex를 단순 코드 생성기가 아니라 PM/개발 리드의 설계, 계획, 검증 보조 도구로 사용합니다.

## 사용 원칙

- LLM이 만든 코드를 그대로 제출하지 않습니다.
- 설계, 계획, 코드 초안, 오류 분석, 테스트 아이디어를 얻는 데 사용합니다.
- 최종 코드는 팀원이 직접 읽고 수정하고 실행합니다.
- 주요 함수와 흐름은 발표에서 설명할 수 있어야 합니다.
- 사용 기록은 `docs/llm/usage-log.md`에 남깁니다.

## Superpowers 흐름

```txt
brainstorming
-> design spec
-> implementation plan
-> implementation
-> verification
-> completion record
```

## repo 안에 남기는 산출물

| 산출물 | 위치 | 목적 |
| --- | --- | --- |
| 설계 문서 | `docs/superpowers/specs/` | 요구사항, 범위, 아키텍처 확정 |
| 실행 계획 | `docs/superpowers/plans/` | 구현 순서와 검증 명령 |
| LLM 활용 기록 | `docs/llm/usage-log.md` | 제출용 LLM 사용 내역 |
| 프롬프트 요약 | `docs/llm/prompt-summary-log.md` | 중요한 요청과 결정 요약 |
| 작업 상태 | `docs/contributing/plans-status.md` | 현재 진행 상황 |

## Codex 사용 예시

- PRD를 읽고 MVP 범위를 줄이는 데 사용
- OpenCairn의 문서 구조를 조사하고 이 repo에 맞게 축소하는 데 사용
- README, CONTRIBUTING, AGENTS, docs index 초안 작성에 사용
- 기술 스택 후보와 공식 문서 근거를 대조하는 데 사용
- 검증 명령과 GitHub 공개 repo 세팅을 점검하는 데 사용

