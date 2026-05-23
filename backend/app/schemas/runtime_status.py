from pydantic import BaseModel, Field


class RuntimeComponentStatus(BaseModel):
    configured: bool
    ready: bool
    missing_env: list[str] = Field(default_factory=list)
    missing_schema: list[str] = Field(default_factory=list)
    blocker: str | None = None


class RuntimeStatusResponse(BaseModel):
    mode: str
    supabase_backend: RuntimeComponentStatus
    supabase_schema: RuntimeComponentStatus
    gemini: RuntimeComponentStatus
    google_calendar: RuntimeComponentStatus
