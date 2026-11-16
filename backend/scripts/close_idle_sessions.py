"""Close user sessions that have had no heartbeat for longer than SESSION_INACTIVITY_MINUTES.

The end of each closed session is its last heartbeat, so the idle gap never counts as session time.
Safe to run any number of times; meant to run every 5 minutes.

Run from backend/: python -m scripts.close_idle_sessions
"""
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.modules.sessions.service import SessionService


def close_idle_sessions() -> int:
    with SessionLocal() as session:
        return SessionService(session).close_idle()


if __name__ == "__main__":
    closed = close_idle_sessions()
    print(f"{datetime.now(timezone.utc).isoformat()} closed {closed} idle session(s)")
