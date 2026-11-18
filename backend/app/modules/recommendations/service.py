import redis
from uuid import UUID
from app.modules.recommendations.repository import RecommendationsRepository
import json

class RecommendationService:
    def __init__(self, user_id: UUID ):   
        
        self.client = redis.Redis(
            host="valkey", # redis permite conectarnos con Valkey. Aqui va el host_name, en esta caso, va el nombre del servicio en el compose
            port=6379, # puerto en el que corre Valkey
            decode_responses=True # Decodifica de bytes a str
        )
        self.user_id = user_id
        self.recommendation_repository = RecommendationsRepository(client=self.client)

    def get_recommendations(self, user_id: UUID) -> list[str]:

        # usando el cliente, obtenemos json (por eso get y no hsget) de recomendaciones para un usuario, que recommender almacenó en Valkey
        recommendations = self.recommendation_repository.get_recommendations(user_id=user_id)

        if recommendations is None:
            return {}

        return json.loads(recommendations)
# TODO: revisar que front si maneje lista {}