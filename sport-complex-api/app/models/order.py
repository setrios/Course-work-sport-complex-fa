from sqlalchemy import Column, Integer, String, Enum, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.db.mysql_session import Base
import enum

class OrderType(str, enum.Enum):
    IN_STORE = "in_store"
    ONLINE_PICKUP = "online_pickup"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    CLUB_CARD_BALANCE = "club_card_balance"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    order_date = Column(DateTime, server_default=func.now())
    order_type = Column(Enum(OrderType), default=OrderType.IN_STORE)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    subtotal = Column(Numeric(10, 2))
    discount_amount = Column(Numeric(10, 2), default=0.00)
    total_amount = Column(Numeric(10, 2))
    payment_method = Column(Enum(PaymentMethod))
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    notes = Column(Text)
    completed_by = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(255))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2))
    discount = Column(Numeric(10, 2), default=0.00)
    subtotal = Column(Numeric(10, 2))
    added_at = Column(DateTime, server_default=func.now())
