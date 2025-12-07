from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum as SQLEnum, Time
from sqlalchemy.orm import relationship
import enum

from app.config import Base


# ==========================================
# ENUMS
# ==========================================

class MembershipType(str, enum.Enum):
    UNLIMITED = "unlimited"
    MONTHLY_1 = "monthly_1"
    MONTHLY_3 = "monthly_3"
    MONTHLY_6 = "monthly_6"
    MONTHLY_12 = "monthly_12"
    PAY_PER_VISIT = "pay_per_visit"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    FROZEN = "frozen"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    ONLINE = "online"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ==========================================
# SPORT COMPLEX MODELS
# ==========================================

class SportClient(Base):
    """Клієнт спорткомплексу (розширено)"""
    __tablename__ = "sport_clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)  # Посилання на app.auth
    full_name = Column(String(100))
    birth_date = Column(DateTime)
    phone = Column(String(20))
    email = Column(String(100), unique=True)
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))

    # Медичні дані
    medical_certificate_valid_until = Column(DateTime, nullable=True)
    medical_notes = Column(Text, nullable=True)  # Обмеження, алергії тощо
    has_valid_cert = Column(Boolean, default=False)

    # Профіль
    profile_photo_doc_id = Column(String(100), nullable=True)  # CouchDB ID
    fitness_goals = Column(String(200), nullable=True)  # Цілі (weight_loss, muscle_gain, etc)
    experience_level = Column(String(50), default="beginner")  # Рівень підготовки

    # Дані для контакту
    preferred_contact = Column(String(50), default="email")  # email, phone, sms
    receive_notifications = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Зв'язки
    memberships = relationship("SportMembership", back_populates="client")
    visits = relationship("SportVisit", back_populates="client")
    payments = relationship("SportPayment", back_populates="client")
    class_enrollments = relationship("ClassEnrollment", back_populates="client")
    feedback = relationship("TrainerFeedback", back_populates="client")


class SportMembership(Base):
    """Абонемент клієнта"""
    __tablename__ = "sport_memberships"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("sport_clients.id"))
    membership_type = Column(SQLEnum(MembershipType))
    status = Column(SQLEnum(MembershipStatus), default=MembershipStatus.ACTIVE)

    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    frozen_until = Column(DateTime, nullable=True)  # Дата розморожування

    price = Column(Float)  # Ціна абонемента
    visits_included = Column(Integer, nullable=True)  # Для ограниченных абонементів
    visits_used = Column(Integer, default=0)

    auto_renew = Column(Boolean, default=False)  # Автоматичне поновлення

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Зв'язки
    client = relationship("SportClient", back_populates="memberships")
    payments = relationship("SportPayment", back_populates="membership")


class SportService(Base):
    """Послуга/Тип заняття"""
    __tablename__ = "sport_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)  # "Базовий фітнес", "Аквааеробіка"
    description = Column(Text)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    duration_minutes = Column(Integer, default=60)  # Стандартна тривалість

    # Вимоги
    requires_medical_cert = Column(Boolean, default=False)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    # Ціна
    price_per_visit = Column(Float)
    price_monthly = Column(Float, nullable=True)
    price_unlimited = Column(Float, nullable=True)

    # Параметри
    max_capacity = Column(Integer, default=20)
    equipment_needed = Column(String(200), nullable=True)  # JSON або простий текст

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Зв'язки
    schedules = relationship("ClassSchedule", back_populates="service")
    class_enrollments = relationship("ClassEnrollment", back_populates="service")


class SportTrainer(Base):
    """Тренер спорткомплексу"""
    __tablename__ = "sport_trainers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)  # Посилання на app.auth
    full_name = Column(String(100))
    specialization = Column(String(100))  # "Фітнес", "Плавання", "Йога"

    bio = Column(Text, nullable=True)
    experience_years = Column(Integer)
    hourly_rate = Column(Float)  # Оклад за годину (для їх розрахунків)

    phone = Column(String(20))
    email = Column(String(100), unique=True)

    # Сертифікати в CouchDB (doc_ids)
    certifications_doc_ids = Column(String(500), nullable=True)  # JSON

    # Рейтинг
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Зв'язки
    schedules = relationship("ClassSchedule", back_populates="trainer")
    feedback = relationship("TrainerFeedback", back_populates="trainer")


class SportRoom(Base):
    """Залу спорткомплексу"""
    __tablename__ = "sport_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)  # "Кімната 1", "Басейн", "Тренажерний зал"
    capacity = Column(Integer)
    equipment = Column(Text)  # JSON або просто опис

    temperature_optimal = Column(Float, nullable=True)  # Оптимальна температура
    has_shower = Column(Boolean, default=False)
    has_locker_room = Column(Boolean, default=False)

    maintenance_until = Column(DateTime, nullable=True)  # На обслуговуванні до
    is_available = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Зв'язки
    schedules = relationship("ClassSchedule", back_populates="room")


