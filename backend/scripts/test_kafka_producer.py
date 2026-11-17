import logging
import time

from app.core.kafka_producer import (
    KafkaEventProducer,
    KafkaSettings,
)

logging.basicConfig(level=logging.INFO)

# Cargar la configuración de Kafka desde el .env q tenemos
settings = KafkaSettings()

# Crear el Producer
producer = KafkaEventProducer(settings)

# Evento temporal para comprobar el envío y que funciona tanto el producer como el listener de kafka
event = {
    "eventId": "test-001",
    "eventType": "video_started",
    "playbackId": "playback-test-001",
    "videoId": "video-test-001",
    "userId": "user-test-001",
    "logType": "playback_event",
}

try:
    # Enviar el evento al Topic looptok.playback-events
    producer.publish(
        topic="looptok.playback-events",
        value=event,
        key="playback-test-001",
    )

    # Esperar a que Kafka confirme la entrega
    remaining = producer.flush(timeout=10)

    if remaining == 0:
        print("Mensaje entregado correctamente a Kafka.")
    else:
        print(f"Quedaron {remaining} mensajes pendientes.")

finally:
    producer.close()
