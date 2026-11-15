from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.dislikes.models import Dislike


class DislikeRepository:
    def __init__(self, session: Session):
        self.session = session

    # add_dislike and remove_dislike are idempotent
    def add_dislike(self, user_id: UUID, video_id: str) -> None:
        stmt = (
            insert(Dislike)
            .values(
                user_id=user_id,
                video_id=video_id,
            )
            .on_conflict_do_nothing(
                constraint="uq_dislikes_user_video"
            )
        )

        self.session.execute(stmt)

    def remove_dislike(self, user_id: UUID, video_id: str) -> None:
        stmt = (
            delete(Dislike)
            .where(
                Dislike.user_id == user_id,
                Dislike.video_id == video_id,
            )
        )

        self.session.execute(stmt)
