from unittest.mock import MagicMock
from uuid import uuid4
import pytest

from app.modules.not_interested.service import NotInterestedService
from app.modules.videos.models import Video
from app.core.errors import VideoNotFoundError


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def service(session):
    service = NotInterestedService(session)

    service.not_interested_repository = MagicMock()
    service.like_repository = MagicMock()
    service.video_repository = MagicMock()

    return service


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def video_id():
    return "test_video_123"


def test_add_not_interested_success(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.add_not_interested(user_id, video_id)

    service.video_repository.get_by.assert_called_once_with(Video.id, video_id)
    service.not_interested_repository.add_not_interested.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )
    session.commit.assert_called_once()


def test_add_not_interested_removes_like(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.add_not_interested(user_id, video_id)

    # the (user, video) advisory lock is what makes "last action wins" safe under concurrency
    session.execute.assert_called_once()

    service.like_repository.remove_like.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )


def test_add_not_interested_video_not_found(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = None

    with pytest.raises(VideoNotFoundError):
        service.add_not_interested(user_id, video_id)

    service.not_interested_repository.add_not_interested.assert_not_called()
    session.commit.assert_not_called()


def test_remove_not_interested_success(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.remove_not_interested(user_id, video_id)

    service.not_interested_repository.remove_not_interested.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )
    session.commit.assert_called_once()


def test_remove_not_interested_video_not_found(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = None

    with pytest.raises(VideoNotFoundError):
        service.remove_not_interested(user_id, video_id)

    service.not_interested_repository.remove_not_interested.assert_not_called()
    session.commit.assert_not_called()


def test_add_not_interested_repository_error(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()
    service.not_interested_repository.add_not_interested.side_effect = RuntimeError("Database error")

    with pytest.raises(RuntimeError, match="Database error"):
        service.add_not_interested(user_id, video_id)

    session.commit.assert_not_called()
