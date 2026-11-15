"""Insert real sample videos into the `videos` table for local testing.

Data comes from test/raw/*.info.json (yt-dlp metadata) and the youtube-shorts
dataset (category). The mp4 files live under test/out/videos for now.

Run once: .venv/Scripts/python scripts/seed_videos.py
"""
from datetime import date

from app.db.session import SessionLocal
from app.modules.videos.models import Video

# shortcut: s3_key points at the local test/out/videos path, there is no S3/MinIO yet.
# Swap for the real bucket key (e.g. "videos/<id>.mp4") once Persona B sets up storage.
VIDEOS = [
    Video(
        id="6yyP-agq9c",
        title="What happens when @gordonramsay Hugh Jackman & @VancityReynolds get two tortillas ? This.",
        description="Gordon Ramsay shorts clip.",  # info.json description was empty
        category="cooking_food",
        language="en",
        duration_seconds=60,
        creator="Gordon Ramsay",
        tags=[],
        upload_date=date(2024, 7, 29),
        url="https://www.youtube.com/watch?v=-6yyP-agq9c",
    ),
    Video(
        id="Pw40-IoL5kY",
        title="Trust the process #shorts",
        description=(
            "Take a look behind the scenes of our video, “The Opposites "
            "Game”, animated by Anna Samo and Lisa LaBracio!"
        ),
        category="animation_edu",
        language="en",
        duration_seconds=60,
        creator="TED-Ed",
        tags=[],
        upload_date=date(2023, 4, 28),
        url="test/out/videos/Pw40-IoL5kY.mp4",
    ),
]


def seed() -> None:
    with SessionLocal() as session:
        for video in VIDEOS:
            if session.get(Video, video.id) is not None:
                print(f"skip (already exists): {video.id}")
                continue

            session.add(video)
            print(f"inserted: {video.id}")

        session.commit()


if __name__ == "__main__":
    seed()
