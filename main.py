import json
from typing import List, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

# pip install -r requirements.txt

# --- Імпорти Баз Даних ---

# MySQL
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

# Redis
import redis

# CouchDB
import couchdb

# Neo4j
from neo4j import GraphDatabase


app = FastAPI(title="Sport Complex API")

# ==========================================
# 1. КОНФІГУРАЦІЯ ТА ПІДКЛЮЧЕННЯ
# ==========================================

# --- MySQL Config ---
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sport-complex-cw:sport-complex-cw@127.0.0.1:3306/sport-complex-cw"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Redis Config ---
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

# --- CouchDB Config ---
try:
    couch_server = couchdb.Server('http://couchdb:couchdb@localhost:5984/')
    # Створюємо базу, якщо її немає
    if 'medical_docs' not in couch_server:
        db_couch = couch_server.create('medical_docs')
    else:
        db_couch = couch_server['medical_docs']
except Exception as e:
    print(f"CouchDB Warning: {e}")
    db_couch = None # Обробка помилки підключення

# --- Neo4j Config ---
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jneo4j"))


# ==========================================
# 2. МОДЕЛІ ДАНИХ (MySQL + Pydantic)
# ==========================================

# --- SQLAlchemy Models (Таблиці) ---
class ServiceDB(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True) # Басейн, Сауна...
    requires_medical = Column(Boolean, default=False)

