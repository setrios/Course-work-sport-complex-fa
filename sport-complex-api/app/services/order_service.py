from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.product import Product
from app.schemas.order import OrderCreate
from typing import List
import uuid
from datetime import datetime

def generate_order_number() -> str:
    """
    Generate a unique order number.
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"

def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """
    Get all orders with pagination.
    """
    return db.query(Order).offset(skip).limit(limit).all()

def get_order_by_id(db: Session, order_id: int) -> Order:
    """
    Get an order by ID.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

def create_order(db: Session, order_data: OrderCreate) -> Order:
    """
    Create a new order with items and track bestsellers.
    """
    from app.services.redis_service import RedisService
    
    # Generate order number
    order_number = generate_order_number()
    
    # Calculate totals
    subtotal = 0
    order_items = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        if product.quantity_in_stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
        
        item_subtotal = float(product.price) * item.quantity
        subtotal += item_subtotal
        
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": product.price,
            "discount": 0.00,
            "subtotal": item_subtotal
        })
        
        # Update stock
        product.quantity_in_stock -= item.quantity
        
        # Track bestseller in Redis
        RedisService.increment_bestseller(product.id)
        RedisService.update_stock(product.id, product.quantity_in_stock)
    
    # Create order
    new_order = Order(
        order_number=order_number,
        client_id=order_data.client_id,
        order_type=order_data.order_type,
        subtotal=subtotal,
        discount_amount=0.00,
        total_amount=subtotal,
        payment_method=order_data.payment_method,
        payment_status=PaymentStatus.PENDING,
        status=OrderStatus.PENDING,
        notes=order_data.notes
    )
    
    db.add(new_order)
    db.flush()  # Get order.id before adding items
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    
    # Record purchases in Neo4j
    if order_data.client_id:
        try:
            from app.services.graph_service import GraphService
            for item_data in order_items:
                GraphService.record_purchase(
                    order_data.client_id,
                    item_data["product_id"],
                    item_data["quantity"],
                    float(item_data["subtotal"])
                )
        except Exception as e:
            print(f"Neo4j error (non-critical): {e}")
    
    return new_order

def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Order:
    """
    Update order status.
    """
    order = get_order_by_id(db, order_id)
    order.status = new_status
    
    if new_status == OrderStatus.COMPLETED:
        order.completed_at = datetime.now()
    
    db.commit()
    db.refresh(order)
    return order

def get_order_items(db: Session, order_id: int) -> List[OrderItem]:
    """
    Get all items for an order.
    """
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
