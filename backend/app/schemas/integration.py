from pydantic import BaseModel


class GoogleCalendarStatusResponse(BaseModel):
    configured: bool
    connected: bool
    scope: str


class GoogleCalendarConnectResponse(BaseModel):
    configured: bool
    authorization_url: str | None = None
    scope: str
    reason: str | None = None
