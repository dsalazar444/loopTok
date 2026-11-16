from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.events.schemas import EventRequest
from app.modules.events.service import PlaybackService

router = APIRouter(
    prefix="/events",
    tags=["Event"],
)

@router.post(
    "/reproduction",
    status_code=status.HTTP_204_NO_CONTENT,
)
def ingest_playback_event(
    current_user: Annotated[User, Depends(get_current_user)], # es obligatorio estar logueado -> obtenemos su identidad del JWT
    event: EventRequest
) -> None:
    playback_service = PlaybackService()
    playback_service.publish_playback_event(user_id=current_user.id, event=event)
