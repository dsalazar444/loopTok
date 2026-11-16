from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


def lock_user_video(session: Session, user_id: UUID, video_id: str) -> None:
    # Serializes like / not_interested changes for one (user, video) until commit,
    # so two simultaneous requests cannot both succeed and the last one always wins.
    # shortcut: PostgreSQL-only (advisory lock), switch to a row lock if the DB changes.
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
        {"key": f"{user_id}:{video_id}"},
    )
