from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_current_user_id,
    get_google_oauth_http_client,
    get_google_oauth_token_store,
)
from app.core.config import get_settings
from app.schemas.google_oauth import GoogleOAuthConnectionResponse
from app.schemas.integration import (
    GoogleCalendarConnectResponse,
    GoogleCalendarStatusResponse,
)
from app.services.google_calendar_oauth_service import (
    build_google_calendar_connect_response,
    get_google_calendar_status,
    parse_google_calendar_state,
)
from app.services.google_oauth_token_service import (
    GoogleOAuthTokenStore,
    exchange_google_calendar_code,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
GoogleOAuthTokenStoreDep = Annotated[
    GoogleOAuthTokenStore,
    Depends(get_google_oauth_token_store),
]
GoogleOAuthHttpClientDep = Annotated[httpx.Client, Depends(get_google_oauth_http_client)]


@router.get("/google-calendar/status")
def google_calendar_status(
    user_id: CurrentUserId,
    store: GoogleOAuthTokenStoreDep,
) -> GoogleCalendarStatusResponse:
    return get_google_calendar_status(get_settings(), user_id=user_id, store=store)


@router.get("/google-calendar/connect")
def google_calendar_connect(user_id: CurrentUserId) -> GoogleCalendarConnectResponse:
    return build_google_calendar_connect_response(user_id, get_settings())


@router.get("/google-calendar/callback")
def google_calendar_callback(
    code: str,
    state: str,
    store: GoogleOAuthTokenStoreDep,
    client: GoogleOAuthHttpClientDep,
) -> GoogleOAuthConnectionResponse:
    settings = get_settings()
    try:
        user_id = parse_google_calendar_state(state, settings)
        return exchange_google_calendar_code(
            user_id,
            code=code,
            settings=settings,
            store=store,
            client=client,
        )
    except (ValueError, httpx.HTTPError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar 연결에 실패했습니다.",
        ) from exc
