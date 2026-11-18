import redis
from uuid import UUID
import json

class RecommendationService:
    def __init__(self, user_id: UUID ):   
        
        self.client = redis.Redis(
            host="valkey", # redis permite conectarnos con Valkey. Aqui va el host_name, en esta caso, va el nombre del servicio en el compose
            port=6379, # puerto en el que corre Valkey
            decode_responses=True # Decodifica de bytes a str
        )
        self.user_id = user_id


    def get_recommendations(self, user_id: UUID) -> list[str]:

        # usando el cliente, obtenemos json (por eso get y no hsget) de recomendaciones para un usuario, que recommender almacenó en Valkey
        recommendations = self.client.get(f"user:{user_id}:recommendations") # obtenemos un str -> hay que convertirlo a json

        # si no hay recomendaciones, se inicializa una
        if recommendations is None:
            return {}

        return json.loads(recommendations)

        # TODO: Revisar respuestas de error, si se retorna {} eso lo maneja el front? mandar codigos de error?