from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""
    frontend_origin: str = "http://localhost:5173"
    gemini_api_key: str = ""
    gemini_main_model: str = "gemini-3-flash-preview"
    gemini_schedule_model: str = Field(
        default="gemini-3.1-flash-lite",
        validation_alias=AliasChoices("GEMINI_SCHEDULE_MODEL", "GEMINI_LIGHT_MODEL"),
    )
    gemini_embedding_model: str = "gemini-embedding-2"
    gemini_embedding_dim: int = 768
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = (
        "http://127.0.0.1:8000/api/integrations/google-calendar/callback"
    )
    google_calendar_scope: str = "https://www.googleapis.com/auth/calendar.events"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def has_supabase_backend(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def has_google_calendar_oauth(self) -> bool:
        return bool(
            self.google_oauth_client_id
            and self.google_oauth_client_secret
            and self.google_oauth_redirect_uri
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
