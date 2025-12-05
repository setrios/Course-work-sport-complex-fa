from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime, date

# Product Category Schemas
class ProductCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryResponse(ProductCategoryBase):
    id: int
    display_order: int
    is_active: bool
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    article_number: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: float
    quantity_in_stock: int = 0
    is_active: bool = True
    is_featured: bool = False

class ProductCreate(ProductBase):
    ingredients: Optional[str] = None
    nutritional_info: Optional[Dict] = None
    serving_size: Optional[str] = None
    servings_per_container: Optional[int] = None
    cost_price: Optional[float] = None
    min_stock_level: int = 5
    unit: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity_in_stock: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str]
    tags: Optional[List] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
