from __future__ import annotations

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError


def user_id_from_supabase_token(authorization: str | None, jwt_secret: str) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise _unauthorized()

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise _unauthorized()

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


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증된 사용자만 사용할 수 있습니다.",
    )
