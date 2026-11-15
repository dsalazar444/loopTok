from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.likes.service import LikeService

router = APIRouter(
    prefix="/videos",
    tags=["Likes"],
)

@router.post(
    "/{video_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_like(
    video_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    LikeService(session).add_like(
        user_id=current_user.id,
        video_id=video_id,
    )


@router.delete(
    "/{video_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_like(
    video_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    LikeService(session).remove_like(
        user_id=current_user.id,
        video_id=video_id,
    )