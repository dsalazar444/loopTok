from enum import StrEnum

from fastapi import HTTPException, status


class ErrorCode(StrEnum):
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"


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
