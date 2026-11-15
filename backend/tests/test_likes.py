from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modules.likes.service import LikeService
from app.modules.videos.models import Video
from app.core.errors import VideoNotFoundError


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def service(session):
    service = LikeService(session)

    service.like_repository = MagicMock()
    service.not_interested_repository = MagicMock()
    service.video_repository = MagicMock()

    return service


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def video_id():
    return "test_video_123"


def test_add_like_success(service, session, user_id, video_id):
    # Arrange
    service.video_repository.get_by.return_value = MagicMock()

    # Act
    service.add_like(user_id, video_id)

    # Assert
    service.video_repository.get_by.assert_called_once_with(
        Video.id,
        video_id,
    )

    service.like_repository.add_like.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )

    session.commit.assert_called_once()


def test_add_like_removes_not_interested(service, session, user_id, video_id):
    service.video_repository.get_by.return_value = MagicMock()

    service.add_like(user_id, video_id)

    # the (user, video) advisory lock is what makes "last action wins" safe under concurrency
    session.execute.assert_called_once()

    service.not_interested_repository.remove_not_interested.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )


def test_add_like_video_not_found(
    service,
    session,
    user_id,
    video_id,
):
    # Arrange
    service.video_repository.get_by.return_value = None

    # Act & Assert
    with pytest.raises(VideoNotFoundError):
        service.add_like(user_id, video_id)

    service.like_repository.add_like.assert_not_called()
    session.commit.assert_not_called()


def test_remove_like_success(
    service,
    session,
    user_id,
    video_id,
):
    # Arrange
    service.video_repository.get_by.return_value = MagicMock()

    # Act
    service.remove_like(user_id, video_id)

    # Assert
    service.video_repository.get_by.assert_called_once_with(
        Video.id,
        video_id,
    )

    service.like_repository.remove_like.assert_called_once_with(
        user_id=user_id,
        video_id=video_id,
    )

    session.commit.assert_called_once()


def test_remove_like_video_not_found(
    service,
    session,
    user_id,
    video_id,
):
    # Arrange
    service.video_repository.get_by.return_value = None

    # Act & Assert
    with pytest.raises(VideoNotFoundError):
        service.remove_like(user_id, video_id)

    service.like_repository.remove_like.assert_not_called()
    session.commit.assert_not_called()


def test_add_like_repository_error(
    service,
    session,
    user_id,
    video_id,
):
    # Arrange
    service.video_repository.get_by.return_value = MagicMock()

    service.like_repository.add_like.side_effect = RuntimeError(
        "Database error"
    )

    # Act & Assert
    with pytest.raises(RuntimeError, match="Database error"):
        service.add_like(user_id, video_id)

    session.commit.assert_not_called()