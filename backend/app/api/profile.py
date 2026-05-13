from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id, get_profile_store
from app.schemas.profile import ProfileResponse, ProfileUpsertRequest
from app.services.store_protocols import ProfileStore

router = APIRouter(prefix="/profile", tags=["profile"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
ProfileStoreDep = Annotated[ProfileStore, Depends(get_profile_store)]


@router.get("")
def get_profile(
    user_id: CurrentUserId,
    store: ProfileStoreDep,
) -> ProfileResponse | dict[str, bool]:
    profile = store.get_profile(user_id)
    if profile is None:
        return {"exists": False}
    return profile


@router.post("")
def upsert_profile(
    request: ProfileUpsertRequest,
    user_id: CurrentUserId,
    store: ProfileStoreDep,
) -> ProfileResponse:
    return store.upsert_profile(user_id, request)


@router.patch("")
def patch_profile(
    request: ProfileUpsertRequest,
    user_id: CurrentUserId,
    store: ProfileStoreDep,
) -> ProfileResponse:
    return store.upsert_profile(user_id, request)