class ClassSchedule(Base):
    """Розклад занять"""
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("sport_services.id"))
    trainer_id = Column(Integer, ForeignKey("sport_trainers.id"))
    room_id = Column(Integer, ForeignKey("sport_rooms.id"))

    day_of_week = Column(Integer)  # 0-6 (пн-нд)
    start_time = Column(Time)
    end_time = Column(Time)

    # Запис
    enrolled_count = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Зв'язки
    service = relationship("SportService", back_populates="schedules")
    trainer = relationship("SportTrainer", back_populates="schedules")
    room = relationship("SportRoom", back_populates="schedules")
    enrollments = relationship("ClassEnrollment", back_populates="schedule")


class ClassEnrollment(Base):
    """Запис клієнта на заняття"""
    __tablename__ = "class_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("sport_clients.id"))
    schedule_id = Column(Integer, ForeignKey("class_schedules.id"))
    service_id = Column(Integer, ForeignKey("sport_services.id"), nullable=True)

    enrolled_date = Column(DateTime, default=datetime.utcnow)
    attended = Column(Boolean, nullable=True)  # True/False/None (невідомо)
    rating_given = Column(Integer, nullable=True)  # 1-5 зірок для тренера

    notes = Column(Text, nullable=True)  # Особисті нотатки клієнта

    # Зв'язки
    client = relationship("SportClient", back_populates="class_enrollments")
    schedule = relationship("ClassSchedule", back_populates="enrollments")
    service = relationship("SportService", back_populates="class_enrollments")


class SportVisit(Base):
    """Відвідування залу (вхід/вихід)"""
    __tablename__ = "sport_visits"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("sport_clients.id"))
    service_id = Column(Integer, ForeignKey("sport_services.id"), nullable=True)  # Яку послугу клієнт користував

    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Параметри сеансу
    heart_rate_start = Column(Integer, nullable=True)  # Пульс на вході
    heart_rate_end = Column(Integer, nullable=True)
    calories_burned = Column(Float, nullable=True)

    room_id = Column(Integer, ForeignKey("sport_rooms.id"), nullable=True)
    trainer_id = Column(Integer, ForeignKey("sport_trainers.id"), nullable=True)  # Хто тренував

    notes = Column(Text, nullable=True)

    # Зв'язки
    client = relationship("SportClient", back_populates="visits")


class SportPayment(Base):
    """Платіж за послуги"""
    __tablename__ = "sport_payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("sport_clients.id"))
    membership_id = Column(Integer, ForeignKey("sport_memberships.id"), nullable=True)

    amount = Column(Float)
    payment_method = Column(SQLEnum(PaymentMethod))
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)

    payment_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime, nullable=True)

    description = Column(String(200))  # "Абонемент MONTHLY_3", "Pay-per-visit"
    transaction_id = Column(String(100), nullable=True)  # ID з платіжної системи

    receipt_doc_id = Column(String(100), nullable=True)  # CouchDB ID чеку

    # Зв'язки
    client = relationship("SportClient", back_populates="payments")
    membership = relationship("SportMembership", back_populates="payments")


class TrainerFeedback(Base):
    """Відзив про тренера"""
    __tablename__ = "trainer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("sport_trainers.id"))
    client_id = Column(Integer, ForeignKey("sport_clients.id"))

    rating = Column(Integer)  # 1-5
    comment = Column(Text)

    verified_purchase = Column(Boolean, default=True)  # Чи клієнт мав абонемент
    helpful_count = Column(Integer, default=0)  # Скільки людей позначили як корисне

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Зв'язки
    trainer = relationship("SportTrainer", back_populates="feedback")
    client = relationship("SportClient", back_populates="feedback")


class Promotion(Base):
    """Акція/Пропозиція"""
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True)  # "NEWMEMBER20", "SUMMER50"
    description = Column(String(200))

    discount_percent = Column(Float, nullable=True)  # % знижки
    discount_amount = Column(Float, nullable=True)  # Або фіксована сума

    valid_from = Column(DateTime)
    valid_until = Column(DateTime)

    max_uses = Column(Integer, nullable=True)  # Скільки разів можна використати
    current_uses = Column(Integer, default=0)

    applicable_memberships = Column(String(500), nullable=True)  # JSON масив типів
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Зв'язки
    # можна додати many-to-many через association table


class MaintenanceLog(Base):
    """Лог обслуговування обладнання"""
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("sport_rooms.id"), nullable=True)

    maintenance_type = Column(String(100))  # "Repair", "Inspection", "Cleaning"
    description = Column(Text)
    performed_by = Column(String(100))

    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)

    cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
