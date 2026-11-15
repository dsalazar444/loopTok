from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.db.session import get_db_session
from app.core.dependencies import get_optional_user
from app.modules.videos.schemas import VideoListResponse
from app.modules.users.models import User
from app.modules.videos.service import VideoService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/videos",
    tags=["Videos"],
)

@router.get("", response_model=VideoListResponse)
def list_videos(
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User | None, Depends(get_optional_user)], 
    # añadido porque este endpoint mandará tambien likesCounts, y usersLikes, entonces si es autenticado, userLikes se consultará y enviará, pero si no, se mandará vacio
    # y mientras que likesCount no necesita estar autenticado, userLikes si, pues tiene los videos a los que el user le dio like. Por eso necesitamos que puedan acceder tanto si tienen JWT (y se verifica) como si no
    # GET /videos continúa siendo público, pero cuando recibe un JWT válido puede identificar cuáles videos tienen like del usuario.
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 7,
    category: Annotated[str | None, Query()] = None,
) -> VideoListResponse:
    return VideoService(session).list_videos(
        page=page,
        page_size=page_size,
        category=category,
        user_id=current_user.id if current_user else None,
    )