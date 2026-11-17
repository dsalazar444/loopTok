from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.core.errors import EventPublishFailedError
from app.core.kafka_producer import KafkaPublishError, get_kafka_producer, get_kafka_settings
from app.modules.users.models import User
from app.modules.events.schemas import EventRequest
from app.modules.events.service import PlaybackService

router = APIRouter(
    prefix="/events",
    tags=["Event"],
)

# Construye el PlaybackService con el Producer de Kafka 
def get_playback_service() -> PlaybackService:
    try:
        producer = get_kafka_producer()
    except KafkaPublishError as exc:  # Kafka no está configurado -> responde 503 en vez de un 500 
        raise EventPublishFailedError() from exc
    return PlaybackService(producer, get_kafka_settings().playback_topic)


@router.post(
    "/reproduction",
    status_code=status.HTTP_204_NO_CONTENT,
)
def ingest_playback_event(
    current_user: Annotated[User, Depends(get_current_user)], # es obligatorio estar logueado -> obtenemos su identidad del JWT
    event: EventRequest,
    playback_service: Annotated[PlaybackService, Depends(get_playback_service)],
) -> None:
    playback_service.publish_playback_event(user_id=current_user.id, event=event)
