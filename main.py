import json
from typing import List, Optional
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Float, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

import redis
import couchdb
from neo4j import GraphDatabase

from jose import JWTError, jwt
from passlib.context import CryptContext

from dotenv import load_dotenv
import os

load_dotenv()


app = FastAPI(title="Sport Complex API")

# Auth configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://sport-complex-cw:sport-complex-cw@127.0.0.1:3306/sport-complex-cw"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

try:
    couch_server = couchdb.Server('http://couchdb:couchdb@localhost:5984/')
    if 'medical_docs' not in couch_server:
        db_couch = couch_server.create('medical_docs')
    else:
        db_couch = couch_server['medical_docs']
except Exception as e:
    print(f"CouchDB Warning: {e}")
    db_couch = None 

neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jneo4j"))



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
    # trainer specialization (nullable) — used when role == 'trainer'
    specialization = Column(String(100), nullable=True, index=True)
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



class ClientCreate(BaseModel):
    full_name: str
    email: str
    password: str


class TrainerCreate(BaseModel):
    full_name: str
    email: str
    password: str
    specialization: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class TrainerUpdate(UserUpdate):
    specialization: Optional[str] = None

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

    class Config:
        orm_mode = True


class TrainingSessionCreate(BaseModel):
    trainer_id: int
    client_id: int
    service_id: int
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None


class TrainingSessionCreateNoTrainer(BaseModel):
    client_id: int
    service_id: int
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None


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



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Auth utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    # Ensure password is a string
    if not isinstance(password, str):
        password = str(password)
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_email(db: Session, email: str):
    return db.query(ClientDB).filter(ClientDB.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: ClientDB = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker



@app.on_event("startup")
def startup_event():
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    services = [
        {"name": "Pool", "med": True},
        {"name": "Gym", "med": False},
        {"name": "Sauna", "med": False},
        {"name": "Massage", "med": False},
        {"name": "Fitness", "med": False}
    ]
    
    for s in services:
        exists = db.query(ServiceDB).filter(ServiceDB.name == s["name"]).first()
        if not exists:
            db.add(ServiceDB(name=s["name"], requires_medical=s["med"]))
        
        with neo4j_driver.session() as session:
            session.run("MERGE (s:Service {name: $name})", name=s["name"])
    
    db.commit()
    db.close()



@app.post("/login", response_model=dict)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "role": user.role}


@app.get("/me", response_model=dict)
def get_current_user_info(current_user: ClientDB = Depends(get_current_user)):
    """Get current authenticated user's information"""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "specialization": current_user.specialization if current_user.role == "trainer" else None
    }


