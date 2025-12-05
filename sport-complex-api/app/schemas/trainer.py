from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, time, date
from app.models.trainer import TrainerSpecialization, TrainerStatus

# Trainer Schemas
class TrainerBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: TrainerSpecialization
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    experience_years: Optional[int] = None
    certification: Optional[str] = None
    hourly_rate: Optional[float] = None

class TrainerCreate(TrainerBase):
    pass

class TrainerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    experience_years: Optional[int] = None
    certification: Optional[str] = None
    hourly_rate: Optional[float] = None
    status: Optional[TrainerStatus] = None

class TrainerResponse(TrainerBase):
    id: int
    rating: float
    total_sessions: int
    status: TrainerStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schedule Schemas
class ScheduleBase(BaseModel):
    day_of_week: int  # 0-6
    start_time: time
    end_time: time
    service_id: Optional[int] = None

class ScheduleCreate(ScheduleBase):
    trainer_id: int

class ScheduleResponse(ScheduleBase):
    id: int
    trainer_id: int
    is_active: bool
    
    class Config:
        from_attributes = True
