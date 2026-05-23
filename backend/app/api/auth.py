from __future__ import annotations

import httpx
import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError


def bearer_token_from_authorization(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauthorized()

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise _unauthorized()
    return token


def user_id_from_supabase_token(authorization: str | None, jwt_secret: str) -> str:
    token = bearer_token_from_authorization(authorization)

    try:
        # Supabase access tokens are HS256 JWTs signed with the project JWT secret.
        # We trust the user id only after signature verification and a subject check.
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except InvalidTokenError as exc:
        raise _unauthorized() from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise _unauthorized()
    return subject


def user_id_from_supabase_auth_api(
    authorization: str | None,
    *,
    supabase_url: str,
    service_role_key: str,
) -> str:
    token = bearer_token_from_authorization(authorization)
    if not supabase_url or not service_role_key:
        raise _unauthorized()

    try:
        response = httpx.get(
            f"{supabase_url.rstrip('/')}/auth/v1/user",
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=10,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise _unauthorized() from exc

    user_id = response.json().get("id")
    if not isinstance(user_id, str) or not user_id:
        raise _unauthorized()
    return user_id


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증된 사용자만 사용할 수 있습니다.",
    )
