import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-with-at-least-32-bytes-long")

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
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


@pytest.fixture
def test_user(session):
    user = User(
        full_name="Carlos Gomez",
        username="carlos_dev",
        password_hash=hash_password("MySecretPassword123!"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# 1. Login with correct credentials
def test_login_successful(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "username": "carlos_dev",
            "password": "MySecretPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600


# 2. Login with non-existent user
def test_login_nonexistent_user(client, session):
    response = client.post(
        "/auth/login",
        json={
            "username": "unknown_user_999",
            "password": "AnyPassword123!",
        },
    )

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_CREDENTIALS"
    assert detail["message"] == "Invalid username or password"


# 3. Login with wrong password
def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "username": "carlos_dev",
            "password": "WrongPassword456!",
        },
    )

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_CREDENTIALS"
    assert detail["message"] == "Invalid username or password"


# 4. Request with missing fields (422)
@pytest.mark.parametrize(
    "payload",
    [
        {"username": "carlos_dev"},
        {"password": "MySecretPassword123!"},
        {},
        {"username": "", "password": "MySecretPassword123!"},
        {"username": "carlos_dev", "password": ""},
    ],
)
def test_login_missing_or_invalid_fields(client, payload):
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 422


# 5. JWT generation with correct claims
def test_jwt_claims(client, test_user):
    before_login = datetime.now(timezone.utc).timestamp()

    response = client.post(
        "/auth/login",
        json={
            "username": "carlos_dev",
            "password": "MySecretPassword123!",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == str(test_user.id)
    assert "iat" in payload
    assert "exp" in payload
    assert payload["iat"] >= int(before_login) - 2
    assert payload["exp"] - payload["iat"] == 3600


# 6. Rejection of expired JWT
def test_reject_expired_jwt(client):
    expired_token, _ = create_access_token(
        user_id=uuid4(),
        expires_delta=timedelta(seconds=-10),
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


# 7. Rejection of JWT with invalid signature
def test_reject_invalid_signature_jwt(client, test_user):
    payload = {
        "sub": str(test_user.id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    tampered_token = jwt.encode(
        payload,
        "completely-different-and-wrong-secret-key-32-bytes",
        algorithm="HS256",
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


# 8. Access /users/me with valid token
def test_access_users_me_valid_token(client, test_user):
    login_response = client.post(
        "/auth/login",
        json={
            "username": "carlos_dev",
            "password": "MySecretPassword123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(test_user.id)
    assert body["username"] == "carlos_dev"
    assert body["fullName"] == "Carlos Gomez"
    assert "createdAt" in body
    assert "password" not in body
    assert "password_hash" not in body


# 9. Access /users/me without token
def test_access_users_me_without_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


# 10. Access /users/me with invalid token
def test_access_users_me_with_malformed_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


# 11. Access /users/me with valid token whose user was deleted
def test_access_users_me_deleted_user(client, session, test_user):
    token, _ = create_access_token(user_id=test_user.id)

    # Delete the user from the database
    session.delete(test_user)
    session.commit()

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"

