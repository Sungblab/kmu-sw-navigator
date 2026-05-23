from __future__ import annotations


def is_schema_cache_error(error: Exception) -> bool:
    text = str(error)
    return "PGRST205" in text or "PGRST202" in text or "schema cache" in text


def schema_blocker_message(command_name: str, error: Exception) -> str:
    if is_schema_cache_error(error):
        return (
            f"{command_name} failed: Supabase schema is not applied. "
            "Apply supabase/schema.sql, then rerun this smoke."
        )
    return f"{command_name} failed: {error}"
