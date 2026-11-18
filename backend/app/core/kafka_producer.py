import json #convertir el devento de python a JSON
import logging
import threading #para hios que atiende las confirmaciones de kafka
from collections.abc import Callable  #para definir el tipo de una funcion q recibimos como parametro
from functools import lru_cache  #evitar cargar varias veces la configuracion 
from typing import Any

from confluent_kafka import KafkaError, KafkaException, Message, Producer
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# ---------- ERRORES DEL PRODUCER ----------
# Se lanza cuando NO se pudo encolar el mensaje (producer cerrado o sin inicializar, cola llena,
# mensaje no válido para JSON, configuración inválida). El service lo convierte en un 503.
# Si el mensaje se encola pero falla al llegar a Kafka, no se usa: se registra en el callback de entrega
class KafkaPublishError(Exception):
    pass
# --------------------------------------------

# ---------- flujo de como envia el producer un mensaje a broker ----------
# Qué configurar: la dirección del servidor y convertir clave y valor a bytes 
#  
# 1. Conexión inicial: se conecta al servidor de arranque y le pide la lista de brokers y quién lidera cada partición.
#   
# 2. Elegir partición: mensajes con la misma key van a la misma partición -> key = playbackId).
#   al llamar produce(...) en publish()  se hace automatico -> nosotros solo pasamos la key

# 3. Enviar al broker líder: el mensaje va directo al broker líder de esa partición.
#   -> solo hay 1  broker, así que siempre es el liderS
# 4. Envío en segundo plano: hilos internos convierten y transmiten los mensajes; produce() solo los encola.
#   -> hilos _poller solo atiende las confirmaciones
# ----------------------------------------------------------------


# aca se almacena la cofiguracion apra conectarnos a kafka -> lee y organiza lso valores que tengmos en .env
class KafkaSettings(BaseSettings):
    bootstrap_servers: str | None = None   #KAFKA_BOOTSTRAP_SERVERS -> donde encontrar el broke de kafkaacks
    required: bool = False   #KAFKA_REQUIRED
    client_id: str = "looptok-backend"  
    playback_topic: str = "looptok.playback-events"


    # Lee las variables KAFKA_ desde el archivo .env o el entorno
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        env_file=".env",
        extra="ignore"
    )

    # Prepara la configuración que necesita confluent_kafka adapta los nombres de la configuracion 
    def to_client_config(self) -> dict[str, Any]:
        config = {
            "bootstrap.servers": self.bootstrap_servers,
            "client.id": self.client_id,
            "enable.idempotence": True, # ayuda a evitar duplicados causados por reintentos internos del Producer
            "acks": "all",   #garantias para la durabilidad de los mensajes -> todas lsa replicas deben confirmar la recepcion del mensaje
        }

        # elimina las configuraciones sin valor 
        return {key: value for key, value in config.items() if value is not None}


class KafkaEventProducer:
    def __init__(self, settings: KafkaSettings | None = None) -> None: # meotdo para inicialziacionn cuando creamos un objeto de la clase
        # Usa la configuración recibida
        settings = settings or KafkaSettings()

        if not settings.bootstrap_servers:
            raise KafkaPublishError("KAFKA_BOOTSTRAP_SERVERS no está configurada")

        try: # se crea el producer
            self._producer = Producer({
                **settings.to_client_config(), #** para desempaquetar dict de client_config con toda la info
                "error_cb": self._on_client_error
            })
        except KafkaException as exc:
            raise KafkaPublishError(f"Configuracion de Kafka invalida: {exc}") from exc

        self._closed = False # si hay error se cierra el producer
        self._lock = threading.Lock() #candando para hilos
        self._stop = threading.Event()

        # Hilo secundario para consultar en kafka para antender las conrimacines de lso emnsajes que envia el prodcuer
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


    # Registra errores globales del cliente -> en conexión con Kafka
    @staticmethod #pq no hay que accedeer a nada del objeto
    def _on_client_error(error: KafkaError) -> None:
        logger.error("Error del cliente de Kafka: %s", error)

#debemos recibir el topic donde publicar,value:contenido del evento, key:playbackid,ondelivery para recibir r de la entrga
# key -> acompaña a cada mensaje y que Kafka usa para decidir a qué partición va
    def publish(self, topic: str, value: dict[str, Any], key: str | None = None,
        on_delivery: Callable[[KafkaError | None, Message], None] | None = None,
    ) -> None:

        # python no tiene forma de convertir a bytes hay que pasarlo primero  a json
        try:
            json_data = json.dumps(value, ensure_ascii=False, allow_nan=False)
            payload = json_data.encode("utf-8") # de json a bytes
        except (TypeError, ValueError) as exc:
            raise KafkaPublishError(f"El mensaje no es valido para JSON: {exc}") from exc

        # Se ejecuta cuando Kafka confirma si el mensaje llegó o falló
        def delivery_callback(error: KafkaError | None, message: Message) -> None:
            if error is not None:
                logger.error("Error al entregar el mensaje: %s", error)

            if on_delivery is not None:
                on_delivery(error, message)

        try:
            # Evita publicar mientras el Producer se está cerrando
            with self._lock:
                if self._closed:
                    raise KafkaPublishError("El Producer está cerrado")
                # aca enviamos a kafka 
                self._producer.produce(
                    topic, #publicamos en nuestr unico topic
                    value=payload, #evento serializado
                    key=key.encode("utf-8") if key is not None else None,
                    on_delivery=delivery_callback #funcion q se ejecuta cuando kafka termine de almacenar el mensaje
                )

        except BufferError as exc:
            raise KafkaPublishError("La cola local de Kafka está llena") from exc
        except KafkaException as exc:
            raise KafkaPublishError(f"No se pudo enviar el mensaje: {exc}") from exc

    # cuando se apaga el back y  antes habiamos publicado 5 mensajes (quedan en cola local) 
    # con flush se peude esperar a que se entrguen antes de cerrar
    def flush(self, timeout: float = 10.0) -> int:
        return self._producer.flush(timeout)

    # Deja de aceptar mensajes y terminamos  poll
    def close(self, timeout: float = 10.0) -> None:
        with self._lock:
            self._closed = True

        remaining = self.flush(timeout)
        self._stop.set()
        self._poller.join(timeout=1.0)

        if remaining:
            logger.warning(
                "El Producer se cerró con %d mensaje(s) sin entregar",
                remaining
            )


# ayuda a reutilizar la confi sin tener que  crearla de nuevo 
@lru_cache
def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()


# VARIABLE GLOBAR -> al inicioo no tiene nigun producer -> ES PARA INICIALIZAR
_producer: KafkaEventProducer | None = None


# Se ejecuta al iniciar FastAPI en main
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


# Devuelve el Producer 
def get_kafka_producer() -> KafkaEventProducer:
    if _producer is None:
        raise KafkaPublishError("El Producer no esta inicializado")

    return _producer


# la usamos al apagar FastAPI
def close_kafka_producer() -> None:
    global _producer

    if _producer is not None:
        _producer.close()
        _producer = None
