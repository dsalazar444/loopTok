from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db_session
from app.modules.sessions.schemas import StartSessionRequest
from app.modules.sessions.service import SessionService
from app.modules.users.models import User

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def start_session(
    body: StartSessionRequest,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    SessionService(session).start(
        user_id=current_user.id,
        session_id=body.session_id,
    )


@router.post("/{session_id}/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
def heartbeat(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    SessionService(session).heartbeat(
        user_id=current_user.id,
        session_id=session_id,
    )


@router.post("/{session_id}/end", status_code=status.HTTP_204_NO_CONTENT)
def end_session(
    session_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    SessionService(session).end(
        user_id=current_user.id,
        session_id=session_id,
    )
