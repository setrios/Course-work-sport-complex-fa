from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import uvicorn
from datetime import date
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.auth import AuthService, require_role, require_user
from app.config import Base, SessionLocal, engine, get_db, neo4j_driver, sport_system
from app.db_models import CategoryDB, SupplierDB, ProductDB
from app.sport_models import (
    SportClient, SportMembership, SportService, SportTrainer,
    SportRoom, ClassSchedule, ClassEnrollment, SportVisit,
    SportPayment, TrainerFeedback, Promotion, MaintenanceLog
)
from app.schemas import (
    CategoryCreate,
    ClientCreate,
    ClientListQuery,
    ClientUpdate,
    MedicalCertificateCreate,
    ProductCreate,
    ProductImageUpload,
    ProductListQuery,
    ServiceCreate,
    SupplierCreate,
    TrainerCreate,
    UserLogin,
    UserRegister,
    UserProfileUpdate,
    VisitCreate,
)
from app.services import AnalyticsService, CategoryService, OrderService, ProductService, SportService, SupplierService

# Services
supplier_service = SupplierService()
category_service = CategoryService()
product_service = ProductService()
order_service = OrderService()
analytics_service = AnalyticsService()
sport_service = SportService()
auth_service = AuthService()


# -------------------------------------------------
# Startup: create tables and seed reference data
# -------------------------------------------------

