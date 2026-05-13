# Gemini Answer Generation Plan

> **For agentic workers:** 이 plan은 retrieval evidence와 memory context를 Gemini 답변 생성에 연결한 구현 기록이다.

**Goal:** `GEMINI_API_KEY`가 있으면 `/api/chat`이 retrieved evidence와 personalization memory를 prompt로 묶어 Gemini 답변을 생성한다. 키가 없으면 기존 deterministic answer를 유지한다.

## Implemented Scope

- `backend/app/services/answer_generation_service.py`를 추가했다.
- `GeminiAnswerGenerator`가 `google-genai` `models.generate_content()`를 호출한다.
- `build_answer_prompt()`가 사용자 질문, intent, 개인화 메모리, 내부 검색 근거를 분리해 prompt를 만든다.
- `backend/app/services/chat_contract_service.py`가 optional answer generator를 받게 했다.
- `backend/app/api/dependencies.py`가 `GEMINI_API_KEY`가 있을 때 `GeminiAnswerGenerator`를 제공한다.
- `/api/chat`이 answer generator dependency를 받아 Gemini/fallback 경로를 선택한다.
- fake generator 테스트로 prompt/context 전달과 answer override를 검증했다.

## Core Logic Notes

- 내부 자료 근거가 있으면 prompt에 source title, heading path, score, content를 넣는다.
- 내부 자료 근거가 없으면 prompt에 근거 없음이 명시된다.
- 최신 취업/공모전 정보는 Google grounding 전이므로 확정적으로 답하지 말라는 규칙을 system/prompt에 넣었다.
- Gemini가 빈 답변을 반환하면 오류로 처리한다.

## Verification

```powershell
cd backend
uv run python -m pytest tests\services\test_answer_generation_service.py tests\api\test_chat_contract_api.py -q
cd ..
pnpm lint:backend
```

결과:

- focused answer/chat tests: 6 passed
- `pnpm lint:backend`: All checks passed

## Remaining Work

- 실제 `GEMINI_API_KEY`로 `pnpm gemini:answer-smoke` live chat generation smoke를 수행한다.
- chat session/message Supabase 저장을 연결한다.
- career/startup intent에는 Google grounding을 별도 연결한다.
