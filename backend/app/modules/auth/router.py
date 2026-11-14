from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.modules.auth.schemas import RegisterRequest
from app.modules.auth.service import AuthService
from app.modules.users.schemas import UserResponse
from app.modules.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    session: Annotated[Session, Depends(get_db_session)],
) -> User:
    service = AuthService(session)

    return service.register(request)
