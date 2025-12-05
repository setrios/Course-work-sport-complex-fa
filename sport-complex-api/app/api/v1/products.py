from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductCategoryCreate, ProductCategoryResponse
)
from app.services.product_service import (
    get_products, get_product_by_id, create_product, 
    update_product, delete_product, get_categories, create_category
)
from app.db.mysql_session import get_db

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None,
    is_featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all products with optional filters.
    """
    return get_products(db, skip, limit, category_id, is_featured)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    return get_product_by_id(db, product_id)

@router.post("/", response_model=ProductResponse, status_code=201)
def create_new_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    """
    return create_product(db, product_data)

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_info(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update product information.
    """
    return update_product(db, product_id, product_data)

@router.delete("/{product_id}")
def delete_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """
    Deactivate a product.
    """
    return delete_product(db, product_id)

# Categories
@router.get("/categories/", response_model=List[ProductCategoryResponse], tags=["Product Categories"])
def list_categories(db: Session = Depends(get_db)):
    """
    Get all product categories.
    """
    return get_categories(db)

@router.post("/categories/", response_model=ProductCategoryResponse, status_code=201, tags=["Product Categories"])
def create_new_category(category_data: ProductCategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new product category.
    """
    return create_category(db, category_data)
