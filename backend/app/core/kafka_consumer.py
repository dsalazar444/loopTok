import json, logging
from confluent_kafka import Consumer, KafkaException
from app.core.kafka_producer import get_kafka_settings
from app.modules.events.schemas import KafkaEvent

logger = logging.getLogger(__name__)
settings = get_kafka_settings()


def on_client_error(error):
    logger.error("Error del cliente de Kafka: %s", error)


def msg_process(evento):
    pass

# Confirma el offset a Kafka. Si falla solo se registra -> 
# el consumer sigue, y el siguiente commit exitoso cubre este mensaje
def commit_offset():
    try:
        consumer.commit(asynchronous=False)
    except KafkaException as exc:
        logger.error("No se pudo confirmar el offset: %s", exc)


# para conectarme a un cluster de kafka debo priemero usar la api kafkaconsumer 
# la configuracion es esta de abajo
conf = {
    'bootstrap.servers': settings.bootstrap_servers,
    'group.id':'looptok_consumer',
    'auto.offset.reset':'earliest',
    "enable.auto.commit": False,
    "error_cb": on_client_error  # registra en el log los errores de conexión con el broker
}

# se crea la instancia del consumer
consumer = Consumer(conf)
running = True

# podemos suscribirnos a cualquier topic (solo hay 1)
topic = settings.playback_topic  # KAFKA_PLAYBACK_TOPIC del env

# el consumidor entra en un bucle infinito buscando  nuevos mensajes
# la idea es 
# 1. Pregunta si hay mensajes nuevos
# 2. Si hay un mensaje, poll() lo devuelve (un mensaje por vuelta)
# 3. Si no hay mensajes, espera un momento.
# 4. Vuelve a preguntar
try: 
    consumer.subscribe([topic])

    while running:
        msg = consumer.poll(timeout=1.0) # se consulta kafka apra obtener un mensaje    
        if msg is None:
            continue
        if msg.error(): # se mira s el mensaje recibido es un error y lo msotramos
            if msg.error().fatal(): 
                raise KafkaException(msg.error())
            logger.error("Error al leer de Kafka: %s", msg.error())  # error temporal: se registra y sigue
            continue

        else:
            try:

                datos_dict = json.loads(msg.value().decode('utf-8')) # bytes -> JSON string -> diccionario -> Objeto Python
                evento_recibido = KafkaEvent(**datos_dict)

            except (ValueError, TypeError) as exc:  # JSON roto, bytes invalidos, JSON que no es un objeto o evento que no cumple KafkaEvent
                logger.error("Mensaje invalido: %s", exc)
                commit_offset()   # descartamos  el mensaje invalido
                continue  # se salta este mensaje y sigue con el siguiente

            print(evento_recibido.event_id)
            msg_process(evento_recibido)   #funcion donde llevamos el evento ya validado para procesarlo u otras cosas
            commit_offset() # offsets -> la posición de un mensaje dentro de una partición al el consumer confirmar  un offset -> le comunica a Kafka hasta que posicion ha avanzado
finally:
    consumer.close() # cierre controlado


# manejo de errores: errores de conexion o errores de logica de negocio
#  El Consumer pierde conexión con el broker -> libdrkafka
# Consumer se cae antes del commit	->Puede provocar que Kafka entregue nuevamente un evento. por offset
# JSON inválido -> no puede convertir el mensaje recibido en un evento válido en la deserializacion
# Recomendador caido ->	No puede entregar los eventos al recomendador ( TODO: hacer cuando esté)
# el recomendador tarda demasiado en responder. ( TODO: hacer cuando esté)