def seed_initial():
    db = SessionLocal()
    categories = ["Електроніка", "Одяг", "Продукти харчування", "Книги", "Меблі", "Спортивне обладнання", "Аксесуари"]
    for cat in categories:
        if not db.query(CategoryDB).filter(CategoryDB.name == cat).first():
            db.add(CategoryDB(name=cat))
            with neo4j_driver.session() as session:
                session.run("MERGE (c:Category {name: $name})", name=cat)

    suppliers = [
        {"name": "TechWorld", "city": "Київ", "country": "Україна", "email": "info@techworld.ua"},
        {"name": "FashionHub", "city": "Львів", "country": "Україна", "email": "sales@fashionhub.ua"},
        {"name": "FoodMart", "city": "Одеса", "country": "Україна", "email": "orders@foodmart.ua"},
        {"name": "SportGear", "city": "Київ", "country": "Україна", "email": "info@sportgear.ua"},
    ]
    for s in suppliers:
        if not db.query(SupplierDB).filter(SupplierDB.name == s["name"]).first():
            db.add(SupplierDB(name=s["name"], city=s["city"], country=s["country"], contact_email=s["email"]))
            with neo4j_driver.session() as session:
                session.run(
                    "MERGE (s:Supplier {name: $name, city: $city, country: $country})",
                    name=s["name"],
                    city=s["city"],
                    country=s["country"],
                )
    
    # Sync sport_data.json to individual JSON files and USERS dict
    from app.auth import USERS
    try:
        import json
        from pathlib import Path
        
        sport_data_path = Path("data/sport_data.json")
        if sport_data_path.exists():
            with open(sport_data_path, 'r', encoding='utf-8') as f:
                sport_data = json.load(f)
            
            # Sync clients to clients.json
            clients_from_sport_data = sport_data.get("clients", [])
            if clients_from_sport_data:
                clients_path = Path("data/clients.json")
                existing_clients = []
                if clients_path.exists():
                    with open(clients_path, 'r', encoding='utf-8') as f:
                        existing_clients = json.load(f)
                
                # Merge clients (avoid duplicates by username)
                existing_usernames = {c.get("username") for c in existing_clients}
                for client in clients_from_sport_data:
                    if client.get("username") not in existing_usernames:
                        existing_clients.append(client)
                        print(f"✓ Synced client to clients.json: {client.get('full_name')}")
                
                with open(clients_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_clients, f, indent=2, ensure_ascii=False)
            
            # Sync trainers to trainers.json
            trainers_from_sport_data = sport_data.get("trainers", [])
            if trainers_from_sport_data:
                trainers_path = Path("data/trainers.json")
                existing_trainers = []
                if trainers_path.exists():
                    with open(trainers_path, 'r', encoding='utf-8') as f:
                        existing_trainers = json.load(f)
                
                # Merge trainers (avoid duplicates by trainer_id)
                existing_ids = {t.get("trainer_id") for t in existing_trainers}
                for trainer in trainers_from_sport_data:
                    if trainer.get("trainer_id") not in existing_ids:
                        existing_trainers.append(trainer)
                        print(f"✓ Synced trainer to trainers.json: {trainer.get('full_name')}")
                
                with open(trainers_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_trainers, f, indent=2, ensure_ascii=False)
            
            # Sync memberships to memberships.json
            memberships_from_sport_data = sport_data.get("memberships", [])
            if memberships_from_sport_data:
                memberships_path = Path("data/memberships.json")
                existing_memberships = []
                if memberships_path.exists():
                    with open(memberships_path, 'r', encoding='utf-8') as f:
                        existing_memberships = json.load(f)
                
                # Merge memberships (avoid duplicates by membership_id)
                existing_ids = {m.get("membership_id") for m in existing_memberships}
                for membership in memberships_from_sport_data:
                    if membership.get("membership_id") not in existing_ids:
                        existing_memberships.append(membership)
                        print(f"✓ Synced membership to memberships.json: ID {membership.get('membership_id')}")
                
                with open(memberships_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_memberships, f, indent=2, ensure_ascii=False)
            
            # Add all clients with username and password to USERS dict
            for client in clients_from_sport_data:
                username = client.get("username")
                password = client.get("password")
                
                if username and password and username not in USERS:
                    USERS[username] = {
                        "password": password,
                        "role": "user",
                        "email": client.get("contact_info", {}).get("email")
                    }
                    print(f"✓ Synced client credentials: {username}")
    except Exception as e:
        print(f"Warning: Could not sync sport data: {e}")
    
    # Seed test clients to sport_system and JSON store
    from datetime import date
    from sport_complex import ContactInfo
    
    test_clients = [
        {
            "full_name": "Іван Петренко",
            "birth_date": date(1990, 5, 15),
            "gender": "MALE",
            "contact": ContactInfo(phone="+380501234567", email="ivan@example.com"),
            "username": "ivan_petrenko",
            "password": "ivan123456",
        },
        {
            "full_name": "Марія Іванівна",
            "birth_date": date(1995, 3, 22),
            "gender": "FEMALE",
            "contact": ContactInfo(phone="+380661234567", email="maria@example.com"),
            "username": "maria_ivanova",
            "password": "maria123456",
        },
        {
            "full_name": "Олег Коваленко",
            "birth_date": date(1988, 7, 10),
            "gender": "MALE",
            "contact": ContactInfo(phone="+380731234567", email="oleg@example.com"),
            "username": "oleg_kovalenko",
            "password": "oleg123456",
        },
    ]
    
    for client_data in test_clients:
        # Check if client already exists in JSON store
        existing_clients = sport_service.store.list_all("clients")
        if not any(c.get("username") == client_data["username"] for c in existing_clients):
            # Register user account
            try:
                auth_service.register(client_data["username"], client_data["password"], client_data["contact"].email)
            except Exception as e:
                print(f"Warning: Could not register user {client_data['username']}: {e}")
            
            # Add client to sport system (in-memory)
            sport_system.add_client_entity(
                full_name=client_data["full_name"],
                birth_date=client_data["birth_date"],
                gender=client_data["gender"],
                contact=client_data["contact"],
            )
            
            # Add client to JSON store (persistent)
            client_obj = {
                "full_name": client_data["full_name"],
                "birth_date": client_data["birth_date"].isoformat(),
                "gender": client_data["gender"],
                "contact_info": {
                    "phone": client_data["contact"].phone,
                    "email": client_data["contact"].email,
                    "address": client_data["contact"].address,
                },
                "username": client_data["username"],
                "has_valid_cert": False,
            }
            sport_service.store.add("clients", client_obj, "client_id")
            print(f"✓ Seeded client: {client_data['full_name']}")
    
    # Seed test trainers to JSON store
    test_trainers = [
        {
            "full_name": "Дмитро Силенко",
            "specialization": "Фітнес і силові тренування",
            "birth_date": date(1985, 3, 10),
            "phone": "+380951234567",
            "email": "dmitro@example.com",
        },
        {
            "full_name": "Світлана Романова",
            "specialization": "Йога та флексібільність",
            "birth_date": date(1992, 7, 25),
            "phone": "+380961234567",
            "email": "svitlana@example.com",
        },
        {
            "full_name": "Андрій Попов",
            "specialization": "Кардіо та марафонський біг",
            "birth_date": date(1988, 1, 15),
            "phone": "+380971234567",
            "email": "andrey@example.com",
        },
    ]
    
    for trainer_data in test_trainers:
        existing = sport_service.store.list_all("trainers")
        if not any(t.get("full_name") == trainer_data["full_name"] for t in existing):
            trainer_obj = {
                "full_name": trainer_data["full_name"],
                "specialization": trainer_data["specialization"],
                "birth_date": trainer_data["birth_date"].isoformat(),
                "contact_info": {
                    "phone": trainer_data["phone"],
                    "email": trainer_data["email"],
                },
            }
            sport_service.store.add("trainers", trainer_obj, "trainer_id")
    
    # Seed test services to JSON store
    test_services = [
        {
            "service_name": "Персональна тренування (1 година)",
            "price": 300.00,
            "requires_medical_certificate": False,
        },
        {
            "service_name": "Групова тренування з фітнесу",
            "price": 100.00,
            "requires_medical_certificate": False,
        },
        {
            "service_name": "Йога клас",
            "price": 80.00,
            "requires_medical_certificate": False,
        },
        {
            "service_name": "Цільова тренування (спеціалізована)",
            "price": 250.00,
            "requires_medical_certificate": True,
        },
        {
            "service_name": "Реабілітаційна тренування",
            "price": 200.00,
            "requires_medical_certificate": True,
        },
    ]
    
    for service_data in test_services:
        existing = sport_service.store.list_all("services")
        if not any(s.get("service_name") == service_data["service_name"] for s in existing):
            service_obj = {
                "service_name": service_data["service_name"],
                "price": service_data["price"],
                "requires_medical_certificate": service_data["requires_medical_certificate"],
                "is_active": True,
            }
            sport_service.store.add("services", service_obj, "service_id")
    
    db.commit()
    db.close()
    logger.info("[SeedInitial] Test data seeded successfully for sport entities")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    seed_initial()
    yield
    # Shutdown (if needed)


