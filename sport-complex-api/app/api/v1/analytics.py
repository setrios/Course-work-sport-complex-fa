from fastapi import APIRouter
from app.services.redis_service import RedisService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/bestsellers")
def get_bestsellers(limit: int = 10):
    """
    Get top bestselling products from Redis.
    """
    bestsellers = RedisService.get_bestsellers(limit)
    return {
        "bestsellers": [
            {"product_id": int(product_id), "sales_count": int(score)}
            for product_id, score in bestsellers
        ]
    }

@router.get("/online-users")
def get_online_users():
    """
    Get currently online users.
    """
    online = RedisService.get_online_users()
    return {
        "count": len(online),
        "user_ids": online
    }
