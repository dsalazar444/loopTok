import json
import logging
import threading
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from confluent_kafka import KafkaError, KafkaException, Message, Producer
from pydantic_settings import BaseSettings, SettingsConfigDict

# Logger para registrar errores y eventos importantes del Producer.
logger = logging.getLogger(__name__)


# Define el tipo de función que recibirá la confirmación de entrega de Kafka ->
# error será None si el mensaje se entregó correctamente, o contendrá el error si falló
DeliveryCallback = Callable[[KafkaError | None, Message], None]


class KafkaSettings(BaseSettings):
    bootstrap_servers: str | None = None  # KAFKA_BOOTSTRAP_SERVERS por ej 127.0.0.1:9092
    required: bool = False  
    client_id: str = "looptok-backend" # Identifica este Producer ante Kafka
    playback_topic: str = "looptok.playback-events"  # KAFKA_PLAYBACK_TOPIC: topic de eventos de reproducción
   
    security_protocol: str | None = None   # Opcionales -> solo para brokers con seguridad si se hace en despliegue
    sasl_mechanism: str | None = None
    sasl_username: str | None = None
    sasl_password: str | None = None

    # Configura cómo se leen las variables de entorno y el archivo .env
    model_config = SettingsConfigDict(env_prefix="KAFKA_", env_file=".env", extra="ignore")

    # Convierte los nombres de configuración de Python a los nombres que espera la libreria de confluent_kafka
    def to_client_config(self) -> dict[str, str | bool]:
        config = {
            "bootstrap.servers": self.bootstrap_servers,
            "client.id": self.client_id,
            "enable.idempotence": True,
            "acks": "all",  # Solicita confirmación de todos los nodos que estén en el conjunto ISR
            "security.protocol": self.security_protocol, # Parámetros de seguridad. Se utilizan cuando el broker los requiere.
            "sasl.mechanism": self.sasl_mechanism,
            "sasl.username": self.sasl_username,
            "sasl.password": self.sasl_password,
        }
        return {k: v for k, v in config.items() if v is not None}  # Elimina las opciones que no fueron configuradas 


class KafkaPublishError(Exception):
    # Error cuando NO se pudo encolar el mensaje (cola llena, producer cerrado, mensaje no válido)
    # Si el mensaje se encola pero falla al llegar a Kafka, no se usa este error -> se avisa en el callback
    pass


class KafkaEventProducer:
    def __init__(self, settings: KafkaSettings | None = None) -> None:
        settings = settings or KafkaSettings()   #usamos la configuracion recibida o carga la config del entorno
        if not settings.bootstrap_servers:
            raise KafkaPublishError("KAFKA_BOOTSTRAP_SERVERS no está configurada")
        
        try:
            self._producer = Producer(
                {**settings.to_client_config(), "error_cb": self._on_client_error}
            )
        except KafkaException as exc:  
            raise KafkaPublishError(f"Configuración de Kafka inválida: {exc}") from exc
        
        self._closed = False  # pasa a True cuando se cierra el Producer

        self._lock = threading.Lock()  # evita que publish() encole justo cuando se está cerrando
        self._stop = threading.Event()  

        # Hilo en segundo plano que revisa las confirmaciones de Kafka
        self._poller = threading.Thread(target=self._poll_loop, name="kafka-poll", daemon=True)
        self._poller.start()

    # Mientras no se solicite detener el hilo, consulta a Kafka ->
    # poll() permite procesar confirmaciones de entrega y ejecutar callbacks
    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._producer.poll(0.5)
            except Exception: 
                logger.exception("El callback de Kafka lanzó una excepción")

    @staticmethod
    def _on_client_error(error: KafkaError) -> None:
        # Errores globales como broker inalcanzable o problema de conexion con el broker
        logger.error("Error del cliente de Kafka: %s", error)

    def publish(
        self,
        topic: str,
        value: dict[str, Any],
        key: str | None = None,
        on_delivery: DeliveryCallback | None = None,
    ) -> None:
        
        # publish solo encola el mensaje en una cola local. No significa que ya llegó a Kafka ->
        # eso se confirma después, en el callback.

        try:
            # Convertimos el evento a JSON y luego a bytes para enviarlo.
            json_data = json.dumps(value, ensure_ascii=False, allow_nan=False)
            payload = json_data.encode("utf-8")

        except (TypeError, ValueError) as exc:
            raise KafkaPublishError(f"El mensaje no es serializable a JSON: {exc}") from exc

        def _delivery(error: KafkaError | None, message: Message) -> None:
            if error is not None:
                logger.error("Fallo en la entrega a Kafka (topic=%s): %s", message.topic(), error)
            if on_delivery is not None:
                try:
                    on_delivery(error, message)
                except Exception:
                    logger.exception("Error en el callback de entrega")

        try:
            with self._lock:  # un solo hilo a la vez: así no se encola un mensaje mientras se cierra
                if self._closed:
                    raise KafkaPublishError("El producer está cerrado")
                self._producer.produce(
                    topic,
                    value=payload,
                    key=key.encode("utf-8") if key is not None else None,
                    on_delivery=_delivery,
                )
        except BufferError as exc:  # buffer local lleno -> el broker no alcanzó o está caído
            raise KafkaPublishError("La cola local de Kafka está llena") from exc
        
        except KafkaException as exc:
            raise KafkaPublishError(f"No se pudo encolar el mensaje: {exc}") from exc


    def flush(self, timeout: float = 10.0) -> int:
        # Espera a que Kafka confirme los mensajes pendientes y devuelve cuántos quedaron sin confirmar
        return self._producer.flush(timeout)

    def close(self, timeout: float = 10.0) -> None:
        with self._lock:
            self._closed = True  # desde aquí publish() ya no acepta mensajes nuevos
        remaining = self.flush(timeout)  # envía lo que estaba pendiente
        self._stop.set()  
        self._poller.join(timeout=1.0) 
        if remaining:
            logger.warning("El producer de Kafka se cerró con %d mensaje(s) sin entregar", remaining)


@lru_cache  # evita releer el .env en cada petición
def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()


# Producer único de toda la app -> Empieza vacío y se crea al arrancar (init_kafka_producer)
_producer: KafkaEventProducer | None = None


def init_kafka_producer() -> None:
    # Se llama una sola vez al arrancar la app desde el lifespan en main
    global _producer
    settings = get_kafka_settings()
    if not settings.bootstrap_servers:  
        if settings.required:  
            raise KafkaPublishError("KAFKA_BOOTSTRAP_SERVERS no está configurada y KAFKA_REQUIRED=true")
       
        logger.warning("Kafka no configurado: los eventos de reproducción responderán 503")
        return
    _producer = KafkaEventProducer(settings)


def get_kafka_producer() -> KafkaEventProducer:
    # Devuelve el Producer ya creado, Si no existe lanza error
    if _producer is None:
        raise KafkaPublishError("El producer de Kafka no está inicializado")
    return _producer


def close_kafka_producer() -> None:      # Se llama al apagar la app -> envía lo pendiente y cierra el Producer
 
    global _producer
    if _producer is not None:
        _producer.close()
        _producer = None
