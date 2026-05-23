from app.core.supabase_errors import is_schema_cache_error, schema_blocker_message


def test_schema_cache_error_detects_postgrest_codes() -> None:
    assert is_schema_cache_error(RuntimeError("PGRST205 schema cache")) is True
    assert is_schema_cache_error(RuntimeError("PGRST202 function missing")) is True
    assert is_schema_cache_error(RuntimeError("network failed")) is False


def test_schema_blocker_message_names_schema_action() -> None:
    message = schema_blocker_message("Supabase smoke", RuntimeError("PGRST205"))

    assert "Supabase schema is not applied" in message
    assert "supabase/schema.sql" in message