class ClientDB(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    # Зв'язок для історії
    subscriptions = relationship("SubscriptionDB", back_populates="client")

class SubscriptionDB(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    plan_type = Column(String(50)) # unlimited, monthly, one_time
    created_at = Column(DateTime, default=datetime.utcnow)
    # Посилання на мед довідку в CouchDB (якщо треба)
    medical_doc_id = Column(String(100), nullable=True)
    
    client = relationship("ClientDB", back_populates="subscriptions")
    service = relationship("ServiceDB")

# --- Pydantic Models (Валідація вхідних/вихідних даних) ---
class ClientCreate(BaseModel):
    full_name: str
    email: str

class MedicalDocInput(BaseModel):
    client_email: str
    doctor_name: str
    result: str # "fit", "unfit"
    details: dict # Довільні дані (тиск, пульс і т.д.)

class SubscriptionCreate(BaseModel):
    client_id: int
    service_name: str
    plan_type: str # unlimited, monthly, one_time
    medical_doc_id: Optional[str] = None

# ==========================================
# 3. ДОПОМІЖНІ ФУНКЦІЇ
# ==========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ініціалізація БД при старті
@app.on_event("startup")
def startup_event():
    # 1. Створюємо таблиці MySQL
    Base.metadata.create_all(bind=engine)
    
    # 2. Заповнюємо базові послуги (MySQL + Neo4j)
    db = SessionLocal()
    services = [
        {"name": "Pool", "med": True},
        {"name": "Gym", "med": False},
        {"name": "Sauna", "med": False},
        {"name": "Massage", "med": False},
        {"name": "Fitness", "med": False}
    ]
    
    for s in services:
        # MySQL
        exists = db.query(ServiceDB).filter(ServiceDB.name == s["name"]).first()
        if not exists:
            db.add(ServiceDB(name=s["name"], requires_medical=s["med"]))
        
        # Neo4j (Створюємо ноди Послуг для графа)
        with neo4j_driver.session() as session:
            session.run("MERGE (s:Service {name: $name})", name=s["name"])
    
    db.commit()
    db.close()

# ==========================================
# 4. API РУЧКИ (ENDPOINTS)
# ==========================================

# --- Блок 1: Клієнти та Послуги (MySQL + Redis) ---

@app.post("/clients/", response_model=dict)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Реєстрація нового клієнта в MySQL"""
    db_client = ClientDB(full_name=client.full_name, email=client.email)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Створюємо ноду клієнта в Neo4j
    with neo4j_driver.session() as session:
        session.run("MERGE (c:Client {mysql_id: $cid, name: $name})", 
                    cid=db_client.id, name=db_client.full_name)
                    
    return {"status": "created", "id": db_client.id, "name": db_client.full_name}

@app.get("/services/")
def get_services(db: Session = Depends(get_db)):
    """Отримання списку послуг. Спочатку дивимось Redis, потім MySQL."""
    
    # 1. Перевірка кешу Redis
    cached_services = redis_client.get("all_services")
    if cached_services:
        print("DEBUG: Returning from Redis")
        return json.loads(cached_services)

    # 2. Якщо в кеші немає - беремо з MySQL
    print("DEBUG: Returning from MySQL")
    services = db.query(ServiceDB).all()
    result = [{"id": s.id, "name": s.name, "requires_medical": s.requires_medical} for s in services]
    
    # 3. Записуємо в Redis (TTL 60 секунд)
    redis_client.setex("all_services", 60, json.dumps(result))
    
    return result

# --- Блок 2: Медичні довідки (CouchDB) ---

@app.post("/medical-checkup/")
def submit_medical_doc(doc: MedicalDocInput):
    """
    Приймає результати обстеження від клініки.
    Зберігає неструктурований документ в CouchDB.
    """
    if not db_couch:
        raise HTTPException(status_code=500, detail="CouchDB not connected")
    
    # Формуємо документ
    document = {
        "type": "medical_certificate",
        "client_email": doc.client_email,
        "doctor": doc.doctor_name,
        "status": doc.result,
        "timestamp": datetime.utcnow().isoformat(),
        "clinical_data": doc.details # Гнучке поле
    }
    
    # Зберігаємо в CouchDB
    doc_id, doc_rev = db_couch.save(document)
    
    return {
        "status": "received", 
        "couchdb_id": doc_id, 
        "message": "Certificate stored. Use this ID for pool subscription."
    }

# --- Блок 3: Оформлення абонемента (MySQL + Neo4j Logic) ---

@app.post("/subscribe/")
def buy_subscription(sub_data: SubscriptionCreate, db: Session = Depends(get_db)):
    """
    Оформлення клубної картки/послуги.
    Перевіряє наявність довідки для Басейну.
    Пише в MySQL і створює зв'язок в Neo4j.
    """
    
    # 1. Знаходимо послугу
    service = db.query(ServiceDB).filter(ServiceDB.name == sub_data.service_name).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # 2. Перевірка логіки Басейну
    if service.requires_medical:
        if not sub_data.medical_doc_id:
            raise HTTPException(status_code=400, detail="Pool requires a medical certificate ID")
        
        # Тут можна зробити запит в CouchDB щоб перевірити чи документ існує і статус == fit
        # Для простоти - просто віримо наявності ID
        print(f"Linking medical doc {sub_data.medical_doc_id} to subscription")

    # 3. Запис в MySQL (Історія/Абонемент)
    new_sub = SubscriptionDB(
        client_id=sub_data.client_id,
        service_id=service.id,
        plan_type=sub_data.plan_type,
        medical_doc_id=sub_data.medical_doc_id
    )
    db.add(new_sub)
    db.commit()

    # 4. Аналітика в Neo4j (Графовий зв'язок)
    # Створюємо зв'язок: (Client) -> [USES] -> (Service)
    # Зберігаємо також тип абонементу у зв'язку
    query = """
    MATCH (c:Client {mysql_id: $cid})
    MATCH (s:Service {name: $sname})
    MERGE (c)-[r:USES]->(s)
    SET r.last_visit = datetime(), r.plan = $plan
    """
    with neo4j_driver.session() as session:
        session.run(query, cid=sub_data.client_id, sname=service.name, plan=sub_data.plan_type)

    return {"status": "success", "subscription_id": new_sub.id}

# --- Блок 4: Аналітика (Neo4j) ---

@app.get("/analytics/popular")
def get_popular_services():
    """
    Використовує Neo4j для підрахунку популярності.
    Адміністрація дивиться цей звіт.
    """
    query = """
    MATCH (c:Client)-[:USES]->(s:Service)
    RETURN s.name AS Service, count(c) AS Visitors
    ORDER BY Visitors DESC
    """
    
    results = []
    with neo4j_driver.session() as session:
        data = session.run(query)
        for record in data:
            results.append({
                "service": record["Service"],
                "visitors_count": record["Visitors"]
            })
            
    return {"report_type": "Popularity by Client Usage", "data": results}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)