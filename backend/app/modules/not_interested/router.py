from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.not_interested.service import NotInterestedService

router = APIRouter(
    prefix="/videos",
    tags=["Not interested"],
)


@router.post(
    "/{video_id}/not-interested",
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_not_interested(
    video_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    NotInterestedService(session).add_not_interested(
        user_id=current_user.id,
        video_id=video_id,
    )


@router.delete(
    "/{video_id}/not-interested",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_not_interested(
    video_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    NotInterestedService(session).remove_not_interested(
        user_id=current_user.id,
        video_id=video_id,
    )
