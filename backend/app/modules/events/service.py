import logging
from uuid import UUID

from app.core.errors import EventPublishFailedError
from app.core.kafka_producer import KafkaEventProducer, KafkaPublishError
from app.modules.events.schemas import EventRequest

logger = logging.getLogger(__name__)


class PlaybackService:
    # producer -> el que envía a Kafka | topic -> el "canal" de Kafka donde se publican los eventos
    def __init__(self, producer: KafkaEventProducer, topic: str) -> None:
        self.producer = producer
        self.topic = topic

    def publish_playback_event(self, user_id: UUID, event: EventRequest) -> None:
        # convertimos objeto en un json
        event_data = event.model_dump(mode="json",by_alias=True, exclude=None) 
        # by_alias= true es para que cuando lo convierta a json, mantenga las claves con el alias que se define en el esquema (camelCase) para mantener consistencia con el front
        # exclude=None para que no añada parametros que tengan valor none
        
        # añadimos key de user id
        event_data["userId"] = str(user_id)

        # publish solo encola el mensaje no confirma que ya llegó a Kafka
        # Si falla después, el producer lo deja en el log 
        # key = playbackId -> los eventos de una misma reproducción quedan juntos y en orden
        try:
            self.producer.publish(
                topic=self.topic,
                value=event_data,
                key=str(event.playback_id),
            )
        except KafkaPublishError as exc:
            # Falló al encolar (producer cerrado, cola llena, mensaje no válido) -> se avisa al frontend con 503
            logger.error("No se pudo publicar el evento %s: %s", event.event_id, exc)
            raise EventPublishFailedError() from exc
