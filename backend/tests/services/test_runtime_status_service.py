from app.core.config import Settings
from app.scripts.supabase_schema_check import SchemaCheckItem
from app.services.runtime_status_service import build_runtime_status


def test_runtime_status_reports_missing_env_without_secret_values() -> None:
    status = build_runtime_status(Settings())

    assert status.mode == "live"
    assert status.supabase_backend.ready is False
    assert status.supabase_backend.missing_env == [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]
    assert status.supabase_schema.blocker == "supabase_backend_env_missing"
    assert status.gemini.ready is False
    assert status.gemini.missing_env == ["GEMINI_API_KEY"]
    assert status.google_calendar.ready is False
    assert status.google_calendar.missing_env == [
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_CLIENT_SECRET",
    ]


def test_runtime_status_separates_supabase_schema_blocker_from_env() -> None:
    status = build_runtime_status(
        Settings(
            supabase_url="https://example.supabase.co",
            supabase_service_role_key="service-role-secret",
            gemini_api_key="gemini-secret",
            google_oauth_client_id="google-client-id",
            google_oauth_client_secret="google-secret",
        ),
        schema_items=[
            SchemaCheckItem(kind="table", name="profiles", ready=True),
            SchemaCheckItem(kind="function", name="match_document_chunks", ready=False),
        ],
    )

    assert status.supabase_backend.ready is True
    assert status.supabase_backend.missing_env == []
    assert status.supabase_schema.ready is False
    assert status.supabase_schema.blocker == "schema_sql_not_applied"
    assert status.supabase_schema.missing_schema == ["function: match_document_chunks"]
    assert status.gemini.ready is True
    assert status.google_calendar.ready is True
