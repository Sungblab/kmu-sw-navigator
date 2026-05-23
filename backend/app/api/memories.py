from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id, get_memory_store
from app.schemas.memory import MemoryCreateRequest, MemoryResponse, MemoryUpdateRequest
from app.services.memory_service import (
    archive_memory,
    create_memory_candidate,
    update_memory,
)
from app.services.store_protocols import MemoryStore

router = APIRouter(prefix="/memories", tags=["memories"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
MemoryStoreDep = Annotated[MemoryStore, Depends(get_memory_store)]


@router.get("")
def list_memories(
    user_id: CurrentUserId,
    store: MemoryStoreDep,
) -> dict[str, list[MemoryResponse]]:
    return {"memories": store.list_active_memories(user_id)}


@router.post("")
def create_memory(
    request: MemoryCreateRequest,
    user_id: CurrentUserId,
    store: MemoryStoreDep,
) -> MemoryResponse:
    return create_memory_candidate(
        store=store,
        user_id=user_id,
        natural_text=request.natural_text,
        category=request.category,
        key=request.key,
        value_json=request.value_json,
    )


@router.patch("/{memory_id}")
def patch_memory(
    memory_id: str,
    request: MemoryUpdateRequest,
    user_id: CurrentUserId,
    store: MemoryStoreDep,
) -> MemoryResponse:
    return update_memory(
        store=store,
        user_id=user_id,
        memory_id=memory_id,
        natural_text=request.natural_text,
        value_json=request.value_json,
    )


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: str,
    user_id: CurrentUserId,
    store: MemoryStoreDep,
) -> MemoryResponse:
    return archive_memory(store, user_id, memory_id)
