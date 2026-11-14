import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# must be set before the app is imported, Settings reads them at import time
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-with-at-least-32-bytes-long")

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.modules.users.models import User


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


def make_token(sub: str, expires_in: timedelta = timedelta(minutes=5)) -> str:
    settings = get_settings()
    payload = {"sub": sub, "exp": datetime.now(timezone.utc) + expires_in}

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_returns_current_user(client, session):
    user = User(full_name="Ana Perez", username="ana", password_hash="x")
    session.add(user)
    session.commit()

    response = client.get("/users/me", headers=auth(make_token(str(user.id))))

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "ana"
    assert body["fullName"] == "Ana Perez"
    assert "password_hash" not in body


@pytest.mark.parametrize(
    "headers",
    [
        {},
        auth("not-a-jwt"),
        auth(make_token(str(uuid4()), timedelta(minutes=-1))),  # expired
        auth(make_token("not-a-uuid")),
        auth(make_token(str(uuid4()))),  # valid token, user does not exist
    ],
)
def test_rejects_invalid_credentials(client, headers):
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"
