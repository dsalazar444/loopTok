from unittest.mock import MagicMock
from uuid import uuid4
import pytest

from app.modules.dislikes.service import DislikeService
from app.modules.videos.models import Video
from app.core.errors import VideoNotFoundError


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def service(session):
    service = DislikeService(session)

    service.dislike_repository = MagicMock()
    service.like_repository = MagicMock()
    service.video_repository = MagicMock()

    return service


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def video_id():
    return "test_video_123"


def test_add_dislike_success(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.add_dislike(user_id, video_id)

    service.video_repository.get_by.assert_called_once_with(Video.id, video_id)
    service.dislike_repository.add_dislike.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )
    session.commit.assert_called_once()


def test_add_dislike_removes_like(service, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.add_dislike(user_id, video_id)

    service.like_repository.remove_like.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )


def test_add_dislike_video_not_found(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = None

    with pytest.raises(VideoNotFoundError):
        service.add_dislike(user_id, video_id)

    service.dislike_repository.add_dislike.assert_not_called()
    session.commit.assert_not_called()


def test_remove_dislike_success(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.remove_dislike(user_id, video_id)

    service.dislike_repository.remove_dislike.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )
    session.commit.assert_called_once()


def test_remove_dislike_video_not_found(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = None

    with pytest.raises(VideoNotFoundError):
        service.remove_dislike(user_id, video_id)

    service.dislike_repository.remove_dislike.assert_not_called()
    session.commit.assert_not_called()


def test_add_dislike_repository_error(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()
    service.dislike_repository.add_dislike.side_effect = RuntimeError("Database error")

    with pytest.raises(RuntimeError, match="Database error"):
        service.add_dislike(user_id, video_id)

    session.commit.assert_not_called()
