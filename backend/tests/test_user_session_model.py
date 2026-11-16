import os
from datetime import datetime, timezone
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-with-at-least-32-bytes-long")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.sessions.models import UserSession
from app.modules.users.models import User


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with sessionmaker(bind=engine)() as session:
        user = User(full_name="T", username="tester", password_hash="x")
        session.add(user)
        session.commit()
        session.user_id = user.id
        yield session


def test_open_session_uses_client_id_and_defaults(db):
    session_id = uuid4()
    db.add(UserSession(id=session_id, user_id=db.user_id))
    db.commit()

    saved = db.get(UserSession, session_id)

    assert saved.created_at is not None
    assert saved.last_seen_at is not None
    assert saved.ended_at is None
    assert saved.end_reason is None


def test_closed_session_accepts_known_reasons(db):
    db.add(
        UserSession(
            user_id=db.user_id,
            ended_at=datetime.now(timezone.utc),
            end_reason="inactivity",
        )
    )
    db.commit()


@pytest.mark.parametrize(
    "ended_at, end_reason",
    [
        (None, "logout"),  # reason without end time
        (datetime(2026, 1, 1, tzinfo=timezone.utc), None),  # end time without reason
        (datetime(2026, 1, 1, tzinfo=timezone.utc), "whatever"),  # unknown reason
    ],
)
def test_rejects_inconsistent_end_state(db, ended_at, end_reason):
    db.add(UserSession(user_id=db.user_id, ended_at=ended_at, end_reason=end_reason))

    with pytest.raises(IntegrityError):
        db.commit()
