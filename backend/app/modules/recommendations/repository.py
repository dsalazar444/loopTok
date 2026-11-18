import redis
from uuid import UUID

class RecommendationsRepository:
    def __init__(self, client: redis.Redis):
        self.client = client

    def get_recommendations(self, user_id: UUID):
        recs = self.client.get(f"user:{user_id}:recommendations")
        return recs
