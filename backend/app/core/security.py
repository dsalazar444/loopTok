from uuid import UUID

import jwt

from app.core.config import get_settings
from app.core.errors import InvalidTokenError


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
