# Швидкий фікс для демо-режиму
# Цей файл тимчасово відключає підключення до БД для тестування фронтенду

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# DEMO DATA (без бази даних)
DEMO_PRODUCTS = [
    {"id": 1, "name": "Whey Protein 1kg", "price": 850, "quantity_in_stock": 25, "brand": "NutritionPro", "is_active": True, "category_id": 1},
    {"id": 2, "name": "BCAA 500g", "price": 450, "quantity_in_stock": 15, "brand": "SportMax", "is_active": True, "category_id": 1},
    {"id": 3, "name": "Creatine Monohydrate", "price": 350, "quantity_in_stock": 30, "brand": "PowerFuel", "is_active": True, "category_id": 1},
    {"id": 4, "name": "Вода 1.5л", "price": 20, "quantity_in_stock": 100, "brand": "AquaPure", "is_active": True, "category_id": 2},
]

DEMO_TRAINERS = [
    {"id": 1, "first_name": "Іван", "last_name": "Петренко", "specialization": "fitness", "rating": 4.8, "hourly_rate": 300, "experience_years": 5, "bio": "Сертифікований тренер з фітнесу", "total_sessions": 150, "status": "active"},
    {"id": 2, "first_name": "Марія", "last_name": "Коваленко", "specialization": "gym", "rating": 4.9, "hourly_rate": 350, "experience_years": 7, "bio": "Майстер спорту з важкої атлетики", "total_sessions": 200, "status": "active"},
    {"id": 3, "first_name": "Олег", "last_name": "Сидоренко", "specialization": "pool", "rating": 4.7, "hourly_rate": 280, "experience_years": 4, "bio": "Тренер з плавання", "total_sessions": 120, "status": "active"},
]

DEMO_CLIENTS = [
    {"id": 1, "first_name": "Андрій", "last_name": "Шевченко", "phone": "+380501234567", "registration_date": "2024-01-15"},
    {"id": 2, "first_name": "Олена", "last_name": "Костенко", "phone": "+380672345678", "registration_date": "2024-02-20"},
]

DEMO_ORDERS = [
    {
        "id": 1, 
        "order_number": "ORD-20241201-ABC123", 
        "order_date": "2024-12-01T10:30:00", 
        "total_amount": 1700, 
        "status": "completed",
        "items": [
            {"product_id": 1, "quantity": 2, "price": 850}  # 2x Whey Protein
        ]
    },
    {
        "id": 2, 
        "order_number": "ORD-20241202-DEF456", 
        "order_date": "2024-12-02T14:15:00", 
        "total_amount": 450, 
        "status": "pending",
        "items": [
            {"product_id": 2, "quantity": 1, "price": 450}  # 1x BCAA
        ]
    },
]

DEMO_USERS = [
    {"id": 1, "email": "admin@sportcomplex.com", "password": "admin123", "role": "admin", "name": "Адміністратор"},
    {"id": 2, "email": "user@sportcomplex.com", "password": "user123", "role": "client", "name": "Тестовий Користувач"},
]

DEMO_SERVICES = [
    {"id": 1, "name": "Персональне тренування (Fitness)", "description": "Індивідуальне тренування з сертифікованим фітнес-тренером", "price": 300, "duration_minutes": 60, "service_type": "training", "is_active": True},
    {"id": 2, "name": "Персональне тренування (Gym)", "description": "Силові тренування з тренером у залі", "price": 350, "duration_minutes": 60, "service_type": "training", "is_active": True},
    {"id": 3, "name": "Групове тренування", "description": "Групові заняття фітнесом (до 10 осіб)", "price": 150, "duration_minutes": 60, "service_type": "training", "is_active": True},
    {"id": 4, "name": "Плавання (Індивідуальне)", "description": "Персональні заняття плаванням", "price": 280, "duration_minutes": 45, "service_type": "training", "is_active": True},
    {"id": 5, "name": "Масаж спортивний", "description": "Відновлювальний масаж після тренувань", "price": 400, "duration_minutes": 60, "service_type": "wellness", "is_active": True},
]

# API Routes (DEMO)

# Auth endpoints
@app.post("/api/v1/auth/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")
    
    # Find user
    for user in DEMO_USERS:
        if user["email"] == email and user["password"] == password:
            return {
                "access_token": f"demo_token_{user['id']}",
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "role": user["role"],
                    "name": user["name"]
                }
            }
    
    return {"detail": "Invalid credentials"}

@app.post("/api/v1/auth/register")
def register(data: dict):
    email = data.get("email")
    password = data.get("password")
    
    # Check if user exists
    for user in DEMO_USERS:
        if user["email"] == email:
            return {"detail": "User already exists"}
    
    # Create new user
    new_id = max([u["id"] for u in DEMO_USERS]) + 1
    new_user = {
        "id": new_id,
        "email": email,
        "password": password,
        "role": "client",
        "name": email.split("@")[0]
    }
    
    DEMO_USERS.append(new_user)
    
    return {
        "access_token": f"demo_token_{new_id}",
        "token_type": "bearer",
        "user": {
            "id": new_id,
            "email": email,
            "role": "client",
            "name": new_user["name"]
        }
    }

@app.get("/api/v1/products")
def get_products():
    return DEMO_PRODUCTS

@app.get("/api/v1/trainers")
def get_trainers():
    return DEMO_TRAINERS

@app.get("/api/v1/trainers/{trainer_id}")
def get_trainer(trainer_id: int):
    for trainer in DEMO_TRAINERS:
        if trainer["id"] == trainer_id:
            return trainer
    return {"detail": "Trainer not found"}

