from pydantic import BaseModel
from typing import Optional
from datetime import date

# Base schema
class ClientBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None

# Schema for creating a new client
class ClientCreate(ClientBase):
    user_id: Optional[int] = None

# Schema for updating a client
class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

# Schema for response
class ClientResponse(ClientBase):
    id: int
    user_id: Optional[int]
    registration_date: Optional[date]
    
    class Config:
        from_attributes = True
