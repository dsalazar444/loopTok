from datetime import datetime
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.sessions.models import UserSession


class SessionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, session_id: UUID) -> UserSession | None:
        # populate_existing: bulk UPDATEs below must not leave a stale copy in the session
        return self.session.get(UserSession, session_id, populate_existing=True)

    def create_if_absent(self, session_id: UUID, user_id: UUID, now: datetime) -> None:
        if self.get(session_id) is not None:
            return

        try:
            self.session.add(
                UserSession(
                    id=session_id,
                    user_id=user_id,
                    created_at=now,
                    last_seen_at=now,
                )
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()  

    # True only if the session is open, belongs to the user and was active after `cutoff`
    def touch(
        self,
        session_id: UUID,
        user_id: UUID,
        now: datetime,
        cutoff: datetime,
    ) -> bool:
        stmt = (
            update(UserSession)
            .where(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
                UserSession.ended_at.is_(None),
                UserSession.last_seen_at >= cutoff,
            )
            .values(last_seen_at=now)
        )

        return self.session.execute(stmt).rowcount == 1

    # closes every open session idle since before `cutoff`; its end is the last heartbeat, never "now".
    def close_idle(self, cutoff: datetime) -> int:
        stmt = (
            update(UserSession)
            .where(
                UserSession.ended_at.is_(None),
                UserSession.last_seen_at < cutoff,
            )
            .values(ended_at=UserSession.last_seen_at, end_reason="inactivity")
        )

        return self.session.execute(stmt).rowcount

    # True only if an open session of the user was closed; `active_since` also requires recent activity
    def close(
        self,
        session_id: UUID,
        user_id: UUID,
        ended_at: datetime,
        reason: str,
        active_since: datetime | None = None,
    ) -> bool:
        stmt = update(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user_id,
            UserSession.ended_at.is_(None),
        )

        if active_since is not None:
            stmt = stmt.where(UserSession.last_seen_at >= active_since)

        stmt = stmt.values(ended_at=ended_at, end_reason=reason)

        return self.session.execute(stmt).rowcount == 1
