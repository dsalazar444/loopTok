from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import InvalidTokenError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

# auto_error=False so a missing header also returns our own error format
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> User:
    if credentials is None:
        raise InvalidTokenError()

    user_id = decode_access_token(credentials.credentials)
    user = UserRepository(session).get_by_id(user_id)

    if user is None:
        raise InvalidTokenError()

    return user
