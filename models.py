from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Float, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sport-complex-cw:sport-complex-cw@127.0.0.1:3306/sport-complex-cw"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ServiceDB(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True) 
    requires_medical = Column(Boolean, default=False)


class ClientDB(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))  # Store hashed password
    # role: 'client', 'trainer', 'admin' — keeps users in one table and allows easy filtering
    role = Column(String(20), default="client", index=True)
    subscriptions = relationship("SubscriptionDB", back_populates="client")


class SubscriptionDB(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    plan_type = Column(String(50)) 
    created_at = Column(DateTime, default=datetime.utcnow)
    medical_doc_id = Column(String(100), nullable=True)
    
    client = relationship("ClientDB", back_populates="subscriptions")
    service = relationship("ServiceDB")


class TrainingSessionDB(Base):
    __tablename__ = "training_sessions"
    id = Column(Integer, primary_key=True, index=True)
    # allow trainer_id to be nullable for sessions created without an assigned trainer
    trainer_id = Column(Integer, ForeignKey("clients.id"), index=True, nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(255), nullable=True)
    duration_minutes = Column(Integer, default=60)  # default session duration: 1 hour
    status = Column(String(20), default="scheduled", index=True)  # scheduled, in_progress, completed, cancelled

    trainer = relationship("ClientDB", foreign_keys=[trainer_id])
    client = relationship("ClientDB", foreign_keys=[client_id])
    service = relationship("ServiceDB")


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True)
    price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    description = Column(String(500), nullable=True)
    available = Column(Boolean, default=True, index=True)


class SpecializationDB(Base):
    __tablename__ = "specializations"
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("clients.id"), index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trainer = relationship("ClientDB", foreign_keys=[trainer_id])
    service = relationship("ServiceDB")
