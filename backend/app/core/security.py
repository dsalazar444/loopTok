from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.core.config import get_settings
from app.core.errors import InvalidTokenError
from app.modules.auth.security import hash_password, verify_password


def create_access_token(
    user_id: UUID | str,
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    """Generate a signed JWT access token for the given user id.

    Returns a tuple containing:
      - encoded JWT string
      - expires_in duration in seconds
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
        expires_in = int(expires_delta.total_seconds())
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
        expires_in = settings.access_token_expire_minutes * 60

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expires_in


def decode_access_token(token: str) -> UUID:
    """Return the user id stored in the token's `sub` claim."""
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
        return UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError):
        raise InvalidTokenError() from None
