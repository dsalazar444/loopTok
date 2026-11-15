from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.not_interested.models import NotInterested


class NotInterestedRepository:
    def __init__(self, session: Session):
        self.session = session

    # add_not_interested and remove_not_interested are idempotent
    def add_not_interested(self, user_id: UUID, video_id: str) -> None:
        stmt = (
            insert(NotInterested)
            .values(
                user_id=user_id,
                video_id=video_id,
            )
            .on_conflict_do_nothing(
                constraint="uq_not_interested_user_video"
            )
        )

        self.session.execute(stmt)

    def remove_not_interested(self, user_id: UUID, video_id: str) -> None:
        stmt = (
            delete(NotInterested)
            .where(
                NotInterested.user_id == user_id,
                NotInterested.video_id == video_id,
            )
        )

        self.session.execute(stmt)
