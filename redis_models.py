import json
import redis
from datetime import timedelta
from typing import Optional, List, Dict, Any

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)

    # ============ CLIENTS & SESSIONS ============
    def set_session(self, session_token: str, user_data: Dict[str, Any], ttl_seconds=86400):
        key = f"session:{session_token}"
        self.client.setex(key, timedelta(seconds=ttl_seconds), json.dumps(user_data))

    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        data = self.client.get(f"session:{session_token}")
        return json.loads(data) if data else None

    def add_online_user(self, role: str, user_id: int):
        self.client.sadd(f"online:{role}", user_id)
        self.client.expire(f"online:{role}", 300) # Heartbeat TTL

    def get_online_users(self, role: str) -> List[str]:
        return list(self.client.smembers(f"online:{role}"))

    # ============ TRAINERS & BOOKINGS ============
    def set_trainer_schedule(self, trainer_id: int, schedule_data: Dict[str, Any]):
        key = f"trainer_schedule:{trainer_id}"
        self.client.setex(key, timedelta(hours=24), json.dumps(schedule_data))

    def get_trainer_schedule(self, trainer_id: int) -> Optional[Dict]:
        data = self.client.get(f"trainer_schedule:{trainer_id}")
        return json.loads(data) if data else None

    def add_client_session(self, client_id: int, session_id: int, score: float):
        # Score could be timestamp for sorting
        self.client.zadd(f"client_sessions:{client_id}", {str(session_id): score})
        self.client.expire(f"client_sessions:{client_id}", timedelta(days=30))

    def add_session_reminder(self, session_id: int, reminder_timestamp: float):
        self.client.zadd("session_reminders", {str(session_id): reminder_timestamp})

    # ============ PRODUCTS & SHOP ============
    def cache_product(self, product_id: int, product_data: Dict[str, Any]):
        self.client.setex(f"product:{product_id}", timedelta(hours=1), json.dumps(product_data))

    def get_cached_product(self, product_id: int) -> Optional[Dict]:
        data = self.client.get(f"product:{product_id}")
        return json.loads(data) if data else None

    def update_stock(self, product_id: int, quantity: int):
        self.client.set(f"stock:{product_id}", quantity)
    
    def get_stock(self, product_id: int) -> Optional[int]:
        val = self.client.get(f"stock:{product_id}")
        return int(val) if val else None

    def update_bestsellers(self, product_id: int, quantity_sold: int):
        self.client.zincrby("bestsellers:day", quantity_sold, str(product_id))

    def add_to_cart(self, client_id: int, product_id: int, quantity: int):
        self.client.hset(f"cart:{client_id}", str(product_id), quantity)
        self.client.expire(f"cart:{client_id}", timedelta(days=7))

    def get_cart(self, client_id: int) -> Dict[str, str]:
        return self.client.hgetall(f"cart:{client_id}")

    # ============ SERVICES & REPORTS ============
    def cache_report(self, report_key: str, report_data: Dict, ttl=2592000):
        self.client.setex(report_key, timedelta(seconds=ttl), json.dumps(report_data))

    # ============ QUEUES ============
    def push_email_task(self, email_task: Dict[str, Any]):
        self.client.lpush("email_queue", json.dumps(email_task))

    def push_report_task(self, report_task: Dict[str, Any]):
        self.client.lpush("report_queue", json.dumps(report_task))
