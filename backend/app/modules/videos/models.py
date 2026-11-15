from datetime import date

from sqlalchemy import JSON, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class Video(BaseModel):
    __tablename__ = "videos"
    # Imported columns:
    # created_at (DateTime)
    # modified_at (DateTime)

    # overrides BaseModel's UUID id: this is the YouTube video id, not backend-generated
    id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )

    subcategory: Mapped[str | None] = mapped_column(
        String(50),
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        server_default="en",
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    creator: Mapped[str | None] = mapped_column(
        String(100),
    )

    # shortcut: JSON list instead of Postgres TEXT[], so model/tests also work against SQLite. Switch to
    # postgresql.ARRAY(String) if tag filtering needs real array operators (e.g. "contains").
    tags: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )

    upload_date: Mapped[date | None] = mapped_column(
        Date,
    )

    s3_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
