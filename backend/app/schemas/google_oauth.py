from datetime import datetime

from pydantic import BaseModel


class GoogleOAuthTokenRecord(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str | None = None
    scope: str | None = None
    expires_at: datetime | None = None


class GoogleOAuthConnectionResponse(BaseModel):
    connected: bool
    scope: str | None = None
    expires_at: datetime | None = None
