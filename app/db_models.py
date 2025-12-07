from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.config import Base


class SupplierDB(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    city = Column(String(100))
    country = Column(String(100))
    contact_email = Column(String(100))

    products = relationship("ProductDB", back_populates="supplier")


class CategoryDB(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)

    products = relationship("ProductDB", back_populates="category")


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(50), unique=True, index=True)
    name = Column(String(200), index=True)  # Index for search
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)  # Index for filtering
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), index=True)  # Index for filtering
    price = Column(Integer, index=True)  # Index for sorting/filtering
    quantity = Column(Integer, default=0, index=True)  # Index for stock queries
    min_stock = Column(Integer, default=10)
    delivery_days = Column(Integer, default=7)
    image_doc_id = Column(String(100), nullable=True)

    supplier = relationship("SupplierDB", back_populates="products")
    category = relationship("CategoryDB", back_populates="products")
    order_items = relationship("OrderItemDB", back_populates="product")


class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")

    supplier = relationship("SupplierDB")
    items = relationship("OrderItemDB", back_populates="order")


class OrderItemDB(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

    order = relationship("OrderDB", back_populates="items")
    product = relationship("ProductDB", back_populates="order_items")
