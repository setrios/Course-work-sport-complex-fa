from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.order import OrderCreate, OrderResponse, OrderWithItemsResponse
from app.models.order import OrderStatus
from app.services.order_service import (
    get_orders, get_order_by_id, create_order, 
    update_order_status, get_order_items
)
from app.db.mysql_session import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all orders with pagination.
    """
    return get_orders(db, skip, limit)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get a specific order by ID.
    """
    return get_order_by_id(db, order_id)

@router.post("/", response_model=OrderResponse, status_code=201)
def create_new_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order.
    """
    return create_order(db, order_data)

@router.patch("/{order_id}/status")
def update_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db)
):
    """
    Update order status.
    """
    return update_order_status(db, order_id, new_status)

@router.get("/{order_id}/items")
def get_items(order_id: int, db: Session = Depends(get_db)):
    """
    Get all items for a specific order.
    """
    return get_order_items(db, order_id)
