import redis
from uu import UUID
import json
from app.modules.recommender.models import preferences

# Aclaración valkey: A diferencia de PostgreSQL, Valkey no requiere definir tablas ni ejecutar migraciones para estas estructuras.
# Las claves se crean conforme tu aplicación escribe información.
class RecommendationsRepository:
    def __init__(self, client: redis.Redis):
        self.client = client

    # usando el cliente, obtenemos dict de preferencias de un usuario almacenado en Valkey
    def set_recommendations(self, user_id: UUID, categories: list[str]) -> None:
        key = f"user:{user_id}:recommendations"

        self.client.set(key, json.dumps(categories), ex=1200)
        # guardaremos como json, y no como dict, porque es una lista, y le definiremos un TTL de 20 min
        # set tiene dos caracteristicas: override -> reemplaza recommendations para ese user si ya existia -> asi back siempre obtiene la más reciente
            # segunda: permite configurar TTL