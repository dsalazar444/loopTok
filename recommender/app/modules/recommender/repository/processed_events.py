import redis

class ProcessedEventsRepository:
    def __init__(self, client: redis.Redis):
        self.client = client

    def is_processed(self, event_id: str) -> bool:
        exists = self.client.exists(f"processed:event:{event_id}")
        return exists

    def mark_processed(self, event_id: str) -> None:
        self.client.set(f"processed:event:{event_id}","1", ex=86400) # expira en 24h
        