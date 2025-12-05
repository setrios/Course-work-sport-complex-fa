from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime, Date, JSON
from sqlalchemy.sql import func
from app.db.mysql_session import Base

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_category_id = Column(Integer, ForeignKey("product_categories.id"))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    article_number = Column(String(50), unique=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    brand = Column(String(100))
    description = Column(Text)
    ingredients = Column(Text)
    nutritional_info = Column(JSON)
    serving_size = Column(String(50))
    servings_per_container = Column(Integer)
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    quantity_in_stock = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)
    max_stock_level = Column(Integer)
    unit = Column(String(20))
    weight = Column(Numeric(8, 2))
    volume = Column(Numeric(8, 2))
    expiry_date = Column(Date)
    image_url = Column(String(500))
    images = Column(JSON)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    tags = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ProductPromotion(Base):
    __tablename__ = "product_promotions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    discount_percentage = Column(Numeric(5, 2))
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
