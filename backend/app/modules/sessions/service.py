from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import SessionExpiredError, SessionNotFoundError
from app.modules.sessions.models import UserSession
from app.modules.sessions.repository import SessionRepository


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.session_repository = SessionRepository(session)

    # session_started: idempotent, so a repeated request just counts as activity
    def start(self, user_id: UUID, session_id: UUID) -> None:
        now = _utcnow()

        self.session_repository.create_if_absent(session_id, user_id, now)
        self._touch_or_expire(user_id, session_id, now)

    # session_heartbeat
    def heartbeat(self, user_id: UUID, session_id: UUID) -> None:
        self._touch_or_expire(user_id, session_id, _utcnow())

    # session_ended (logout): idempotent, ending an already ended session is not an error
    def end(self, user_id: UUID, session_id: UUID) -> None:
        now = _utcnow()

        closed = self.session_repository.close(
            session_id,
            user_id,
            ended_at=now,
            reason="logout",
            active_since=self._cutoff(now),
        )

        if not closed:
            current = self._get_owned(session_id, user_id)

            if current.ended_at is None:
                self._close_as_inactive(current)

        self.session.commit()

    # used by scripts/close_idle_sessions.py; safe to run repeatedly
    def close_idle(self) -> int:
        closed = self.session_repository.close_idle(self._cutoff(_utcnow()))
        self.session.commit()

        return closed

    def _touch_or_expire(self, user_id: UUID, session_id: UUID, now: datetime) -> None:
        if self.session_repository.touch(session_id, user_id, now, self._cutoff(now)):
            self.session.commit()
            return

        current = self._get_owned(session_id, user_id)

        # open but idle past the limit and not yet closed by the cleaner script
        if current.ended_at is None:
            self._close_as_inactive(current)
            self.session.commit()

        raise SessionExpiredError()

    # the real end of an inactive session is its last heartbeat, never "now"
    def _close_as_inactive(self, current: UserSession) -> None:
        self.session_repository.close(
            current.id,
            current.user_id,
            ended_at=current.last_seen_at,
            reason="inactivity",
        )

    def _get_owned(self, session_id: UUID, user_id: UUID) -> UserSession:
        current = self.session_repository.get(session_id)

        if current is None or current.user_id != user_id:
            raise SessionNotFoundError()

        return current

    def _cutoff(self, now: datetime) -> datetime:
        return now - timedelta(minutes=get_settings().session_inactivity_minutes)