@app.get("/api/v1/services")
def get_services():
    return DEMO_SERVICES

@app.get("/api/v1/clients")
def get_clients():
    return DEMO_CLIENTS

@app.get("/api/v1/clients/{client_id}")
def get_client(client_id: int):
    for client in DEMO_CLIENTS:
        if client["id"] == client_id:
            return client
    return {"detail": "Client not found"}

@app.get("/api/v1/orders")
def get_orders():
    return DEMO_ORDERS

@app.get("/api/v1/analytics/bestsellers")
def get_bestsellers():
    # Calculate real bestsellers from orders
    sales_count = {}
    
    for order in DEMO_ORDERS:
        items = order.get("items", [])
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            
            if product_id in sales_count:
                sales_count[product_id] += quantity
            else:
                sales_count[product_id] = quantity
    
    # Convert to list and sort by sales count
    bestsellers = [
        {"product_id": pid, "sales_count": count}
        for pid, count in sales_count.items()
    ]
    bestsellers.sort(key=lambda x: x["sales_count"], reverse=True)
    
    return {"bestsellers": bestsellers}

@app.post("/api/v1/clients")
def create_client(data: dict):
    # Generate new ID
    new_id = max([c["id"] for c in DEMO_CLIENTS]) + 1 if DEMO_CLIENTS else 1
    
    # Create new client
    new_client = {
        "id": new_id,
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "phone": data.get("phone"),
        "registration_date": "2025-12-05"  # Today's date
    }
    
    # Add to list
    DEMO_CLIENTS.append(new_client)
    
    return new_client

@app.post("/api/v1/orders")
def create_order(data: dict):
    # Generate new ID and order number
    new_id = max([o["id"] for o in DEMO_ORDERS]) + 1 if DEMO_ORDERS else 1
    
    # Get items from request
    items = data.get("items", [])
    
    # Calculate total amount
    total_amount = 0
    order_items = []
    
    # Update product quantities and build order items
    for item in items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)
        
        # Find product and decrease stock
        for product in DEMO_PRODUCTS:
            if product["id"] == product_id:
                product["quantity_in_stock"] -= quantity
                if product["quantity_in_stock"] < 0:
                    product["quantity_in_stock"] = 0
                
                # Add to order items with price
                order_items.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": product["price"]
                })
                total_amount += product["price"] * quantity
                break
    
    new_order = {
        "id": new_id,
        "order_number": f"ORD-20251205-DEMO{new_id}",
        "order_date": "2025-12-05T23:18:00",
        "total_amount": total_amount,
        "status": "pending",
        "items": order_items
    }
    
    # Add to list
    DEMO_ORDERS.append(new_order)
    
    return new_order

# BOOKINGS (Admin View Support)
DEMO_BOOKINGS = []

@app.get("/api/v1/bookings")
def get_bookings():
    return DEMO_BOOKINGS

@app.post("/api/v1/bookings")
def create_booking(data: dict):
    # Generate ID
    new_id = len(DEMO_BOOKINGS) + 1
    booking_number = f"BK-{20250000 + new_id}"
    
    # Resolve Trainer Name
    trainer_id = data.get("trainer_id")
    trainer_name = None
    if trainer_id:
        for t in DEMO_TRAINERS:
            if str(t["id"]) == str(trainer_id):
                trainer_name = f"{t['first_name']} {t['last_name']}"
                break
    
    # Slot Validation Rules
    service_name = data.get("service_name", "")
    booking_date = data.get("date")
    booking_time = data.get("time") # Format "HH:mm"
    
    try:
        hour = int(booking_time.split(":")[0])
    except:
        raise HTTPException(status_code=400, detail="Невірний формат часу")

    # Rule 1: Operating Hours (8:00 - 21:00)
    # Allows booking up to 20:00 (ending at 21:00)
    if hour < 8 or hour > 20: 
        raise HTTPException(status_code=400, detail="Клуб працює з 8:00 до 21:00")

    # Rule 2: Group vs Personal Slots
    is_group = "Групове" in service_name
    
    if is_group:
        # Group: Only 10:00 - 12:00
        if hour not in [10, 11]:
            raise HTTPException(status_code=400, detail="Групові тренування тільки з 10:00 до 12:00")
            
        # Group bookings are NON-BLOCKING (unlimited capacity for demo)
    else:
        # Personal: Any other time EXCEPT 10:00-12:00
        if hour in [10, 11]:
            raise HTTPException(status_code=400, detail="Цей час зарезервовано для групових занять")
            
        # Personal Conflict Check (Blocking)
        if trainer_id:
            for booking in DEMO_BOOKINGS:
                if (booking.get("trainer_name") == trainer_name and 
                    booking.get("date") == booking_date and 
                    booking.get("time") == booking_time and
                    booking.get("status") != "cancelled"):
                    raise HTTPException(status_code=400, detail="Цей час вже зайнято. Оберіть інший слот.")

    new_booking = {
        "id": new_id,
        "booking_number": booking_number,
        "service_name": service_name,
        "date": booking_date,
        "time": f"{booking_time} - {hour+1}:00", # Save slot range
        "notes": data.get("notes"),
        "status": "confirmed",
        "client_id": 1, 
        "trainer_name": trainer_name,
        "created_at": "2025-12-06T12:00:00"
    }
    
    DEMO_BOOKINGS.append(new_booking)
    return new_booking

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

@app.get("/")
def root():
    return FileResponse("static/index.html")
