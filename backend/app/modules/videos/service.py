from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.likes.repository import LikeRepository
from app.modules.videos.repository import VideoRepository
from app.modules.videos.schemas import (VideoListResponse, VideoResponse)

class VideoService:
    def __init__(self, session: Session) -> None:
        self.video_repository = VideoRepository(session)
        self.like_repository = LikeRepository(session)

    def list_videos(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None = None,
        user_id: UUID | None = None,
    ) -> VideoListResponse:
        videos, total = self.video_repository.list_paginated(
            page=page,
            page_size=page_size,
            category=category,
            user_id=user_id,
        )

        video_ids = [video.id for video in videos]

        likes_counts = self.like_repository.get_likes_counts(video_ids)

        liked_video_ids = (
            self.like_repository.get_liked_video_ids(
                user_id=user_id,
                video_ids=video_ids,
            )
            if user_id is not None
            else set()
        )

        items = []

        for video in videos:
            video_response = VideoResponse.model_validate(video)

            video_response.likes_count = likes_counts.get(
                video.id,
                0,
            )

            video_response.is_liked = (
                video.id in liked_video_ids
            )

            items.append(video_response)

        return VideoListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )