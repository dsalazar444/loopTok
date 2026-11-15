from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.db.session import get_db_session
from app.modules.videos.repository import VideoRepository
from app.modules.videos.schemas import VideoListResponse
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/videos",
    tags=["Videos"],
)


@router.get("", response_model=VideoListResponse)
def list_videos(
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    category: Annotated[str | None, Query()] = None,
) -> VideoListResponse:
    items, total = VideoRepository(session).list_paginated(
        page=page,
        page_size=page_size,
        category=category,
    )

    return VideoListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
