from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Dislike(BaseModel):
    __tablename__ = "dislikes"
    # Imported columns:
    # id (UUID)
    # created_at (DateTime)
    # modified_at (DateTime)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "video_id",
            name="uq_dislikes_user_video",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    video_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
    )
