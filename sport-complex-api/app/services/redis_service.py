from typing import Optional, List, Dict, Any
import json
from datetime import timedelta
from app.db.redis_client import get_redis

class RedisService:
    """Service for Redis operations - caching, sessions, tracking"""
    
    @staticmethod
    def cache_product(product_id: int, product_data: Dict[str, Any], ttl_seconds: int = 3600):
        """Cache product data"""
        redis_client = get_redis()
        key = f"product:{product_id}"
        redis_client.setex(key, ttl_seconds, json.dumps(product_data))
    
    @staticmethod
    def get_cached_product(product_id: int) -> Optional[Dict[str, Any]]:
        """Get cached product"""
        redis_client = get_redis()
        key = f"product:{product_id}"
        data = redis_client.get(key)
        return json.loads(data) if data else None
    
    @staticmethod
    def invalidate_product_cache(product_id: int):
        """Remove product from cache"""
        redis_client = get_redis()
        redis_client.delete(f"product:{product_id}")
    
    @staticmethod
    def cache_trainer_schedule(trainer_id: int, schedule_data: List[Dict], ttl_seconds: int = 7200):
        """Cache trainer schedule"""
        redis_client = get_redis()
        key = f"trainer:schedule:{trainer_id}"
        redis_client.setex(key, ttl_seconds, json.dumps(schedule_data))
    
    @staticmethod
    def get_cached_trainer_schedule(trainer_id: int) -> Optional[List[Dict]]:
        """Get cached trainer schedule"""
        redis_client = get_redis()
        key = f"trainer:schedule:{trainer_id}"
        data = redis_client.get(key)
        return json.loads(data) if data else None
    
    @staticmethod
    def invalidate_trainer_schedule(trainer_id: int):
        """Remove trainer schedule from cache"""
        redis_client = get_redis()
        redis_client.delete(f"trainer:schedule:{trainer_id}")
    
    @staticmethod
    def track_online_user(user_id: int, ttl_seconds: int = 300):
        """Track online user (5 min TTL)"""
        redis_client = get_redis()
        redis_client.setex(f"online:{user_id}", ttl_seconds, "1")
    
    @staticmethod
    def get_online_users() -> List[str]:
        """Get list of online user IDs"""
        redis_client = get_redis()
        keys = redis_client.keys("online:*")
        return [key.split(":")[1] for key in keys]
    
    @staticmethod
    def increment_bestseller(product_id: int):
        """Increment bestseller counter"""
        redis_client = get_redis()
        redis_client.zincrby("bestsellers", 1, str(product_id))
    
    @staticmethod
    def get_bestsellers(limit: int = 10) -> List[tuple]:
        """Get top bestselling products"""
        redis_client = get_redis()
        # Returns [(product_id, score), ...]
        return redis_client.zrevrange("bestsellers", 0, limit - 1, withscores=True)
    
    @staticmethod
    def update_stock(product_id: int, quantity: int):
        """Update real-time stock level"""
        redis_client = get_redis()
        redis_client.set(f"stock:{product_id}", quantity)
    
    @staticmethod
    def get_stock(product_id: int) -> Optional[int]:
        """Get real-time stock level"""
        redis_client = get_redis()
        stock = redis_client.get(f"stock:{product_id}")
        return int(stock) if stock else None
