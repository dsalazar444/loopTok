from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.dislikes.service import DislikeService

router = APIRouter(
    prefix="/videos",
    tags=["Dislikes"],
)


@router.post(
    "/{video_id}/dislike",
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_dislike(
    video_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    DislikeService(session).add_dislike(
        user_id=current_user.id,
        video_id=video_id,
    )


@router.delete(
    "/{video_id}/dislike",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_dislike(
    video_id: str,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    DislikeService(session).remove_dislike(
        user_id=current_user.id,
        video_id=video_id,
    )
