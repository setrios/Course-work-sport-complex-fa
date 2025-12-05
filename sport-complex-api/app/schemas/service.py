from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time, date
from app.models.service import SessionType, SessionStatus

# Service Schemas
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    capacity: Optional[int] = None
    base_price: Optional[float] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: int
    
    class Config:
        from_attributes = True

# Training Session Schemas
class TrainingSessionBase(BaseModel):
    trainer_id: int
    service_id: Optional[int] = None
    session_date: date
    start_time: time
    end_time: time
    session_type: SessionType
    max_participants: int = 1
    price: Optional[float] = None

class TrainingSessionCreate(TrainingSessionBase):
    client_id: Optional[int] = None

class TrainingSessionResponse(TrainingSessionBase):
    id: int
    client_id: Optional[int]
    duration_minutes: Optional[int]
    current_participants: int
    status: SessionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True
