from enum import Enum
from fastapi import HTTPException, status

class ErrorCode(str, Enum):
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    VIDEO_NOT_FOUND = "VIDEO_NOT_FOUND"

class AppException(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        code: ErrorCode,
        message: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
            },
        )

class UsernameAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.USERNAME_ALREADY_EXISTS,
            message="Username already exists",
        )

class InvalidTokenError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.INVALID_TOKEN,
            message="Invalid or expired token",
        )

class InvalidCredentialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.INVALID_CREDENTIALS,
            message="Invalid username or password",
        )

class VideoNotFoundError(AppException):
    def __init__(self, video_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.VIDEO_NOT_FOUND,
            message=f"Video with id {video_id} not found",
        )
