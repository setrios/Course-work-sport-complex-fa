from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime



class ClientCreate(BaseModel):
    full_name: str
    email: str
    password: str


class TrainerCreate(BaseModel):
    full_name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class TrainerUpdate(UserUpdate):
    pass


class MedicalDocInput(BaseModel):
    client_email: str
    doctor_name: str
    result: str 
    details: dict 


class SubscriptionCreate(BaseModel):
    client_id: int
    service_name: str
    plan_type: str 
    medical_doc_id: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    plan_type: Optional[str] = None
    medical_doc_id: Optional[str] = None


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    requires_medical: Optional[bool] = None


class SubscriptionCancel(BaseModel):
    client_id: int
    service_name: str


class TrainingSessionOut(BaseModel):
    id: int
    trainer_id: int
    client_id: int
    client_name: Optional[str]
    client_email: Optional[str]
    service_name: Optional[str]
    scheduled_at: datetime
    notes: Optional[str]
    duration_minutes: int
    status: str

    class Config:
        orm_mode = True


class TrainingSessionCreate(BaseModel):
    trainer_id: int
    client_id: int
    service_id: int
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    duration_minutes: Optional[int] = 60


class TrainingSessionCreateNoTrainer(BaseModel):
    client_id: int
    service_id: int
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    duration_minutes: Optional[int] = 60


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int = 0
    description: Optional[str] = None
    available: Optional[bool] = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    available: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    description: Optional[str]
    available: bool

    class Config:
        orm_mode = True


class SpecializationCreate(BaseModel):
    service_id: int


class SpecializationOut(BaseModel):
    id: int
    service_id: int
    service_name: str
    created_at: datetime

    class Config:
        orm_mode = True
