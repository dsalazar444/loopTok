from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.likes.repository import LikeRepository
from app.modules.videos.models import Video
from app.modules.videos.repository import VideoRepository
from app.core.errors import VideoNotFoundError

class LikeService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.like_repository = LikeRepository(session)
        self.video_repository = VideoRepository(session)

    def add_like(self, user_id: UUID, video_id: str) -> None:
        self._validate_video_exists(video_id)

        self.like_repository.add_like(
            user_id=user_id,
            video_id=video_id,
        )

        self.session.commit()

    def remove_like(self, user_id: UUID, video_id: str) -> None:
        self._validate_video_exists(video_id)

        self.like_repository.remove_like(
            user_id=user_id,
            video_id=video_id,
        )

        self.session.commit()

    def _validate_video_exists(self, video_id: str) -> None:
        video = self.video_repository.get_by(
            Video.id,
            video_id,
        )

        if video is None:
            raise VideoNotFoundError(video_id)