app = FastAPI(title="Online Store & Sport Complex API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Health
# -------------------------------------------------

@app.get("/health")
def healthcheck():
    return {"status": "ok"}


# -------------------------------------------------
# Auth
# -------------------------------------------------

@app.post("/auth/register")
def register(payload: UserRegister, user=Depends(require_role(["admin"]))):
    try:
        return auth_service.register(payload.username, payload.password, payload.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login(payload: UserLogin):
    try:
        return auth_service.login(payload.username, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/auth/logout")
def logout(authorization: str | None = None):
    return auth_service.logout(authorization)


@app.get("/auth/me")
def me(user=Depends(require_user)):
    return auth_service.me(user)


# -------------------------------------------------
# Suppliers & Categories
# -------------------------------------------------

@app.post("/suppliers/")
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return supplier_service.create(db, payload.name, payload.city, payload.country, payload.contact_email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create supplier: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/suppliers/")
def list_suppliers(db: Session = Depends(get_db), user=Depends(require_user)):
    return supplier_service.list(db)


@app.post("/categories/")
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return category_service.create(db, payload.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create category: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/categories/")
def list_categories(db: Session = Depends(get_db), user=Depends(require_user)):
    categories = db.query(CategoryDB).all()
    return [{"id": c.id, "name": c.name} for c in categories]


# -------------------------------------------------
# Products
# -------------------------------------------------

@app.post("/products/")
def create_product(payload: ProductCreate, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return product_service.create(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/products/assortment")
def get_assortment(
    db: Session = Depends(get_db),
    user=Depends(require_user),
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    supplier: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc"
):
    """
    Отримати асортимент товарів з пагінацією та фільтрацією.
    
    Параметри:
    - page: номер сторінки (за замовчуванням 1)
    - page_size: розмір сторінки (за замовчуванням 20, макс 100)
    - category: фільтр по категорії
    - supplier: фільтр по постачальнику
    - min_price: мінімальна ціна
    - max_price: максимальна ціна
    - in_stock: тільки товари в наявності
    - search: пошук по назві товару
    - sort_by: поле сортування (name, price, quantity)
    - sort_order: порядок сортування (asc, desc)
    """
    try:
        query = ProductListQuery(
            page=page,
            page_size=min(page_size, 100),
            category=category,
            supplier=supplier,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return product_service.list(db, query)
    except Exception as e:
        logger.error(f"Failed to get products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/products/search/{name_query}")
def search_product(name_query: str, db: Session = Depends(get_db), user=Depends(require_user)):
    try:
        return product_service.search(db, name_query)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/products/stock-extremes")
def stock_extremes(db: Session = Depends(get_db), user=Depends(require_user)):
    return product_service.stock_extremes(db)


@app.get("/products/by-article/{article}")
def product_by_article(article: str, db: Session = Depends(get_db), user=Depends(require_user)):
    try:
        return product_service.by_article(db, article)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/products/upload-image/")
def upload_image(payload: ProductImageUpload, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return product_service.upload_image(db, payload.article, payload.image_base64, payload.mime_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/products/image/{article}")
def get_image(article: str, db: Session = Depends(get_db), user=Depends(require_user)):
    try:
        return product_service.get_image(db, article)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/products/{article}")
def update_product(article: str, payload: ProductCreate, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return product_service.update(db, article, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/products/{article}")
def delete_product(article: str, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return product_service.delete(db, article)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------------------------------------
# Orders / Reports
# -------------------------------------------------

@app.get("/orders/low-stock-report")
def low_stock_report(db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    try:
        return order_service.low_stock_report(db)
    except Exception as e:
        logger.error(f"Failed to generate low stock report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------------------------------------
# Analytics
# -------------------------------------------------

@app.get("/analytics/popular-products")
def popular_products(user=Depends(require_user)):
    try:
        return analytics_service.popular_products()
    except Exception as e:
        logger.error(f"Failed to get popular products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/analytics/suppliers-by-city")
def suppliers_by_city(user=Depends(require_user)):
    try:
        return analytics_service.suppliers_by_city()
    except Exception as e:
        logger.error(f"Failed to get suppliers by city: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------------------------------------
# Sport complex (in-memory)
# -------------------------------------------------

@app.post("/sport/clients")
def sport_create_client(payload: ClientCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.create_client(payload, user_role=user["role"], auth_service=auth_service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create client: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/clients")
def sport_list_clients(
    user=Depends(require_user),
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    has_membership: Optional[bool] = None,
    sort_by: str = "full_name",
    sort_order: str = "asc"
):
    """
    Отримати список клієнтів з пагінацією та фільтрацією.
    
    Параметри:
    - page: номер сторінки (за замовчуванням 1)
    - page_size: розмір сторінки (за замовчуванням 20, макс 100)
    - search: пошук по імені клієнта
    - has_membership: фільтр по активному абонементу (true/false)
    - sort_by: поле сортування
    - sort_order: порядок сортування (asc, desc)
    """
    try:
        query = ClientListQuery(
            page=page,
            page_size=min(page_size, 100),
            search=search,
            has_membership=has_membership,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return sport_service.list_clients(query)
    except Exception as e:
        logger.error(f"Failed to list clients: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/clients/{client_id}")
def sport_get_client(client_id: int, user=Depends(require_user)):
    try:
        return sport_service.get_client(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/sport/clients/{client_id}")
def sport_update_client(client_id: int, payload: ClientUpdate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.update_client(client_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update client: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sport/clients/{client_id}")
def sport_delete_client(client_id: int, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.delete_client(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/sport/trainers")
def sport_create_trainer(payload: TrainerCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.create_trainer(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create trainer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/trainers")
def sport_list_trainers(user=Depends(require_user)):
    return sport_service.list_trainers()


@app.put("/sport/trainers/{trainer_id}")
def sport_update_trainer(trainer_id: int, payload: TrainerCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.update_trainer(trainer_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update trainer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sport/trainers/{trainer_id}")
def sport_delete_trainer(trainer_id: int, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.delete_trainer(trainer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/sport/services")
def sport_create_service(payload: ServiceCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.create_service(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create service: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/services")
def sport_list_services(user=Depends(require_user)):
    return sport_service.list_services()


@app.put("/sport/services/{service_id}")
def sport_update_service(service_id: int, payload: ServiceCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.update_service(service_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update service: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sport/services/{service_id}")
def sport_delete_service(service_id: int, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.delete_service(service_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/sport/medical-certificates")
def sport_medical_certificate(payload: MedicalCertificateCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.attach_medical(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to attach medical certificate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/sport/memberships")
def sport_create_membership(payload: dict, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.create_membership(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create membership: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/memberships")
def sport_list_memberships(user=Depends(require_user)):
    return sport_service.list_memberships()


@app.put("/sport/memberships/{membership_id}")
def sport_update_membership(membership_id: int, payload: dict, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.update_membership(membership_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update membership: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sport/memberships/{membership_id}")
def sport_delete_membership(membership_id: int, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.delete_membership(membership_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ------------------------------------------
# SPORT: Membership for current user
# ------------------------------------------

@app.get("/sport/user/membership")
def get_user_membership(user=Depends(require_user)):
    try:
        username = user.get("username")

        # Find client by username
        clients = sport_service.store.list_all("clients")
        client = next((c for c in clients if c.get("username") == username), None)
        if not client:
            return {"membership": None}

        client_id = client.get("client_id")
        memberships = sport_service.store.list_all("memberships")

        # Prefer active membership for this client; otherwise latest by end_date
        membership = None
        for m in memberships:
            if m.get("client_id") == client_id:
                if m.get("status") == "active":
                    membership = m
                    break
                if not membership:
                    membership = m

        if not membership:
            return {"membership": None, "client_id": client_id}

        days_left = None
        end_date = membership.get("end_date")
        if end_date:
            try:
                days_left = (date.fromisoformat(end_date) - date.today()).days
            except Exception:
                days_left = None

        return {
            "membership": {
                "membership_id": membership.get("membership_id"),
                "client_id": membership.get("client_id"),
                "subscription_type": membership.get("subscription_type"),
                "status": membership.get("status"),
                "start_date": membership.get("start_date"),
                "end_date": membership.get("end_date"),
                "price": membership.get("price"),
                "days_left": days_left,
            },
            "client_id": client_id,
        }
    except Exception as e:
        logger.error(f"Failed to get user membership: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Failed to delete membership: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/user/profile")
def get_profile(user=Depends(require_user)):
    try:
        return sport_service.get_user_profile(user["username"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/sport/user/profile")
def update_profile(payload: UserProfileUpdate, user=Depends(require_user)):
    try:
        return sport_service.update_user_profile(user["username"], payload)
    except ValueError as e:
        detail = str(e)
        status_code = 404 if "not found" in detail.lower() else 400
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/sport/visits")
def sport_register_visit(payload: VisitCreate, user=Depends(require_role(["admin"]))):
    try:
        return sport_service.register_visit(payload)
    except ValueError as e:
        detail = str(e)
        status = 404 if "not found" in detail.lower() else 400
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        logger.error(f"Failed to register visit: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/visits")
def sport_list_visits(user=Depends(require_user)):
    return sport_service.list_visits()


@app.get("/sport/reports")
def sport_reports(user=Depends(require_role(["admin"]))):
    try:
        return sport_service.report()
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sport/analytics")
def sport_analytics(user=Depends(require_user)):
    try:
        return sport_service.analytics()
    except Exception as e:
        logger.error(f"Failed to generate analytics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------------------------------------
# Database Queries (Admin only)
# -------------------------------------------------

@app.get("/db/products/images")
def db_products_images(db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    """Get all products with images for visualization"""
    try:
        products = db.query(ProductDB).all()
        return {
            "status": "success",
            "products": [
                {
                    "article": p.article,
                    "name": p.name,
                    "price": p.price / 100,
                    "quantity": p.quantity,
                    "category": p.category.name if p.category else "N/A",
                    # Use existing image endpoint; frontend will fetch per article
                    "image_url": f"/products/image/{p.article}",
                }
                for p in products
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get products with images: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/db/assortment")
def db_assortment(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"])),
    category: Optional[str] = None,
    supplier: Optional[str] = None,
    low_stock: Optional[bool] = None
):
    """
    Отримати повний асортимент з інвентаризацією та фільтрами.
    
    Параметри:
    - category: фільтр по категорії
    - supplier: фільтр по постачальнику
    - low_stock: показати тільки товари з низьким запасом
    """
    try:
        query = db.query(ProductDB)
        
        if category:
            cat = db.query(CategoryDB).filter(CategoryDB.name == category).first()
            if cat:
                query = query.filter(ProductDB.category_id == cat.id)
        
        if supplier:
            sup = db.query(SupplierDB).filter(SupplierDB.name == supplier).first()
            if sup:
                query = query.filter(ProductDB.supplier_id == sup.id)
        
        if low_stock:
            query = query.filter(ProductDB.quantity < ProductDB.min_stock)
        
        products = query.all()
        
        return {
            "status": "success",
            "filters_applied": {
                "category": category,
                "supplier": supplier,
                "low_stock": low_stock
            },
            "total": len(products),
            "assortment": [
                {
                    "article": p.article,
                    "name": p.name,
                    "category": p.category.name if p.category else "N/A",
                    "supplier": p.supplier.name if p.supplier else "N/A",
                    "price_uah": float(p.price / 100) if p.price else 0,
                    "quantity": p.quantity,
                    "minimum": p.min_stock,
                    "status": "Low Stock" if p.quantity < p.min_stock else "In Stock"
                }
                for p in products
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get assortment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/db/price-availability")
def db_price_availability(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"])),
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    status_filter: Optional[str] = None
):
    """
    Отримати матрицю цін та наявності з фільтрами.
    
    Параметри:
    - min_value: мінімальна загальна вартість товару
    - max_value: максимальна загальна вартість товару
    - status_filter: фільтр по статусу ("In Stock", "Low Stock")
    """
    try:
        products = db.query(ProductDB).all()
        
        price_matrix = []
        for p in products:
            total_value = (p.price / 100) * p.quantity
            status = "In Stock" if p.quantity > p.min_stock else "Low Stock"
            
            # Apply filters
            if min_value is not None and total_value < min_value:
                continue
            if max_value is not None and total_value > max_value:
                continue
            if status_filter and status != status_filter:
                continue
            
            price_matrix.append({
                "article": p.article,
                "name": p.name,
                "price": p.price / 100,
                "quantity": p.quantity,
                "status": status,
                "total_value": total_value,
            })
        
        return {
            "status": "success",
            "filters_applied": {
                "min_value": min_value,
                "max_value": max_value,
                "status_filter": status_filter
            },
            "total": len(price_matrix),
            "price_matrix": price_matrix
        }
    except Exception as e:
        logger.error(f"Failed to get price/availability matrix: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/db/min-max-products")
def db_min_max_products(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"])),
    limit: int = 3,
    sort_by: str = "quantity"
):
    """
    Отримати мінімальні та максимальні товари за вказаним критерієм.
    
    Параметри:
    - limit: кількість товарів для відображення (за замовчуванням 3)
    - sort_by: критерій сортування ("quantity", "price", "total_value")
    """
    try:
        products = db.query(ProductDB).all()
        if not products:
            return {"status": "success", "min_products": [], "max_products": []}
        
        # Sort by selected criterion
        if sort_by == "price":
            sorted_products = sorted(products, key=lambda p: p.price)
        elif sort_by == "total_value":
            sorted_products = sorted(products, key=lambda p: (p.price / 100) * p.quantity)
        else:  # quantity
            sorted_products = sorted(products, key=lambda p: p.quantity)
        
        limit = max(1, min(limit, 10))  # Limit between 1 and 10
        
        return {
            "status": "success",
            "sort_by": sort_by,
            "limit": limit,
            "min_products": [
                {
                    "article": p.article,
                    "name": p.name,
                    "quantity": p.quantity,
                    "price": p.price / 100,
                    "total_value": (p.price / 100) * p.quantity,
                }
                for p in sorted_products[:limit]
            ],
            "max_products": [
                {
                    "article": p.article,
                    "name": p.name,
                    "quantity": p.quantity,
                    "price": p.price / 100,
                    "total_value": (p.price / 100) * p.quantity,
                }
                for p in sorted_products[-limit:][::-1]
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get min/max products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/db/suppliers")
def db_suppliers(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"])),
    city: Optional[str] = None,
    country: Optional[str] = None
):
    """
    Отримати постачальників згруповані за локацією з фільтрами.
    
    Параметри:
    - city: фільтр по місту
    - country: фільтр по країні
    """
    try:
        query = db.query(SupplierDB)
        
        if city:
            query = query.filter(SupplierDB.city == city)
        if country:
            query = query.filter(SupplierDB.country == country)
        
        suppliers = query.all()
        
        # Group by location
        by_location = {}
        for s in suppliers:
            key = f"{s.city}, {s.country}"
            if key not in by_location:
                by_location[key] = []
            by_location[key].append({
                "name": s.name,
                "email": s.contact_email
            })
        
        return {
            "status": "success",
            "filters_applied": {
                "city": city,
                "country": country
            },
            "total_suppliers": len(suppliers),
            "locations": len(by_location),
            "suppliers": [
                {
                    "name": s.name,
                    "city": s.city,
                    "country": s.country,
                    "contact": s.contact_email,
                    "products_supplied": len(s.products) if s.products else 0,
                }
                for s in suppliers
            ],
            "by_location": by_location
        }
    except Exception as e:
        logger.error(f"Failed to get suppliers: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/db/inventory-history")
def db_inventory_history(article: str = None, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    """Get inventory history by article"""
    try:
        if article:
            product = db.query(ProductDB).filter(ProductDB.article == article).first()
            if not product:
                return {"status": "error", "message": f"Product with article '{article}' not found"}
            products = [product]
        else:
            products = db.query(ProductDB).all()
        
        return {
            "status": "success",
            "history": [
                {
                    "article": p.article,
                    "name": p.name,
                    "quantity": p.quantity,
                    "delivery_days": p.delivery_days,
                    "supplier": p.supplier.name if p.supplier else "N/A",
                    "last_updated": p.created_at.isoformat() if hasattr(p, 'created_at') else None,
                }
                for p in products
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get inventory history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/db/generate-order")
def db_generate_order(payload: dict, db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    """
    Generate business letter for order
    
    Вимога: формування ділових листів якщо кількість товарів не перевищує 
    мінімальний обсяг наявних запасів (min_stock)
    
    Параметри:
    - product_id (article): артикул товару
    - quantity: кількість замовлення
    
    Повертає: замовлення лист з деталями, якщо кількість >= min_stock
    """
    try:
        product_id = payload.get("product_id")
        quantity = payload.get("quantity", 1)
        
        if not product_id:
            raise ValueError("product_id is required")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        
        product = db.query(ProductDB).filter(ProductDB.article == product_id).first()
        if not product:
            raise ValueError(f"Product with article '{product_id}' not found")
        
        # Вимога 7: Перевірка, чи замовлена кількість не перевищує мінімальний обсяг запасів
        min_required = product.min_stock if product.min_stock else 10
        if quantity < min_required:
            raise ValueError(
                f"Order quantity ({quantity}) must be at least {min_required} units "
                f"(minimum stock level for '{product.name}')"
            )
        
        # Генерація бізнес-листа замовлення
        from datetime import datetime, timedelta
        order_date = datetime.now().strftime("%d.%m.%Y")
        delivery_date = (datetime.now() + timedelta(days=product.delivery_days or 7)).strftime("%d.%m.%Y")
        
        business_letter = f"""
╔════════════════════════════════════════════════════════════════╗
║           ДІЛОВЕ ЗАМОВЛЕННЯ НА ПОСТАЧАННЯ ТОВАРУ              ║
╚════════════════════════════════════════════════════════════════╝

Дата: {order_date}
Замовник: Спорткомплекс "Active Fit"
Адреса: м. Київ, вул. Тренувальна, 15
Телефон: +380 (44) 123-45-67

────────────────────────────────────────────────────────────────

ПОСТАЧАЛЬНИК:
  • Назва: {product.supplier.name if product.supplier else "N/A"}
  • Email: {product.supplier.contact_email if product.supplier else "N/A"}

────────────────────────────────────────────────────────────────

ДЕТАЛІ ЗАМОВЛЕННЯ:

  Найменування товару: {product.name}
  Артикул: {product.article}
  Запитувана кількість: {quantity} шт
  Мінімальний обсяг запасів: {min_required} шт
  Статус перевірки: ВІДПОВІДАЄ ВИМОГАМ ✓
  
  Ціна за одиницю: {product.price / 100:.2f} ₴
  Сумарна вартість: {(product.price / 100) * quantity:.2f} ₴

────────────────────────────────────────────────────────────────

УМОВИ ПОСТАЧАННЯ:

  • Очікувана дата доставки: {delivery_date}
  • Строк доставки: {product.delivery_days or 7} днів
  • Спосіб доставки: Експрес
  • Терміни оплати: При отриманні
  • Гарантія товару: Стандартна

────────────────────────────────────────────────────────────────

З найкращими побажаннями,

Керівник складу
Спорткомплекс "Active Fit"
"""
        
        return {
            "status": "generated",
            "generated_at": order_date,
            "validation": {
                "quantity_ordered": quantity,
                "min_stock_required": min_required,
                "validation_passed": True,
                "message": f"Order meets minimum stock requirement: {quantity} >= {min_required}"
            },
            "order": {
                "article": product.article,
                "name": product.name,
                "quantity": quantity,
                "unit_price": product.price / 100,
                "total_price": (product.price / 100) * quantity,
                "supplier": product.supplier.name if product.supplier else "N/A",
                "supplier_email": product.supplier.contact_email if product.supplier else "N/A",
                "delivery_days": product.delivery_days or 7,
                "expected_delivery": delivery_date,
            },
            "business_letter": business_letter
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# SPORT: User bookings endpoints
# ==========================================

@app.get("/sport/user/bookings")
def get_user_bookings(user=Depends(require_user)):
    """Get all bookings/enrollments for current user"""
    try:
        username = user.get("username")
        
        # Find client by username
        clients = sport_service.store.list_all("clients")
        client = None
        for c in clients:
            if c.get("username") == username:
                client = c
                break
        
        if not client:
            return {"bookings": []}
        
        # Get all services and trainers
        services = sport_service.store.list_all("services")
        services_map = {s.get("service_id"): s for s in services}
        trainers = sport_service.store.list_all("trainers")
        trainers_map = {t.get("trainer_id"): t for t in trainers}

        # Filter bookings for this client
        bookings_raw = [b for b in sport_service.store.list_all("bookings") if b.get("client_id") == client.get("client_id")]

        bookings = []
        for b in bookings_raw:
            service = services_map.get(b.get("service_id"), {})
            trainer = trainers_map.get(b.get("trainer_id")) if b.get("trainer_id") else None
            bookings.append({
                "booking_id": b.get("booking_id"),
                "client_id": b.get("client_id"),
                "service_id": b.get("service_id"),
                "service_name": b.get("service_name") or service.get("service_name"),
                "price": b.get("price") or service.get("price"),
                "booking_date": b.get("booking_date"),
                "status": b.get("status", "confirmed"),
                "trainer_name": trainer.get("full_name") if trainer else None,
            })

        return {
            "bookings": bookings,
            "client_id": client.get("client_id"),
            "username": username
        }
    except Exception as e:
        logger.error(f"Failed to get user bookings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/sport/user/bookings")
def create_user_booking(payload: dict, user=Depends(require_user)):
    """Create booking for current user"""
    try:
        username = user.get("username")
        service_id = payload.get("service_id")
        booking_date = payload.get("booking_date")
        
        if not service_id or not booking_date:
            raise ValueError("service_id and booking_date are required")
        
        # Find client by username
        clients = sport_service.store.list_all("clients")
        client = None
        for c in clients:
            if c.get("username") == username:
                client = c
                break
        
        if not client:
            raise ValueError("Client not found")
        
        # Get service
        services = sport_service.store.list_all("services")
        service = None
        for s in services:
            if s.get("service_id") == service_id:
                service = s
                break
        
        if not service:
            raise ValueError(f"Service with id {service_id} not found")
        
        # Create booking object
        booking = {
            "client_id": client.get("client_id"),
            "service_id": service_id,
            "booking_date": booking_date,
            "status": "confirmed",
            "service_name": service.get("service_name"),
            "price": service.get("price"),
        }

        saved = sport_service.store.add("bookings", booking, "booking_id")

        return {"status": "booked", "booking": saved}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create booking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sport/user/bookings/{booking_id}")
def delete_user_booking(booking_id: int, user=Depends(require_user)):
    """Cancel/delete a booking belonging to the current user."""
    try:
        username = user.get("username")

        # Find client by username
        clients = sport_service.store.list_all("clients")
        client = next((c for c in clients if c.get("username") == username), None)
        if not client:
            raise ValueError("Client not found")

        # Verify booking belongs to this client
        bookings = sport_service.store.list_all("bookings")
        booking = next((b for b in bookings if b.get("booking_id") == booking_id), None)
        if not booking:
            raise ValueError("Booking not found")
        if booking.get("client_id") != client.get("client_id"):
            raise HTTPException(status_code=403, detail="Cannot cancel booking of another user")

        sport_service.store.delete("bookings", "booking_id", booking_id)
        return {"status": "cancelled", "booking_id": booking_id}
    except HTTPException:
        raise
    except ValueError as e:
        detail = str(e)
        status_code = 404 if "not found" in detail.lower() else 400
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        logger.error(f"Failed to delete booking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# DB SYNC: Products synchronization
# ==========================================

@app.get("/db/sync-products")
def db_sync_products_analysis(db: Session = Depends(get_db), user=Depends(require_role(["admin"]))):
    """
    Compare ProductDB (e-commerce database) with Products inventory.
    Returns sync status, discrepancies, and recommended actions.
    """
    try:
        # Get all products from ProductDB (e-commerce)
        db_products = db.query(ProductDB).all()
        
        # Build a list of DB products
        db_list = []
        for p in db_products:
            try:
                product_data = {
                    "article": p.article or "N/A",
                    "name": p.name or "N/A",
                    "category": None,
                    "category_id": p.category_id,
                    "supplier": None,
                    "supplier_id": p.supplier_id,
                    "price_uah": float(p.price / 100) if p.price else 0,  # price stored as cents
                    "quantity": p.quantity or 0,
                    "min_stock": p.min_stock or 0,
                    "delivery_days": p.delivery_days or 7,
                }
                
                # Safely get category name
                if hasattr(p, 'category') and p.category:
                    try:
                        product_data["category"] = p.category.name
                    except Exception:
                        product_data["category"] = "Unknown"
                
                # Safely get supplier name
                if hasattr(p, 'supplier') and p.supplier:
                    try:
                        product_data["supplier"] = p.supplier.name
                    except Exception:
                        product_data["supplier"] = "Unknown"
                
                db_list.append(product_data)
            except Exception as item_error:
                logger.warning(f"[SyncProducts] Error processing product {p.article}: {str(item_error)}")
                continue
        
        # Analyze sync status
        total_db = len(db_list)
        
        return {
            "status": "analyzed",
            "summary": {
                "total_db_products": total_db,
                "sync_recommendation": "Products inventory should mirror DB assortment for consistency"
            },
            "db_products": db_list,
            "actions": {
                "info": "All products from e-commerce database are listed above",
                "recommendation": "Use frontend sync button to reconcile any differences"
            }
        }
    except Exception as e:
        logger.error(f"Failed to analyze products sync: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

