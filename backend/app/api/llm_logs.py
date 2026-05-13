from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id, get_llm_usage_log_store
from app.schemas.llm_usage import LLMUsageLogListResponse
from app.services.store_protocols import LLMUsageLogStore

router = APIRouter(prefix="/llm-logs", tags=["llm-logs"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
LLMUsageLogStoreDep = Annotated[LLMUsageLogStore, Depends(get_llm_usage_log_store)]


@router.get("")
def list_llm_usage_logs(
    user_id: CurrentUserId,
    store: LLMUsageLogStoreDep,
) -> LLMUsageLogListResponse:
    return LLMUsageLogListResponse(logs=store.list_logs(user_id))