@app.post("/clients/", response_model=dict)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Реєстрація нового клієнта в MySQL"""
    # prevent duplicate emails
    existing = db.query(ClientDB).filter(ClientDB.email == client.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_client = ClientDB(
        full_name=client.full_name, 
        email=client.email, 
        password_hash=get_password_hash(client.password),
        role="client"
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    # create corresponding node in Neo4j with Client label
    with neo4j_driver.session() as session:
        session.run("MERGE (c:Client {mysql_id: $cid, name: $name})", 
                    cid=db_client.id, name=db_client.full_name)

    return {"status": "created", "id": db_client.id, "name": db_client.full_name}


@app.post("/trainers/", response_model=dict)
def create_trainer(trainer: TrainerCreate, db: Session = Depends(get_db)):
    """Register a new trainer in MySQL (accepts specialization)."""
    # prevent duplicate emails
    existing = db.query(ClientDB).filter(ClientDB.email == trainer.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_trainer = ClientDB(
        full_name=trainer.full_name,
        email=trainer.email,
        password_hash=get_password_hash(trainer.password),
        role="trainer",
        specialization=trainer.specialization
    )
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)

    # create corresponding node in Neo4j with Trainer label and specialization
    with neo4j_driver.session() as session:
        session.run(
            "MERGE (t:Trainer {mysql_id: $tid, name: $name}) SET t.specialization = $spec",
            tid=db_trainer.id, name=db_trainer.full_name, spec=db_trainer.specialization
        )

    return {"status": "created", "id": db_trainer.id, "name": db_trainer.full_name}


@app.post("/admins/", response_model=dict)
def create_admin(admin: ClientCreate, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Реєстрація адміністратора (admin role) в MySQL - requires admin authentication"""
    existing = db.query(ClientDB).filter(ClientDB.email == admin.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_admin = ClientDB(
        full_name=admin.full_name, 
        email=admin.email, 
        password_hash=get_password_hash(admin.password),
        role="admin"
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    # NO NEED FOR ADMIN - create corresponding node in Neo4j with Admin label
    # with neo4j_driver.session() as session:
    #     session.run("MERGE (a:Admin {mysql_id: $aid, name: $name})", 
    #                 aid=db_admin.id, name=db_admin.full_name)

    return {"status": "created", "id": db_admin.id, "name": db_admin.full_name}


# FOR FIRST ADMIN CREATION - DELETE AFTER CREATING THE FIRST ADMIN
@app.post("/admins/first-admin", response_model=dict)
def create_first_admin(admin: ClientCreate, db: Session = Depends(get_db)):
    """Create the first admin - only works if no admins exist in the system.
    This endpoint should be removed or disabled after creating the first admin.
    """
    # Check if any admin already exists
    existing_admin = db.query(ClientDB).filter(ClientDB.role == "admin").first()
    if existing_admin:
        raise HTTPException(
            status_code=403, 
            detail="First admin already exists. Use /admins/ endpoint with admin authentication."
        )
    
    # Check if email is already registered
    existing = db.query(ClientDB).filter(ClientDB.email == admin.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_admin = ClientDB(
        full_name=admin.full_name, 
        email=admin.email, 
        password_hash=get_password_hash(admin.password),
        role="admin"
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return {"status": "created", "id": db_admin.id, "name": db_admin.full_name, "message": "First admin created successfully"}


@app.get("/clients/list")
def list_clients(current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """List all clients - Admin only."""
    clients = db.query(ClientDB).filter(ClientDB.role == "client").all()
    return [{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role
    } for u in clients]


@app.get("/clients/{client_id}")
def get_client(client_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return a single client by id - Clients can only view their own profile, admins can view any."""
    client = db.query(ClientDB).filter(ClientDB.id == client_id, ClientDB.role == "client").first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Clients can only view their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != client_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")

    return {"id": client.id, "full_name": client.full_name, "email": client.email, "role": client.role}


@app.delete("/clients/{client_id}", response_model=dict)
def delete_client(client_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a client if no subscriptions or sessions reference them.
    
    Clients can only delete their own profile, admins can delete any.
    Prevents accidental data loss; removes Neo4j node (best-effort).
    """
    client = db.query(ClientDB).filter(ClientDB.id == client_id, ClientDB.role == "client").first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Clients can only delete their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != client_id:
        raise HTTPException(status_code=403, detail="You can only delete your own profile")
    # Cascade-delete: remove training sessions and subscriptions belonging to this client
    # First, fetch and delete sessions where the client is the participant
    sessions = db.query(TrainingSessionDB).filter(TrainingSessionDB.client_id == client_id).all()
    for s in sessions:
        db.delete(s)

    # Then delete subscriptions belonging to this client
    subs = db.query(SubscriptionDB).filter(SubscriptionDB.client_id == client_id).all()
    for sub in subs:
        db.delete(sub)

    # Finally remove the client record
    db.delete(client)
    db.commit()

    # best-effort: remove Neo4j relationships (USES, SCHEDULED, SCHEDULED_UNASSIGNED) and the client node
    try:
        with neo4j_driver.session() as session:
            # delete USES relationships
            session.run("MATCH (c:Client {mysql_id: $cid})-[r:USES]->(s:Service) DELETE r", cid=client_id)
            # delete scheduled relationships where client is source
            session.run("MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED]->(t:Trainer) DELETE r", cid=client_id)
            session.run("MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED_UNASSIGNED]->(s:Service) DELETE r", cid=client_id)
            # finally remove/detach the client node
            session.run("MATCH (c:Client {mysql_id: $cid}) DETACH DELETE c", cid=client_id)
    except Exception:
        pass

    return {"status": "deleted", "id": client_id, "full_name": client.full_name}


@app.get("/trainers/list")
def list_trainers(current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """List all trainers - Admin only."""
    trainers = db.query(ClientDB).filter(ClientDB.role == "trainer").all()
    return [{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role,
        "specialization": u.specialization
    } for u in trainers]


@app.get("/trainers/{trainer_id}")
def get_trainer(trainer_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return a single trainer by id - Trainers can only view their own profile, admins can view any."""
    trainer = db.query(ClientDB).filter(ClientDB.id == trainer_id, ClientDB.role == "trainer").first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Trainers can only view their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != trainer_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")

    return {"id": trainer.id, "full_name": trainer.full_name, "email": trainer.email, "role": trainer.role, "specialization": trainer.specialization}


@app.delete("/trainers/{trainer_id}", response_model=dict)
def delete_trainer(trainer_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a trainer if no training sessions reference them.
    
    Trainers can only delete their own profile, admins can delete any.
    Prevents accidental data loss; removes Neo4j node (best-effort).
    """
    trainer = db.query(ClientDB).filter(ClientDB.id == trainer_id, ClientDB.role == "trainer").first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Trainers can only delete their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != trainer_id:
        raise HTTPException(status_code=403, detail="You can only delete your own profile")

    # check references: trainer assigned sessions
    sess_count = db.query(TrainingSessionDB).filter(TrainingSessionDB.trainer_id == trainer_id).count()
    if sess_count > 0:
        raise HTTPException(status_code=400, detail=f"Trainer cannot be deleted: {sess_count} sessions reference them")

    # best-effort: remove Neo4j node and relationships
    try:
        with neo4j_driver.session() as session:
            session.run("MATCH (t:Trainer {mysql_id: $tid}) DETACH DELETE t", tid=trainer_id)
    except Exception:
        pass

    db.delete(trainer)
    db.commit()

    return {"status": "deleted", "id": trainer_id, "full_name": trainer.full_name}


@app.get("/admins/list")
def list_admins(current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """List all admins - Admin only."""
    admins = db.query(ClientDB).filter(ClientDB.role == "admin").all()
    return [{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role
    } for u in admins]


@app.get("/admins/{admin_id}")
def get_admin(admin_id: int, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Return a single admin by id - Admin only."""
    admin = db.query(ClientDB).filter(ClientDB.id == admin_id, ClientDB.role == "admin").first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"id": admin.id, "full_name": admin.full_name, "email": admin.email, "role": admin.role}


@app.delete("/admins/{admin_id}", response_model=dict)
def delete_admin(admin_id: int, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Delete an admin. Removes Neo4j node (best-effort).

    Note: this does not enforce a 'last-admin' protection.
    """
    admin = db.query(ClientDB).filter(ClientDB.id == admin_id, ClientDB.role == "admin").first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # best-effort: remove Neo4j node
    try:
        with neo4j_driver.session() as session:
            session.run("MATCH (a:Admin {mysql_id: $aid}) DETACH DELETE a", aid=admin_id)
    except Exception:
        pass

    db.delete(admin)
    db.commit()

    return {"status": "deleted", "id": admin_id, "full_name": admin.full_name}


@app.put("/clients/{client_id}")
def update_client(client_id: int, data: UserUpdate, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update client data - users can only update their own profile, admins can update any."""
    client = db.query(ClientDB).filter(ClientDB.id == client_id, ClientDB.role == "client").first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Users can only update their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != client_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # prevent email collisions
    if data.email:
        exists = db.query(ClientDB).filter(ClientDB.email == data.email, ClientDB.id != client_id).first()
        if exists:
            raise HTTPException(status_code=409, detail="Email already registered")
        client.email = data.email

    if data.full_name:
        client.full_name = data.full_name

    db.commit()
    db.refresh(client)

    return {"status": "updated", "id": client.id, "full_name": client.full_name, "email": client.email}


@app.put("/trainers/{trainer_id}")
def update_trainer(trainer_id: int, data: TrainerUpdate, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update trainer data - trainers can update their own profile, admins can update any."""
    trainer = db.query(ClientDB).filter(ClientDB.id == trainer_id, ClientDB.role == "trainer").first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Trainers can only update their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != trainer_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")

    # prevent email collisions
    if data.email:
        exists = db.query(ClientDB).filter(ClientDB.email == data.email, ClientDB.id != trainer_id).first()
        if exists:
            raise HTTPException(status_code=409, detail="Email already registered")
        trainer.email = data.email

    if data.full_name:
        trainer.full_name = data.full_name

    if data.specialization is not None:
        trainer.specialization = data.specialization

    db.commit()
    db.refresh(trainer)

    return {"status": "updated", "id": trainer.id, "full_name": trainer.full_name, "email": trainer.email, "specialization": trainer.specialization}


@app.put("/admins/{admin_id}")
def update_admin(admin_id: int, data: UserUpdate, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Update admin data - admins can update their own profile or other admins."""
    admin = db.query(ClientDB).filter(ClientDB.id == admin_id, ClientDB.role == "admin").first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # prevent email collisions
    if data.email:
        exists = db.query(ClientDB).filter(ClientDB.email == data.email, ClientDB.id != admin_id).first()
        if exists:
            raise HTTPException(status_code=409, detail="Email already registered")
        admin.email = data.email

    if data.full_name:
        admin.full_name = data.full_name

    db.commit()
    db.refresh(admin)

    return {"status": "updated", "id": admin.id, "full_name": admin.full_name, "email": admin.email}


@app.get("/trainers/{trainer_id}/sessions")
def get_trainer_sessions(trainer_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all training sessions for the given trainer.
    
    Trainers can only view their own sessions, admins can view any trainer's sessions.
    This endpoint verifies the trainer exists and has role 'trainer'.
    It returns session info with client name/email and service name.
    """
    trainer = db.query(ClientDB).filter(ClientDB.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Trainers can only view their own sessions unless they're admin
    if current_user.role != "admin" and current_user.id != trainer_id:
        raise HTTPException(status_code=403, detail="You can only view your own sessions")

    sessions = db.query(TrainingSessionDB).filter(TrainingSessionDB.trainer_id == trainer_id).all()
    result = []
    for s in sessions:
        client = db.query(ClientDB).filter(ClientDB.id == s.client_id).first()
        service = None
        if s.service_id:
            service = db.query(ServiceDB).filter(ServiceDB.id == s.service_id).first()

        result.append({
            "id": s.id,
            "trainer_id": s.trainer_id,
            "client_id": s.client_id,
            "client_name": client.full_name if client else None,
            "client_email": client.email if client else None,
            "service_name": service.name if service else None,
            "scheduled_at": s.scheduled_at,
            "notes": s.notes
        })

    return result


@app.post("/sessions/", response_model=dict)
def create_session(payload: TrainingSessionCreate, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clients create a training session with a trainer for a service.

    Validations:
    - trainer exists and has role 'trainer'
    - client exists and has role 'client'
    - client has an active subscription for the specified service (SubscriptionDB entry)
    """
    # verify client exists
    client = db.query(ClientDB).filter(ClientDB.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # verify trainer exists
    trainer = db.query(ClientDB).filter(ClientDB.id == payload.trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    # verify service
    service = db.query(ServiceDB).filter(ServiceDB.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # verify subscription exists for client and service
    sub = db.query(SubscriptionDB).filter(
        SubscriptionDB.client_id == payload.client_id,
        SubscriptionDB.service_id == payload.service_id
    ).first()
    if not sub:
        raise HTTPException(status_code=400, detail="Client does not have a subscription for this service")

    # optionally, if service requires medical doc, ensure subscription has medical_doc_id
    if service.requires_medical and not sub.medical_doc_id:
        raise HTTPException(status_code=400, detail="Service requires a medical certificate; subscription missing medical_doc_id")

    scheduled = payload.scheduled_at if payload.scheduled_at else datetime.utcnow()

    ts = TrainingSessionDB(
        trainer_id=payload.trainer_id,
        client_id=payload.client_id,
        service_id=payload.service_id,
        scheduled_at=scheduled,
        notes=payload.notes
    )
    db.add(ts)
    db.commit()
    db.refresh(ts)

    # Optionally, create relationship in Neo4j to track scheduled sessions (lightweight)
    try:
        with neo4j_driver.session() as session:
            session.run(
                "MATCH (t:Trainer {mysql_id: $tid}), (c:Client {mysql_id: $cid}), (s:Service {name: $sname}) \
                 MERGE (c)-[:SCHEDULED {at: datetime(), scheduled_for: $scheduled}]->(t)",
                tid=trainer.id, cid=client.id, sname=service.name, scheduled=scheduled.isoformat()
            )
    except Exception:
        # don't fail the request if Neo4j write fails; log would be better in real app
        pass

    return {"status": "created", "session_id": ts.id, "scheduled_at": ts.scheduled_at}


@app.post("/sessions/unassigned/", response_model=dict)
def create_unassigned_session(payload: TrainingSessionCreateNoTrainer, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clients create a training session WITHOUT specifying a trainer.

    Validations:
    - client exists and has role 'client'
    - service exists
    - client has a subscription for that service
    """
    # verify client exists
    client = db.query(ClientDB).filter(ClientDB.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Clients can only create sessions for themselves unless they're admin
    if current_user.role != "admin" and current_user.id != payload.client_id:
        raise HTTPException(status_code=403, detail="You can only create sessions for yourself")

    # verify service
    service = db.query(ServiceDB).filter(ServiceDB.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # verify subscription exists for client and service
    sub = db.query(SubscriptionDB).filter(
        SubscriptionDB.client_id == payload.client_id,
        SubscriptionDB.service_id == payload.service_id
    ).first()
    if not sub:
        raise HTTPException(status_code=400, detail="Client does not have a subscription for this service")

    # optionally, if service requires medical doc, ensure subscription has medical_doc_id
    if service.requires_medical and not sub.medical_doc_id:
        raise HTTPException(status_code=400, detail="Service requires a medical certificate; subscription missing medical_doc_id")

    scheduled = payload.scheduled_at if payload.scheduled_at else datetime.utcnow()

    ts = TrainingSessionDB(
        trainer_id=None,
        client_id=payload.client_id,
        service_id=payload.service_id,
        scheduled_at=scheduled,
        notes=payload.notes
    )
    db.add(ts)
    db.commit()
    db.refresh(ts)

    # Optionally, track the unassigned session in Neo4j (link client and service)
    try:
        with neo4j_driver.session() as session:
            session.run(
                "MATCH (c:Client {mysql_id: $cid}), (s:Service {name: $sname}) \n"
                "MERGE (c)-[:SCHEDULED_UNASSIGNED {at: datetime(), scheduled_for: $scheduled}]->(s)",
                cid=client.id, sname=service.name, scheduled=scheduled.isoformat()
            )
    except Exception:
        pass

    return {"status": "created", "session_id": ts.id, "scheduled_at": ts.scheduled_at}


@app.delete("/clients/{client_id}/sessions/{session_id}", response_model=dict)
def delete_client_session(client_id: int, session_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a session - clients can only delete their own sessions, admins can delete any."""
    sess = db.query(TrainingSessionDB).filter(TrainingSessionDB.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Users can only delete their own sessions unless they're admin
    if current_user.role != "admin" and current_user.id != sess.client_id:
        raise HTTPException(status_code=403, detail="You can only delete your own sessions")

    db.delete(sess)
    db.commit()

    # best-effort: try to remove related Neo4j scheduling relationships if possible
    try:
        with neo4j_driver.session() as session:
            if sess.trainer_id:
                session.run(
                    "MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED]->(t:Trainer {mysql_id: $tid}) DELETE r",
                    cid=sess.client_id, tid=sess.trainer_id
                )
            else:
                if sess.service_id:
                    svc_obj = db.query(ServiceDB).filter(ServiceDB.id == sess.service_id).first()
                    if svc_obj:
                        session.run(
                            "MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED_UNASSIGNED]->(s:Service {name: $sname}) DELETE r",
                            cid=sess.client_id, sname=svc_obj.name
                        )
    except Exception:
        pass

    return {"status": "deleted", "session_id": session_id}


@app.delete("/trainers/{trainer_id}/sessions/{session_id}", response_model=dict)
def delete_trainer_session(trainer_id: int, session_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a session - trainers can only delete their own sessions, admins can delete any."""
    sess = db.query(TrainingSessionDB).filter(TrainingSessionDB.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Trainers can only delete sessions assigned to them unless they're admin
    if current_user.role != "admin" and current_user.id != sess.trainer_id:
        raise HTTPException(status_code=403, detail="You can only delete sessions assigned to you")

    db.delete(sess)
    db.commit()

    # best-effort: remove Neo4j scheduled relation
    try:
        with neo4j_driver.session() as session:
            session.run(
                "MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED]->(t:Trainer {mysql_id: $tid}) DELETE r",
                cid=sess.client_id, tid=sess.trainer_id
            )
    except Exception:
        pass

    return {"status": "deleted", "session_id": session_id}

@app.delete("/sessions/{session_id}", response_model=dict)
def delete_session(session_id: int, client_id: Optional[int] = None, trainer_id: Optional[int] = None, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a session by ID with optional validation.

    If client_id provided, verifies the session belongs to that client.
    If trainer_id provided, verifies the session belongs to that trainer.
    Performs Neo4j cleanup (best-effort) similar to other session delete endpoints.
    """
    sess = db.query(TrainingSessionDB).filter(TrainingSessionDB.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Users can only delete their own sessions unless they're admin
    if current_user.role != "admin":
        if sess.client_id != current_user.id and sess.trainer_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own sessions")

    if client_id is not None and sess.client_id != client_id:
        raise HTTPException(status_code=403, detail="Session does not belong to the specified client")
    if trainer_id is not None and sess.trainer_id != trainer_id:
        raise HTTPException(status_code=403, detail="Session does not belong to the specified trainer")

    # delete the session
    db.delete(sess)
    db.commit()

    # best-effort: clean up Neo4j scheduling relationships
    try:
        with neo4j_driver.session() as session:
            if sess.trainer_id:
                session.run(
                    "MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED]->(t:Trainer {mysql_id: $tid}) DELETE r",
                    cid=sess.client_id, tid=sess.trainer_id
                )
            else:
                if sess.service_id:
                    svc_obj = db.query(ServiceDB).filter(ServiceDB.id == sess.service_id).first()
                    if svc_obj:
                        session.run(
                            "MATCH (c:Client {mysql_id: $cid})-[r:SCHEDULED_UNASSIGNED]->(s:Service {name: $sname}) DELETE r",
                            cid=sess.client_id, sname=svc_obj.name
                        )
    except Exception:
        pass

    return {"status": "deleted", "session_id": session_id}

@app.get("/users/{user_id}/dashboard")
def get_user_dashboard(user_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return dashboard info for a user: upcoming sessions, completed sessions,
    subscriptions, and latest medical document (if any).

    Notes:
    - 'Upcoming' means scheduled_at >= now (UTC).
    - 'Completed' means scheduled_at < now.
    - Medical docs are looked up in CouchDB by matching client_email.
    """
    user = db.query(ClientDB).filter(ClientDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only view their own dashboard unless they're admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own dashboard")

    now = datetime.utcnow()

    # Sessions where user is the client
    sessions = db.query(TrainingSessionDB).filter(TrainingSessionDB.client_id == user_id).all()
    upcoming = []
    completed = []
    for s in sessions:
        trainer = db.query(ClientDB).filter(ClientDB.id == s.trainer_id).first()
        service = None
        if s.service_id:
            service = db.query(ServiceDB).filter(ServiceDB.id == s.service_id).first()

        entry = {
            "id": s.id,
            "trainer_id": s.trainer_id,
            "trainer_name": trainer.full_name if trainer else None,
            "trainer_email": trainer.email if trainer else None,
            "service_name": service.name if service else None,
            "scheduled_at": s.scheduled_at,
            "notes": s.notes
        }

        if s.scheduled_at and s.scheduled_at >= now:
            upcoming.append(entry)
        else:
            completed.append(entry)

    # Subscriptions for this user
    subs = db.query(SubscriptionDB).filter(SubscriptionDB.client_id == user_id).all()
    subscriptions = []
    for sub in subs:
        svc = db.query(ServiceDB).filter(ServiceDB.id == sub.service_id).first()
        subscriptions.append({
            "id": sub.id,
            "service_name": svc.name if svc else None,
            "plan_type": sub.plan_type,
            "created_at": sub.created_at,
            "medical_doc_id": sub.medical_doc_id
        })

    # Latest medical document for this user (by timestamp) from CouchDB, if available
    medical_doc = None
    if db_couch:
        try:
            latest_ts = None
            latest_doc = None
            for doc_id in db_couch:
                try:
                    doc = db_couch[doc_id]
                except Exception:
                    continue
                if doc.get("type") == "medical_certificate" and doc.get("client_email") == user.email:
                    ts = doc.get("timestamp")
                    try:
                        t = datetime.fromisoformat(ts) if ts else None
                    except Exception:
                        t = None
                    if not latest_ts or (t and latest_ts and t > latest_ts) or (t and not latest_ts):
                        latest_ts = t
                        latest_doc = doc
            if latest_doc:
                medical_doc = latest_doc
        except Exception:
            medical_doc = None

    return {
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role},
        "upcoming_sessions": upcoming,
        "completed_sessions": completed,
        "subscriptions": subscriptions,
        "latest_medical_doc": medical_doc
    }


@app.post("/products/", response_model=dict)
def add_product(product: ProductCreate, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Add a product to the shop and invalidate the products cache."""
    # prevent duplicate product names
    exists = db.query(ProductDB).filter(ProductDB.name == product.name).first()
    if exists:
        raise HTTPException(status_code=409, detail="Product with this name already exists")

    p = ProductDB(
        name=product.name,
        price=product.price,
        stock=product.stock,
        description=product.description,
        available=product.available if product.available is not None else True
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    # invalidate products cache
    try:
        redis_client.delete("all_products")
    except Exception:
        pass

    return {"status": "created", "id": p.id, "name": p.name}


@app.get("/products/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    """Return products available for everyone (available == True)."""
    # try Redis first (cache-aside)
    try:
        cached = redis_client.get("all_products")
        if cached:
            print("DEBUG: Returning products from Redis")
            return json.loads(cached)
    except Exception:
        # if Redis is down or errors, fall back to DB
        pass

    prods = db.query(ProductDB).filter(ProductDB.available == True).all()
    result = [
        {"id": p.id, "name": p.name, "price": p.price, "stock": p.stock, "description": p.description, "available": p.available}
        for p in prods
    ]

    # populate cache (best-effort)
    try:
        redis_client.setex("all_products", 60, json.dumps(result))
    except Exception:
        pass

    return result


@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: int, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Delete a product by ID and invalidate the products cache."""
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_name = product.name
    db.delete(product)
    db.commit()

    # invalidate products cache
    try:
        redis_client.delete("all_products")
    except Exception:
        pass

    return {"status": "deleted", "id": product_id, "name": product_name}


@app.put("/products/{product_id}", response_model=dict)
def update_product(product_id: int, data: ProductUpdate, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Update product by ID (all fields optional) and invalidate the products cache."""
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # prevent name collisions if changing name
    if data.name:
        exists = db.query(ProductDB).filter(ProductDB.name == data.name, ProductDB.id != product_id).first()
        if exists:
            raise HTTPException(status_code=409, detail="Product with this name already exists")
        product.name = data.name

    if data.price is not None:
        product.price = data.price

    if data.stock is not None:
        product.stock = data.stock

    if data.description is not None:
        product.description = data.description

    if data.available is not None:
        product.available = data.available

    db.commit()
    db.refresh(product)

    # invalidate products cache
    try:
        redis_client.delete("all_products")
    except Exception:
        pass

    return {"status": "updated", "id": product.id, "name": product.name, "price": product.price, "stock": product.stock}


@app.get("/services/")
def get_services(db: Session = Depends(get_db)):
    """Отримання списку послуг. Спочатку дивимось Redis, потім MySQL."""
    
    cached_services = redis_client.get("all_services")
    if cached_services:
        print("DEBUG: Returning from Redis")
        return json.loads(cached_services)

    print("DEBUG: Returning from MySQL")
    services = db.query(ServiceDB).all()
    result = [{"id": s.id, "name": s.name, "requires_medical": s.requires_medical} for s in services]

    redis_client.setex("all_services", 60, json.dumps(result))
    
    return result



@app.post("/services/", response_model=dict)
def create_service(item: dict = Body(...), current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """
    Create a new Service.
    Body example: {"name": "Pilates", "requires_medical": false}
    """
    name = item.get("name")
    requires_medical = bool(item.get("requires_medical", False))
    if not name:
        raise HTTPException(status_code=400, detail="Service name required")

    exists = db.query(ServiceDB).filter(ServiceDB.name == name).first()
    if exists:
        raise HTTPException(status_code=409, detail="Service already exists")

    svc = ServiceDB(name=name, requires_medical=requires_medical)
    db.add(svc)
    db.commit()
    db.refresh(svc)

    # create Neo4j node
    try:
        with neo4j_driver.session() as session:
            session.run("MERGE (s:Service {name: $name}) SET s.requires_medical = $med", name=name, med=requires_medical)
    except Exception:
        pass

    # invalidate Redis cache
    try:
        redis_client.delete("all_services")
    except Exception:
        pass

    return {"status": "created", "id": svc.id, "name": svc.name}


@app.delete("/services/{service_id}", response_model=dict)
def delete_service(service_id: int, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Delete a service if no subscriptions or sessions reference it.

    Checks:
    - service must exist
    - there must be zero subscriptions and zero training sessions referencing the service
    """
    svc = db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")

    # check references
    sub_count = db.query(SubscriptionDB).filter(SubscriptionDB.service_id == service_id).count()
    sess_count = db.query(TrainingSessionDB).filter(TrainingSessionDB.service_id == service_id).count()
    if sub_count > 0 or sess_count > 0:
        raise HTTPException(status_code=400, detail=f"Service cannot be deleted: {sub_count} subscriptions, {sess_count} sessions reference it")

    svc_name = svc.name
    db.delete(svc)
    db.commit()

    # remove Neo4j node (best-effort)
    try:
        with neo4j_driver.session() as session:
            session.run("MATCH (s:Service {name: $name}) DETACH DELETE s", name=svc_name)
    except Exception:
        pass

    # invalidate Redis cache
    try:
        redis_client.delete("all_services")
    except Exception:
        pass

    return {"status": "deleted", "id": service_id, "name": svc_name}


@app.put("/services/{service_id}", response_model=dict)
def update_service(service_id: int, data: ServiceUpdate, current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """Update service by ID (name and/or requires_medical).
    
    Validates:
    - service exists
    - if changing name, new name must be unique
    
    Updates Neo4j Service node properties (best-effort).
    """
    svc = db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")

    old_name = svc.name

    # Update name if provided
    if data.name is not None:
        # prevent name collisions
        existing = db.query(ServiceDB).filter(ServiceDB.name == data.name, ServiceDB.id != service_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Service with this name already exists")
        svc.name = data.name

    # Update requires_medical if provided
    if data.requires_medical is not None:
        svc.requires_medical = data.requires_medical

    db.commit()
    db.refresh(svc)

    # Update Neo4j node properties (best-effort)
    try:
        with neo4j_driver.session() as session:
            # If name changed, update the node
            if svc.name != old_name:
                session.run(
                    "MATCH (s:Service {name: $old_name}) SET s.name = $new_name, s.requires_medical = $med",
                    old_name=old_name, new_name=svc.name, med=svc.requires_medical
                )
            else:
                session.run(
                    "MATCH (s:Service {name: $name}) SET s.requires_medical = $med",
                    name=svc.name, med=svc.requires_medical
                )
    except Exception:
        pass

    # invalidate Redis cache
    try:
        redis_client.delete("all_services")
    except Exception:
        pass

    return {"status": "updated", "id": service_id, "name": svc.name, "requires_medical": svc.requires_medical}


@app.post("/medical-checkup/")
def submit_medical_doc(doc: MedicalDocInput, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Приймає результати обстеження від клініки.
    Зберігає неструктурований документ в CouchDB.
    Clients can only submit their own medical documents, admins can submit for any client.
    """
    if not db_couch:
        raise HTTPException(status_code=500, detail="CouchDB not connected")
    
    # Clients can only submit medical docs for themselves unless they're admin
    if current_user.role != "admin" and current_user.email != doc.client_email:
        raise HTTPException(status_code=403, detail="You can only submit medical documents for yourself")
    
    # Verify the client email exists in the database
    client = get_user_by_email(db, doc.client_email)
    if not client:
        raise HTTPException(status_code=404, detail="Client with this email not found")
    
    document = {
        "type": "medical_certificate",
        "client_email": doc.client_email,
        "doctor": doc.doctor_name,
        "status": doc.result,
        "timestamp": datetime.utcnow().isoformat(),
        "clinical_data": doc.details 
    }
    
    doc_id, doc_rev = db_couch.save(document)
    
    return {
        "status": "received", 
        "couchdb_id": doc_id, 
        "message": "Certificate stored. Use this ID for pool subscription."
    }


@app.post("/cancel-subscription/")
def cancel_subscription(cancel_data: SubscriptionCancel, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Скасування підписки на послугу.
    Видаляє запис з MySQL і видаляє зв'язок з Neo4j.
    """
    
    client = db.query(ClientDB).filter(ClientDB.id == cancel_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Clients can only cancel their own subscriptions unless they're admin
    if current_user.role != "admin" and current_user.id != cancel_data.client_id:
        raise HTTPException(status_code=403, detail="You can only cancel your own subscriptions")
    
    service = db.query(ServiceDB).filter(ServiceDB.name == cancel_data.service_name).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Find and delete subscription
    sub = db.query(SubscriptionDB).filter(
        SubscriptionDB.client_id == cancel_data.client_id,
        SubscriptionDB.service_id == service.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found for this client and service")

    db.delete(sub)
    db.commit()

    # Remove Neo4j relationship (best-effort)
    try:
        query = """
        MATCH (c:Client {mysql_id: $cid})-[r:USES]->(s:Service {name: $sname})
        DELETE r
        """
        with neo4j_driver.session() as session:
            session.run(query, cid=cancel_data.client_id, sname=cancel_data.service_name)
    except Exception:
        pass

    return {"status": "cancelled", "subscription_id": sub.id, "client_id": cancel_data.client_id, "service_name": cancel_data.service_name}


@app.post("/subscriptions/", response_model=dict)
def create_subscription(sub_data: SubscriptionCreate, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new subscription (alias for /subscribe/ endpoint).
    
    Validates:
    - client exists
    - service exists by name
    - if service requires medical doc, medical_doc_id is provided
    
    Creates Neo4j USES relationship and sets plan properties.
    """
    client = db.query(ClientDB).filter(ClientDB.id == sub_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Clients can only create subscriptions for themselves unless they're admin
    if current_user.role != "admin" and current_user.id != sub_data.client_id:
        raise HTTPException(status_code=403, detail="You can only create subscriptions for yourself")
    
    service = db.query(ServiceDB).filter(ServiceDB.name == sub_data.service_name).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.requires_medical:
        if not sub_data.medical_doc_id:
            raise HTTPException(status_code=400, detail=f"Service '{service.name}' requires a medical certificate ID")

    # check if subscription already exists
    existing_sub = db.query(SubscriptionDB).filter(
        SubscriptionDB.client_id == sub_data.client_id,
        SubscriptionDB.service_id == service.id
    ).first()
    if existing_sub:
        raise HTTPException(status_code=409, detail="Subscription already exists for this client and service")

    new_sub = SubscriptionDB(
        client_id=sub_data.client_id,
        service_id=service.id,
        plan_type=sub_data.plan_type,
        medical_doc_id=sub_data.medical_doc_id
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    # Create Neo4j relationship (best-effort)
    try:
        with neo4j_driver.session() as session:
            session.run(
                "MATCH (c:Client {mysql_id: $cid}) MATCH (s:Service {name: $sname}) "
                "MERGE (c)-[r:USES]->(s) SET r.last_visit = datetime(), r.plan = $plan",
                cid=client.id, sname=service.name, plan=sub_data.plan_type
            )
    except Exception:
        pass

    return {"status": "created", "subscription_id": new_sub.id, "client_id": client.id, "service_name": service.name}


@app.delete("/subscriptions/{subscription_id}", response_model=dict)
def delete_subscription(subscription_id: int, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a subscription by ID.
    
    Also removes the Neo4j USES relationship (best-effort).
    """
    sub = db.query(SubscriptionDB).filter(SubscriptionDB.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Users can only delete their own subscriptions unless they're admin
    if current_user.role != "admin" and current_user.id != sub.client_id:
        raise HTTPException(status_code=403, detail="You can only delete your own subscriptions")

    # Get client and service info for Neo4j cleanup
    client = db.query(ClientDB).filter(ClientDB.id == sub.client_id).first()
    service = db.query(ServiceDB).filter(ServiceDB.id == sub.service_id).first()

    db.delete(sub)
    db.commit()

    # Remove Neo4j relationship (best-effort)
    if client and service:
        try:
            with neo4j_driver.session() as session:
                session.run(
                    "MATCH (c:Client {mysql_id: $cid})-[r:USES]->(s:Service {name: $sname}) DELETE r",
                    cid=client.id, sname=service.name
                )
        except Exception:
            pass

    return {"status": "deleted", "subscription_id": subscription_id}


@app.put("/subscriptions/{subscription_id}", response_model=dict)
def update_subscription(subscription_id: int, data: SubscriptionUpdate, current_user: ClientDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update subscription by ID (plan_type and/or medical_doc_id).
    
    Validates:
    - subscription exists
    - if service requires medical doc, medical_doc_id must be provided
    
    Updates Neo4j USES relationship properties (best-effort).
    """
    sub = db.query(SubscriptionDB).filter(SubscriptionDB.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Users can only update their own subscriptions unless they're admin
    if current_user.role != "admin" and current_user.id != sub.client_id:
        raise HTTPException(status_code=403, detail="You can only update your own subscriptions")

    # Get service to check if it requires medical doc
    service = db.query(ServiceDB).filter(ServiceDB.id == sub.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Update plan_type if provided
    if data.plan_type is not None:
        sub.plan_type = data.plan_type

    # Update medical_doc_id if provided
    if data.medical_doc_id is not None:
        sub.medical_doc_id = data.medical_doc_id

    # If service requires medical doc, ensure medical_doc_id is set
    if service.requires_medical and not sub.medical_doc_id:
        raise HTTPException(status_code=400, detail=f"Service '{service.name}' requires a medical certificate ID")

    db.commit()
    db.refresh(sub)

    # Update Neo4j relationship properties (best-effort)
    client = db.query(ClientDB).filter(ClientDB.id == sub.client_id).first()
    if client:
        try:
            with neo4j_driver.session() as session:
                session.run(
                    "MATCH (c:Client {mysql_id: $cid})-[r:USES]->(s:Service {name: $sname}) "
                    "SET r.plan = $plan, r.last_updated = datetime()",
                    cid=client.id, sname=service.name, plan=sub.plan_type
                )
        except Exception:
            pass

    return {"status": "updated", "subscription_id": subscription_id, "plan_type": sub.plan_type, "medical_doc_id": sub.medical_doc_id}


@app.get("/analytics/popular-services")
def get_popular_services(current_user: ClientDB = Depends(require_role(["admin"]))):
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


@app.get("/analytics/popular-trainers")
def get_popular_trainers(current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """
    Returns most popular trainers by number of scheduled sessions.
    Primary source: Neo4j (counts SCHEDULED relationships).
    Fallback: MySQL (counts TrainingSessionDB entries grouped by trainer_id).
    """
    # Try Neo4j first (best-effort)
    try:
        query = """
        MATCH (c:Client)-[:SCHEDULED]->(t:Trainer)
        RETURN t.name AS Trainer, count(c) AS Sessions
        ORDER BY Sessions DESC
        LIMIT 10
        """
        results = []
        with neo4j_driver.session() as session:
            data = session.run(query)
            for record in data:
                results.append({"trainer": record["Trainer"], "sessions_count": record["Sessions"]})

        if results:
            return {"report_type": "Popular Trainers by Scheduled Sessions (Neo4j)", "data": results}
    except Exception:
        # Neo4j may be down — fall through to SQL fallback
        pass

    # Fallback to SQL: count training_sessions by trainer_id
    results = []
    rows = (
        db.query(TrainingSessionDB.trainer_id, func.count(TrainingSessionDB.id).label("sessions_count"))
        .filter(TrainingSessionDB.trainer_id != None)
        .group_by(TrainingSessionDB.trainer_id)
        .order_by(func.count(TrainingSessionDB.id).desc())
        .limit(10)
        .all()
    )
    for trainer_id, sessions_count in rows:
        trainer = db.query(ClientDB).filter(ClientDB.id == trainer_id).first()
        results.append({"trainer": trainer.full_name if trainer else f"id:{trainer_id}", "sessions_count": sessions_count})

    return {"report_type": "Popular Trainers by Scheduled Sessions (SQL)", "data": results}


@app.get("/analytics/popular-subscriptions")
def get_subscription_stats(current_user: ClientDB = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    """
    Returns subscription counts grouped by service and plan_type.
    Uses MySQL (SubscriptionDB joined with ServiceDB).
    """
    rows = (
        db.query(ServiceDB.name.label("service_name"), SubscriptionDB.plan_type, func.count(SubscriptionDB.id).label("sub_count"))
        .join(ServiceDB, ServiceDB.id == SubscriptionDB.service_id)
        .group_by(ServiceDB.name, SubscriptionDB.plan_type)
        .order_by(func.count(SubscriptionDB.id).desc())
        .all()
    )

    results = []
    for service_name, plan_type, sub_count in rows:
        results.append({"service": service_name, "plan_type": plan_type, "subscriptions_count": sub_count})

    return {"report_type": "Subscriptions by Service and Plan", "data": results}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)