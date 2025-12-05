from sqlalchemy import Column, Integer, String, Text, Enum, Numeric, ForeignKey, DateTime, Time, Date, Boolean, SmallInteger
from sqlalchemy.sql import func
from app.db.mysql_session import Base
import enum

class TrainerSpecialization(str, enum.Enum):
    FITNESS = "fitness"
    GYM = "gym"
    POOL = "pool"
    MASSAGE = "massage"

class TrainerStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    INACTIVE = "inactive"

class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    specialization = Column(Enum(TrainerSpecialization), nullable=False)
    bio = Column(Text)
    photo_url = Column(String(500))
    experience_years = Column(Integer)
    certification = Column(Text)
    hourly_rate = Column(Numeric(10, 2))
    rating = Column(Numeric(3, 2), default=0.00)
    total_sessions = Column(Integer, default=0)
    status = Column(Enum(TrainerStatus), default=TrainerStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class TrainerSchedule(Base):
    __tablename__ = "trainer_schedules"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    day_of_week = Column(SmallInteger)  # 0-6, 0=Monday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))
    is_active = Column(Boolean, default=True)

class TrainerScheduleException(Base):
    __tablename__ = "trainer_schedule_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    exception_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    reason = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
