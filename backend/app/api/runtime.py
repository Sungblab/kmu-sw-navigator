from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user_id
from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.schemas.runtime_status import RuntimeStatusResponse
from app.scripts.supabase_schema_check import SchemaCheckItem, check_supabase_schema
from app.services.runtime_status_service import build_runtime_status

router = APIRouter(prefix="/runtime", tags=["runtime"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]


def get_runtime_schema_items() -> list[SchemaCheckItem] | None:
    settings = get_settings()
    if not settings.has_supabase_backend:
        return None
    try:
        return check_supabase_schema(get_supabase_client())
    except Exception as exc:
        return [
            SchemaCheckItem(
                kind="connection",
                name="supabase",
                ready=False,
                error=str(exc)[:180],
            )
        ]


RuntimeSchemaItems = Annotated[list[SchemaCheckItem] | None, Depends(get_runtime_schema_items)]


@router.get("/status")
def runtime_status(
    _: CurrentUserId,
    schema_items: RuntimeSchemaItems,
) -> RuntimeStatusResponse:
    return build_runtime_status(get_settings(), schema_items=schema_items)
