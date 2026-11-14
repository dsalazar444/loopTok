import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.modules.users.models import User
from app.modules.auth.security import verify_password


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    testing_session = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    def override_db_session():
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_db_session] = (
        override_db_session
    )

    with TestClient(app) as test_client:
        yield test_client, testing_session

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_register_user(client):
    test_client, testing_session = client

    response = test_client.post(
        "/auth/register",
        json={
            "fullName": "Ana Torres",
            "username": "Ana_123",
            "password": "securePassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["fullName"] == "Ana Torres"
    assert data["username"] == "ana_123"
    assert "password" not in data
    assert "password_hash" not in data

    with testing_session() as session:
        user = session.scalar(
            select(User).where(User.username == "ana_123")
        )

        assert user is not None
        assert user.password_hash != "securePassword123"
        assert verify_password(
            "securePassword123",
            user.password_hash,
        )


def test_duplicate_username(client):
    test_client, _ = client

    first_user = {
        "fullName": "Ana Torres",
        "username": "Ana_123",
        "password": "securePassword123",
    }

    first_response = test_client.post(
        "/auth/register",
        json=first_user,
    )

    second_response = test_client.post(
        "/auth/register",
        json={
            **first_user,
            "username": "ANA_123",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]["code"]
        == "USERNAME_ALREADY_EXISTS"
    )


@pytest.mark.parametrize(
    "username,password",
    [
        ("ab", "securePassword123"),
        ("ana@123", "securePassword123"),
        ("ana123", "short"),
    ],
)
def test_invalid_registration(client, username, password):
    test_client, _ = client

    response = test_client.post(
        "/auth/register",
        json={
            "fullName": "Ana Torres",
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 422
