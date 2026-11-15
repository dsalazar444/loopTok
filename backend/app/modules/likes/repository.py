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

    # para saber si un video especifico fue dado like por un usuario especifico
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

    # obtener ids de todos los videos a los que un usuario les ha dado like -> util para que en GET /videos, se mande esta info para todos los videos mandados, de una vez
    def get_liked_video_ids(
        self,
        user_id: UUID,
        video_ids: list[str],
    ) -> set[str]:
        if not video_ids:
            return set()

        statement = (
            select(Like.video_id)
            .where(
                Like.user_id == user_id,
                Like.video_id.in_(video_ids),
            )
        )

        return set(self.session.scalars(statement).all())

    # obtener cuenta de cantidad de likes para un video especifico 
    def get_likes_count(self, video_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(Like)
            .where(Like.video_id == video_id)
        )

        return self.session.scalar(stmt) or 0

    # obtener cantidad de likes para una lista de videos
    def get_likes_counts(
        self,
        video_ids: list[str],
    ) -> dict[str, int]:
        if not video_ids:
            return {}

        statement = (
            select(
                Like.video_id,
                func.count(Like.id),
            )
            .where(Like.video_id.in_(video_ids))
            .group_by(Like.video_id)
        )

        results = self.session.execute(statement).all()

        return {
            video_id: count for video_id, count in results
        }

