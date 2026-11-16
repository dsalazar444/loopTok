from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class UserSession(BaseModel):
    """One visit of a logged-in user. `id` is the session_id sent by the frontend."""

    __tablename__ = "user_sessions"
    # Imported columns:
    # id (UUID) -> session_id
    # created_at (DateTime) -> session_started
    # modified_at (DateTime)

    __table_args__ = (
        # ended_at and end_reason are set together, so session data stays unambiguous
        CheckConstraint(
            "(ended_at IS NULL AND end_reason IS NULL) OR "
            "(ended_at IS NOT NULL AND end_reason IS NOT NULL "
            "AND end_reason IN ('logout', 'inactivity'))",  # IS NOT NULL: a NULL reason would otherwise pass the CHECK
            name="ck_user_sessions_end_state",
        ),
        # the idle-session cleaner only looks at open sessions
        Index(
            "ix_user_sessions_open_last_seen",
            "last_seen_at",
            postgresql_where=text("ended_at IS NULL"),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    end_reason: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
