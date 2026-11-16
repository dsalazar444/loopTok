import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

# must be set before the app is imported, Settings reads them at import time
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-with-at-least-32-bytes-long")

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.modules.sessions.models import UserSession
from app.modules.sessions.repository import SessionRepository
from app.modules.sessions.service import SessionService
from app.modules.users.models import User

LIMIT = timedelta(minutes=get_settings().session_inactivity_minutes)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def naive(value: datetime) -> datetime:
    # SQLite returns datetimes without tzinfo
    return value.replace(tzinfo=None)


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with sessionmaker(bind=engine, expire_on_commit=False)() as db_session:
        app.dependency_overrides[get_db_session] = lambda: db_session
        yield db_session

    app.dependency_overrides.clear()


@pytest.fixture
def client(session):
    return TestClient(app)


def make_user(session, username: str) -> User:
    user = User(full_name=username, username=username, password_hash="x")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def user(session):
    return make_user(session, "ana")


@pytest.fixture
def other_user(session):
    return make_user(session, "bob")


def headers_for(user: User) -> dict[str, str]:
    settings = get_settings()
    token = jwt.encode(
        {"sub": str(user.id), "exp": utcnow() + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


def add_session(session, user, *, idle: timedelta = timedelta(0), ended: bool = False) -> UserSession:
    last_seen = utcnow() - idle
    row = UserSession(
        user_id=user.id,
        created_at=last_seen - timedelta(minutes=1),
        last_seen_at=last_seen,
        ended_at=last_seen if ended else None,
        end_reason="logout" if ended else None,
    )
    session.add(row)
    session.commit()
    return row


def reload(session, session_id) -> UserSession:
    return session.get(UserSession, session_id, populate_existing=True)


# --- start ---

def test_start_creates_an_open_session(client, session, user):
    session_id = uuid4()

    response = client.post("/sessions", json={"session_id": str(session_id)}, headers=headers_for(user))

    assert response.status_code == 204
    saved = reload(session, session_id)
    assert saved.user_id == user.id
    assert saved.ended_at is None


def test_start_twice_is_idempotent(client, session, user):
    session_id = uuid4()
    body = {"session_id": str(session_id)}

    first = client.post("/sessions", json=body, headers=headers_for(user))
    second = client.post("/sessions", json=body, headers=headers_for(user))

    assert (first.status_code, second.status_code) == (204, 204)
    assert session.scalar(select(func.count()).select_from(UserSession)) == 1


def test_start_with_an_id_owned_by_another_user_is_not_found(client, session, user, other_user):
    row = add_session(session, other_user)

    response = client.post("/sessions", json={"session_id": str(row.id)}, headers=headers_for(user))

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SESSION_NOT_FOUND"


def test_start_with_an_expired_id_asks_for_a_new_one(client, session, user):
    row = add_session(session, user, ended=True)

    response = client.post("/sessions", json={"session_id": str(row.id)}, headers=headers_for(user))

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "SESSION_EXPIRED"


# --- heartbeat ---

def test_heartbeat_updates_last_seen(client, session, user):
    row = add_session(session, user, idle=timedelta(minutes=5))
    before = naive(row.last_seen_at)

    response = client.post(f"/sessions/{row.id}/heartbeat", headers=headers_for(user))

    assert response.status_code == 204
    saved = reload(session, row.id)
    assert saved.last_seen_at > before
    assert saved.ended_at is None


def test_heartbeat_after_the_inactivity_limit_closes_it_at_the_last_heartbeat(client, session, user):
    row = add_session(session, user, idle=LIMIT + timedelta(minutes=1))
    last_seen = naive(row.last_seen_at)

    response = client.post(f"/sessions/{row.id}/heartbeat", headers=headers_for(user))

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "SESSION_EXPIRED"
    saved = reload(session, row.id)
    assert saved.end_reason == "inactivity"
    assert saved.ended_at == last_seen  # not "now": the idle gap is not part of the session


def test_heartbeat_on_an_ended_session_is_expired(client, session, user):
    row = add_session(session, user, ended=True)

    response = client.post(f"/sessions/{row.id}/heartbeat", headers=headers_for(user))

    assert response.status_code == 409
    assert reload(session, row.id).end_reason == "logout"  # untouched


def test_heartbeat_unknown_or_foreign_session_is_not_found(client, session, user, other_user):
    foreign = add_session(session, other_user)

    for session_id in (uuid4(), foreign.id):
        response = client.post(f"/sessions/{session_id}/heartbeat", headers=headers_for(user))

        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "SESSION_NOT_FOUND"


# --- end ---

def test_end_closes_with_logout(client, session, user):
    row = add_session(session, user)

    response = client.post(f"/sessions/{row.id}/end", headers=headers_for(user))

    assert response.status_code == 204
    saved = reload(session, row.id)
    assert saved.end_reason == "logout"
    assert abs(saved.ended_at - naive(utcnow())) < timedelta(seconds=30)


def test_end_twice_keeps_the_first_end(client, session, user):
    row = add_session(session, user)

    client.post(f"/sessions/{row.id}/end", headers=headers_for(user))
    first_end = reload(session, row.id).ended_at
    response = client.post(f"/sessions/{row.id}/end", headers=headers_for(user))

    assert response.status_code == 204
    assert reload(session, row.id).ended_at == first_end


def test_end_after_the_inactivity_limit_records_the_last_heartbeat(client, session, user):
    row = add_session(session, user, idle=LIMIT + timedelta(minutes=1))
    last_seen = naive(row.last_seen_at)

    response = client.post(f"/sessions/{row.id}/end", headers=headers_for(user))

    assert response.status_code == 204
    saved = reload(session, row.id)
    assert saved.end_reason == "inactivity"
    assert saved.ended_at == last_seen


def test_end_unknown_or_foreign_session_is_not_found(client, session, user, other_user):
    foreign = add_session(session, other_user)

    for session_id in (uuid4(), foreign.id):
        response = client.post(f"/sessions/{session_id}/end", headers=headers_for(user))

        assert response.status_code == 404

    assert reload(session, foreign.id).ended_at is None  # the other user's session is untouched


# --- auth and input ---

@pytest.mark.parametrize(
    "method, path",
    [
        ("post", "/sessions"),
        ("post", f"/sessions/{uuid4()}/heartbeat"),
        ("post", f"/sessions/{uuid4()}/end"),
    ],
)
def test_requires_a_valid_token(client, method, path):
    response = getattr(client, method)(path, json={"session_id": str(uuid4())})

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


def test_rejects_a_session_id_that_is_not_a_uuid(client, user):
    assert client.post("/sessions", json={"session_id": "nope"}, headers=headers_for(user)).status_code == 422
    assert client.post("/sessions/nope/heartbeat", headers=headers_for(user)).status_code == 422
    assert client.post("/sessions/nope/end", headers=headers_for(user)).status_code == 422


# --- cleaner (scripts/close_idle_sessions.py) ---

def test_close_idle_closes_only_idle_open_sessions(session, user, other_user):
    idle = add_session(session, user, idle=LIMIT + timedelta(minutes=1))
    idle_of_other_user = add_session(session, other_user, idle=LIMIT + timedelta(hours=3))
    recent = add_session(session, user, idle=timedelta(minutes=5))
    already_ended = add_session(session, user, idle=LIMIT + timedelta(hours=1), ended=True)
    idle_last_seen = naive(idle.last_seen_at)

    closed = SessionService(session).close_idle()

    assert closed == 2
    assert reload(session, idle.id).end_reason == "inactivity"
    assert reload(session, idle.id).ended_at == idle_last_seen  # last heartbeat, not "now"
    assert reload(session, idle_of_other_user.id).end_reason == "inactivity"
    assert reload(session, recent.id).ended_at is None
    assert reload(session, already_ended.id).end_reason == "logout"  # untouched


def test_close_idle_can_run_repeatedly(session, user):
    add_session(session, user, idle=LIMIT + timedelta(minutes=1))
    service = SessionService(session)

    assert service.close_idle() == 1
    assert service.close_idle() == 0


# --- repository ---

def test_create_if_absent_survives_a_concurrent_insert(session, user):
    row = add_session(session, user)
    session.expunge_all()  # as in the real race: this request has not seen the row yet

    repo = SessionRepository(session)
    with patch.object(repo, "get", return_value=None):  # "absent" when checked, inserted by someone else meanwhile
        repo.create_if_absent(row.id, user.id, utcnow())  # must not raise

    assert session.scalar(select(func.count()).select_from(UserSession)) == 1
