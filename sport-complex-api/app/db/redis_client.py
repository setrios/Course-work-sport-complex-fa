import redis
from typing import Optional

# Hardcoded for now since Config is skipped
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

class RedisClient:
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Returns a Redis client instance (singleton pattern).
        """
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
        return cls._instance

def get_redis() -> redis.Redis:
    """
    Dependency that provides a Redis client.
    """
    return RedisClient.get_client()
