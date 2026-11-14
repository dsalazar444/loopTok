from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserResponse)
def read_current_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    return user
