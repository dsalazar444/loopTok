import json, logging
from confluent_kafka import Consumer, KafkaError, KafkaException
from pydantic import ValidationError
from app.core.kafka_producer import get_kafka_settings
from app.modules.events.schemas import EventRequest, KafkaEvent

logger = logging.getLogger(__name__)
settings = get_kafka_settings()  
# se suscribe a varios topics  
# de ahi lee procesa y reacciona frente a flujos de datos o eventos en tiempo real 
class KafkaEvent(EventRequest):
    user_id: UUID = Field(alias="userId")

def on_client_error(error):
    logger.error("Error del cliente de Kafka: %s", error)

# para conectarme a un cluster de kafka debo priemero usar la api kafkaconsumer 
# la configuracion es esta de abajo
conf = {
    'bootstrap.servers': settings.bootstrap_servers,
    'group.id':'looptok_consumer',
    'auto.offset.reset':'earliest',
    "enable.auto.commit": False    
}
# se crea la instancia del consumer
consumer = Consumer(conf)
running = True

# podemos suscribirnos a cualquier topic (solo hay 1)
topic = 'looptok.playback-events'


# el consumidor entra en un bucle infinito buscando  nuevos mensajes
# la idea es 
# Pregunta si hay mensajes nuevos
# Si hay mensajes, los recibe y kafka los envia agrupados en un objeto llamado ConsumerRecords
# Si no hay mensajes, espera un momento.
# Vuelve a preguntar
try: 
    consumer.subscribe([topic])

    while running:
        msg = consumer.poll(timeout=1.0) # se consulta kafka apra obtener un mensaje    
        if msg is None:
            continue
        if msg.error(): # se mira s el mensaje recibido es un error y lo msotramos
            if msg.error().fatal(): 
                raise KafkaException(msg.error())
            continue 

        else:
            try:

                datos_dict = json.loads(msg.value().decode('utf-8')) # bytes -> JSON string -> diccionario -> Objeto Python
                evento_recibido = KafkaEvent(**datos_dict)

            except(UnicodeDecodeError,json.JSONDecodeError) as exc:
                logger.error("Error de deserializacion: %s", exc)
                consumer.commit(asynchronous=False)
                continue

            except ValidationError as exc:
                logger.error("Error de validacion del evento: %s", exc)
                consumer.commit(asynchronous=False)
                continue

            
            except ValueError as exc:  # JSON roto, bytes inválidos o evento que no cumple EventRequest
                logger.error("Mensaje invalido: %s", exc)
                consumer.commit(asynchronous=False)   #     # Descartamos deliberadamente el mensaje inválido
                continue  # se salta este mensaje y sigue con el siguiente

            print(evento_recibido.event_id)
            msg_process(msg)   #funcion donde llevamos el mensaje para procesarlo u otras cosas
            consumer.commit(asynchronous=False) # offsets: la posición de un mensaje dentro de una partición al el consumer confirmar  un offset -> le comunica a Kafka hasta que posicion ha avanzado
finally:
    consumer.close() # cierre controlado


def msg_process(msg):
    pass

# manejo de errores: errores de conexion o errores de logica de negocio
#  El Consumer pierde conexión con el broker -> libdrkafka
# JSON inválido -> no puede convertir el mensaje recibido en un evento válido en la deserializacion
# Recomendador caido ->	No puede entregar los eventos al recomendador ( TODO: hacer cuando esté)
# el recomendador tarda demasiado en responder. ( TODO: hacer cuando esté)
# Consumer se cae antes del commit	->Puede provocar que Kafka entregue nuevamente un evento. por offset


# TODO: reintentos
# Qué hacer cuando falla temporalmente la entrega de un evento al recomendador.