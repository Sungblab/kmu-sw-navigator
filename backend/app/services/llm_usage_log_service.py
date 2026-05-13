from __future__ import annotations

from app.schemas.llm_usage import LLMUsageLogCreateRequest, LLMUsageLogResponse


class InMemoryLLMUsageLogStore:
    def __init__(self) -> None:
        self.logs: list[LLMUsageLogResponse] = []

    def create_log(
        self,
        user_id: str,
        request: LLMUsageLogCreateRequest,
    ) -> LLMUsageLogResponse:
        log = LLMUsageLogResponse(user_id=user_id, **request.model_dump())
        self.logs.append(log)
        return log

    def list_logs(self, user_id: str, *, limit: int = 50) -> list[LLMUsageLogResponse]:
        user_logs = [log for log in self.logs if log.user_id == user_id]
        return user_logs[-limit:][::-1]
