import os
from datetime import date

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-with-at-least-32-bytes-long")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.videos.models import Video


def test_creates_and_reads_video_with_youtube_id():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with sessionmaker(bind=engine)() as session:
        session.add(
            Video(
                id="dQw4w9WgXcQ",  # YouTube video id, not a UUID
                title="Atardecer en la montaña",
                description="Un hermoso atardecer desde la cima.",
                category="Naturaleza",
                duration_seconds=180,
                tags=["sunset", "mountain"],
                upload_date=date(2026, 1, 1),
                url="https://www.youtube.com/watch?v=-6yyP-agq9c",
            )
        )
        session.commit()

        video = session.get(Video, "dQw4w9WgXcQ")

        assert video is not None
        assert video.language == "en"  # default applied
        assert video.subcategory is None
        assert video.tags == ["sunset", "mountain"]
        assert video.created_at is not None
