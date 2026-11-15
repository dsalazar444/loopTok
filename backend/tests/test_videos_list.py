import os
from datetime import date

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-with-at-least-32-bytes-long")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.modules.videos.models import Video


def make_video(index: int, category: str = "cooking_food") -> Video:
    return Video(
        id=f"video-{index:03d}",
        title=f"Video {index}",
        description="desc",
        category=category,
        duration_seconds=60,
        tags=[],
        upload_date=date(2026, 1, 1),
        s3_key=f"test/out/videos/video-{index:03d}.mp4",
    )


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


def test_lists_videos_with_default_pagination(client, session):
    for i in range(3):
        session.add(make_video(i))
    session.commit()

    response = client.get("/videos")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["pageSize"] == 20
    assert len(body["items"]) == 3
    assert body["items"][0]["s3Key"].startswith("test/out/videos/")


def test_paginates_results(client, session):
    for i in range(5):
        session.add(make_video(i))
    session.commit()

    response = client.get("/videos", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["page"] == 2
    assert len(body["items"]) == 2


def test_filters_by_category(client, session):
    session.add(make_video(0, category="cooking_food"))
    session.add(make_video(1, category="animation_edu"))
    session.commit()

    response = client.get("/videos", params={"category": "animation_edu"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["category"] == "animation_edu"


def test_rejects_invalid_page(client, session):
    response = client.get("/videos", params={"page": 0})

    assert response.status_code == 422
