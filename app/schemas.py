from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from sport_complex import Gender
from app.sport_models import (
    MembershipType, MembershipStatus, PaymentMethod, PaymentStatus, DifficultyLevel
)


class SupplierCreate(BaseModel):
    name: str
    city: str
    country: str
    contact_email: str


class CategoryCreate(BaseModel):
    name: str


class ProductCreate(BaseModel):
    article: str
    name: str
    category_name: str
    supplier_name: str
    price: float
    quantity: int
    min_stock: int = 10
    delivery_days: int = 7


class ProductImageUpload(BaseModel):
    article: str
    image_base64: str
    mime_type: str


class OrderCreate(BaseModel):
    supplier_id: int
    items: List[dict]


class ContactInfoModel(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class ClientCreate(BaseModel):
    full_name: str
    birth_date: date
    gender: str
    contact_info: Optional[Union[dict, ContactInfoModel]] = None
    username: str
    password: str


class ClientUpdate(BaseModel):
    full_name: str
    birth_date: date
    gender: str
    contact_info: Optional[Union[dict, ContactInfoModel]] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserProfileUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class MembershipCreate(BaseModel):
    client_id: str
    service_id: str
    start_date: date
    end_date: date
    status: Optional[str] = "active"


class TrainerCreate(BaseModel):
    full_name: str
    birth_date: date
    gender: str
    specialization: str
    contact_info: Optional[ContactInfoModel] = None


class ServiceCreate(BaseModel):
    service_name: str
    price: float
    requires_medical_certificate: bool = False


class MedicalCertificateCreate(BaseModel):
    client_id: str
    clinic_name: str
    examination_result: str
    examination_date: date
    expiry_date: date


class VisitCreate(BaseModel):
    client_id: str
    service_id: str
    entry_time: Optional[datetime] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class ProductListQuery(BaseModel):
    """Query parameters for product list with pagination and filters."""
    page: int = Field(default=1, ge=1, description="Номер сторінки")
    page_size: int = Field(default=20, ge=1, le=100, description="Розмір сторінки")
    category: Optional[str] = Field(default=None, description="Фільтр по категорії")
    supplier: Optional[str] = Field(default=None, description="Фільтр по постачальнику")
    min_price: Optional[float] = Field(default=None, ge=0, description="Мінімальна ціна")
    max_price: Optional[float] = Field(default=None, ge=0, description="Максимальна ціна")
    in_stock: Optional[bool] = Field(default=None, description="Тільки в наявності")
    search: Optional[str] = Field(default=None, description="Пошук по назві")
    sort_by: Optional[str] = Field(default="name", description="Поле сортування: name, price, quantity")
    sort_order: Optional[str] = Field(default="asc", description="Порядок: asc або desc")


class ClientListQuery(BaseModel):
    """Query parameters for client list with pagination and filters."""
    page: int = Field(default=1, ge=1, description="Номер сторінки")
    page_size: int = Field(default=20, ge=1, le=100, description="Розмір сторінки")
    search: Optional[str] = Field(default=None, description="Пошук по імені")
    has_membership: Optional[bool] = Field(default=None, description="Має активний абонемент")
    sort_by: Optional[str] = Field(default="full_name", description="Поле сортування")
    sort_order: Optional[str] = Field(default="asc", description="Порядок: asc або desc")

