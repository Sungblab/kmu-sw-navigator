from app.core.config import Settings
from app.schemas.runtime_status import RuntimeComponentStatus, RuntimeStatusResponse
from app.scripts.supabase_schema_check import SchemaCheckItem


def build_runtime_status(
    settings: Settings,
    schema_items: list[SchemaCheckItem] | None = None,
) -> RuntimeStatusResponse:
    supabase_missing = _missing_env(
        {
            "SUPABASE_URL": settings.supabase_url,
            "SUPABASE_SERVICE_ROLE_KEY": settings.supabase_service_role_key,
        }
    )
    supabase_ready = not supabase_missing
    schema_status = _schema_status(supabase_ready=supabase_ready, schema_items=schema_items)

    gemini_missing = _missing_env({"GEMINI_API_KEY": settings.gemini_api_key})
    google_missing = _missing_env(
        {
            "GOOGLE_OAUTH_CLIENT_ID": settings.google_oauth_client_id,
            "GOOGLE_OAUTH_CLIENT_SECRET": settings.google_oauth_client_secret,
        }
    )

    return RuntimeStatusResponse(
        mode="live",
        supabase_backend=RuntimeComponentStatus(
            configured=supabase_ready,
            ready=supabase_ready,
            missing_env=supabase_missing,
            blocker=None if supabase_ready else "supabase_backend_env_missing",
        ),
        supabase_schema=schema_status,
        gemini=RuntimeComponentStatus(
            configured=not gemini_missing,
            ready=not gemini_missing,
            missing_env=gemini_missing,
            blocker=None if not gemini_missing else "gemini_env_missing",
        ),
        google_calendar=RuntimeComponentStatus(
            configured=not google_missing,
            ready=not google_missing,
            missing_env=google_missing,
            blocker=None if not google_missing else "google_oauth_env_missing",
        ),
    )


def _schema_status(
    *,
    supabase_ready: bool,
    schema_items: list[SchemaCheckItem] | None,
) -> RuntimeComponentStatus:
    if not supabase_ready:
        return RuntimeComponentStatus(
            configured=False,
            ready=False,
            blocker="supabase_backend_env_missing",
        )

    if schema_items is None:
        return RuntimeComponentStatus(configured=True, ready=False, blocker="schema_not_checked")

    missing_schema = [f"{item.kind}: {item.name}" for item in schema_items if not item.ready]
    return RuntimeComponentStatus(
        configured=True,
        ready=not missing_schema,
        missing_schema=missing_schema,
        blocker=None if not missing_schema else "schema_sql_not_applied",
    )


def _missing_env(values: dict[str, str]) -> list[str]:
    # Live readiness only exposes variable names. Values may be service-role keys or OAuth secrets.
    return [name for name, value in values.items() if not value]
