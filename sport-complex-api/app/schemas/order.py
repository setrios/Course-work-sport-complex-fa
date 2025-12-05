from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderType, OrderStatus, PaymentMethod, PaymentStatus

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product_name: Optional[str]
    unit_price: float
    discount: float
    subtotal: float
    added_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    client_id: Optional[int] = None
    order_type: OrderType = OrderType.IN_STORE
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: int
    order_number: str
    order_date: datetime
    status: OrderStatus
    subtotal: float
    discount_amount: float
    total_amount: float
    payment_status: PaymentStatus
    
    class Config:
        from_attributes = True

class OrderWithItemsResponse(OrderResponse):
    items: List[OrderItemResponse]
