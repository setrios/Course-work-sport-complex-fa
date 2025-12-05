from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate, ProductCategoryCreate
from typing import List, Optional

def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    is_featured: Optional[bool] = None
) -> List[Product]:
    """
    Get all products with optional filters.
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    return query.offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Product:
    """
    Get a product by ID with Redis caching.
    """
    from app.services.redis_service import RedisService
    
    # Try cache first
    cached = RedisService.get_cached_product(product_id)
    if cached:
        return Product(**cached)
    
    # Get from DB
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Cache for future requests
    product_dict = {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "quantity_in_stock": product.quantity_in_stock,
        "is_active": product.is_active
    }
    RedisService.cache_product(product_id, product_dict)
    
    return product

def create_product(db: Session, product_data: ProductCreate) -> Product:
    """
    Create a new product.
    """
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Product:
    """
    Update product information and invalidate cache.
    """
    from app.services.redis_service import RedisService
    
    product = get_product_by_id(db, product_id)
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    # Invalidate cache
    RedisService.invalidate_product_cache(product_id)
    
    return product

def delete_product(db: Session, product_id: int):
    """
    Delete (deactivate) a product.
    """
    product = get_product_by_id(db, product_id)
    product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully"}

# Product Categories
def get_categories(db: Session) -> List[ProductCategory]:
    """
    Get all product categories.
    """
    return db.query(ProductCategory).filter(ProductCategory.is_active == True).all()

def create_category(db: Session, category_data: ProductCategoryCreate) -> ProductCategory:
    """
    Create a new product category.
    """
    new_category = ProductCategory(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category
