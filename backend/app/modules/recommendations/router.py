from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.recommendations.service import RecommendationService

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)

@router.get(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def get_recommendations(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    user_id = current_user.id

    service = RecommendationService()
    service.get_recommendations(user_id=user_id)

