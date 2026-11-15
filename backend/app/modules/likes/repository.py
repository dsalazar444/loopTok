from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.likes.models import Like

class LikeRepository:
    def __init__(self, session: Session):
        self.session = session

    # add_like and remove_like are idempotents
    def add_like(self, user_id: UUID, video_id: str) -> None:
        stmt = (
            insert(Like)
            .values(
                user_id=user_id,
                video_id=video_id,
            )
            .on_conflict_do_nothing(
                constraint="uq_likes_user_video"
            )
        )

        self.session.execute(stmt)

    def remove_like(self, user_id: UUID, video_id: str) -> None:
        stmt = (
            delete(Like)
            .where(
                Like.user_id == user_id,
                Like.video_id == video_id,
            )
        )

        self.session.execute(stmt)

    def is_liked(self, user_id: UUID, video_id: str) -> bool:
        stmt = (
            select(Like.id)
            .where(
                Like.user_id == user_id,
                Like.video_id == video_id,
            )
            .limit(1)
        )

        return self.session.scalar(stmt) is not None

    def get_likes_count(self, video_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(Like)
            .where(Like.video_id == video_id)
        )

        return self.session.scalar(stmt) or 0