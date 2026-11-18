import json
import logging
import threading
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from confluent_kafka import KafkaError, KafkaException, Message, Producer
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class KafkaSettings(BaseSettings):
    bootstrap_servers: str | None = None
    required: bool = False
    client_id: str = "looptok-backend"
    playback_topic: str = "looptok.playback-events"

    # Configuración opcional para conexiones seguras
    security_protocol: str | None = None
    sasl_mechanism: str | None = None
    sasl_username: str | None = None
    sasl_password: str | None = None

    # Lee las variables KAFKA_ desde el archivo .env o el entorno
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        env_file=".env",
        extra="ignore"
    )

    # Prepara la configuración que necesita confluent_kafka
    def to_client_config(self) -> dict[str, Any]:
        config = {
            "bootstrap.servers": self.bootstrap_servers,
            "client.id": self.client_id,
            "enable.idempotence": True,
            "acks": "all",
            "security.protocol": self.security_protocol,
            "sasl.mechanism": self.sasl_mechanism,
            "sasl.username": self.sasl_username,
            "sasl.password": self.sasl_password,
        }

        # Solo envía las opciones que tienen un valor
        return {key: value for key, value in config.items() if value is not None}


class KafkaPublishError(Exception):
    pass


class KafkaEventProducer:
    def __init__(self, settings: KafkaSettings | None = None) -> None:
        # Usa la configuración recibida o carga la del entorno
        settings = settings or KafkaSettings()

        if not settings.bootstrap_servers:
            raise KafkaPublishError("KAFKA_BOOTSTRAP_SERVERS no está configurada")

        try:
            self._producer = Producer({
                **settings.to_client_config(),
                "error_cb": self._on_client_error
            })
        except KafkaException as exc:
            raise KafkaPublishError(f"Configuración de Kafka inválida: {exc}") from exc

        self._closed = False
        self._lock = threading.Lock()
        self._stop = threading.Event()

        # Hilo que atiende las confirmaciones de Kafka
        self._poller = threading.Thread(
            target=self._poll_loop,
            name="kafka-poll",
            daemon=True
        )
        self._poller.start()

    # Consulta a Kafka hasta que se solicite detener el hilo
    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._producer.poll(0.5)
            except Exception:
                logger.exception("Error al consultar las confirmaciones de Kafka")

    # Registra errores generales de conexión con Kafka
    @staticmethod
    def _on_client_error(error: KafkaError) -> None:
        logger.error("Error del cliente de Kafka: %s", error)

    def publish(
        self,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        on_delivery: Callable[[KafkaError | None, Message], None] | None = None,
    ) -> None:

        # Convierte el evento a JSON y después a bytes
        try:
            json_data = json.dumps(value, ensure_ascii=False, allow_nan=False)
            payload = json_data.encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise KafkaPublishError(f"El mensaje no es válido para JSON: {exc}") from exc

        # Se ejecuta cuando Kafka confirma si el mensaje llegó o falló
        def delivery_callback(error: KafkaError | None, message: Message) -> None:
            if error is not None:
                logger.error(
                    "Error al entregar el mensaje (topic=%s): %s",
                    message.topic(),
                    error
                )

            if on_delivery is not None:
                try:
                    on_delivery(error, message)
                except Exception:
                    logger.exception("Error en el callback de entrega")

        try:
            # Evita publicar mientras el Producer se está cerrando
            with self._lock:
                if self._closed:
                    raise KafkaPublishError("El Producer está cerrado")

                self._producer.produce(
                    topic,
                    value=payload,
                    key=key.encode("utf-8") if key is not None else None,
                    on_delivery=delivery_callback
                )

        except BufferError as exc:
            raise KafkaPublishError("La cola local de Kafka está llena") from exc
        except KafkaException as exc:
            raise KafkaPublishError(f"No se pudo enviar el mensaje: {exc}") from exc

    # Espera a que se entreguen los mensajes pendientes
    def flush(self, timeout: float = 10.0) -> int:
        return self._producer.flush(timeout)

    # Deja de aceptar mensajes y cierra el Producer
    def close(self, timeout: float = 10.0) -> None:
        with self._lock:
            self._closed = True

        remaining = self.flush(timeout)

        # Detiene el hilo que consulta las confirmaciones
        self._stop.set()
        self._poller.join(timeout=1.0)

        if remaining:
            logger.warning(
                "El Producer se cerró con %d mensaje(s) sin entregar",
                remaining
            )


# Carga la configuración una sola vez
@lru_cache
def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()


# Instancia única del Producer para toda la aplicación
_producer: KafkaEventProducer | None = None


# Se ejecuta al iniciar FastAPI
def init_kafka_producer() -> None:
    global _producer

    settings = get_kafka_settings()

    if not settings.bootstrap_servers:
        if settings.required:
            raise KafkaPublishError(
                "KAFKA_BOOTSTRAP_SERVERS no está configurada y KAFKA_REQUIRED=true"
            )

        logger.warning("Kafka no está configurado")
        return

    _producer = KafkaEventProducer(settings)


# Devuelve el Producer que ya se creó al iniciar la aplicación
def get_kafka_producer() -> KafkaEventProducer:
    if _producer is None:
        raise KafkaPublishError("El Producer no está inicializado")

    return _producer


# Se ejecuta al apagar FastAPI
def close_kafka_producer() -> None:
    global _producer

    if _producer is not None:
        _producer.close()
        _producer = None
