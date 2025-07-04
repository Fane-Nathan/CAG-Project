import redis

class GPTCacheService:
    def __init__(self, settings):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )

    def get(self, key: str):
        return self.redis_client.get(key)

    def set(self, key: str, value: str):
        self.redis_client.set(key, value)
