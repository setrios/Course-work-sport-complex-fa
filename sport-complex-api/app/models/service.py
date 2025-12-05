from sqlalchemy import Column, Integer, String, Text, Enum, Numeric, ForeignKey, DateTime, Time, Date
from sqlalchemy.sql import func
from app.db.mysql_session import Base
import enum

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    capacity = Column(Integer)
    base_price = Column(Numeric(10, 2))

class SessionType(str, enum.Enum):
    PERSONAL = "personal"
    GROUP = "group"
    CONSULTATION = "consultation"

class SessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer)
    session_type = Column(Enum(SessionType), nullable=False)
    max_participants = Column(Integer, default=1)
    current_participants = Column(Integer, default=0)
    price = Column(Numeric(10, 2))
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    notes = Column(Text)
    cancellation_reason = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
