# SportComplex API

Comprehensive API for managing a sports complex with trainer scheduling, shop, and client management.

## 🏗️ Architecture

This project uses a **polyglot persistence** architecture:
- **MySQL** - Transactional data (users, orders, trainers)
- **Redis** - Caching and real-time features
- **CouchDB** - Document storage (reports, medical certificates)
- **Neo4j** - Graph relationships (recommendations)

## 📁 Project Structure

```
sport-complex-api/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── auth.py      # Authentication (login, register)
│   │   ├── trainers.py  # Trainer management
│   │   ├── services.py  # Services (gym, pool, etc.)
│   │   ├── products.py  # Product catalog
│   │   └── orders.py    # Order processing
│   ├── core/            # Configuration
│   │   ├── config.py    # Settings
│   │   └── security.py  # JWT & password hashing
│   ├── db/              # Database connections
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Redis 6.0+
- CouchDB 3.0+
- Neo4j 5.0+

### Installation

1. **Clone the repository:**
```bash
cd sport-complex-api
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up databases:**

**MySQL:**
```bash
mysql -u root -p < ../Course-work-sport-complex-fa/mysql_schema.sql
```

**Neo4j:**
```bash
# Open Neo4j Browser and run:
# ../Course-work-sport-complex-fa/neo4j_schema.cypher
```

4. **Configure environment (optional):**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run the server:**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

#### Trainers
- `GET /api/v1/trainers` - List all trainers
- `POST /api/v1/trainers` - Create trainer
- `GET /api/v1/trainers/{id}` - Get trainer details
- `PATCH /api/v1/trainers/{id}` - Update trainer
- `GET /api/v1/trainers/{id}/schedules` - Get trainer schedule

#### Services
- `GET /api/v1/services` - List services (pool, gym, etc.)
- `POST /api/v1/services` - Create service

#### Products
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product details
- `PATCH /api/v1/products/{id}` - Update product

#### Orders
- `POST /api/v1/orders` - Create new order
- `GET /api/v1/orders` - List all orders
- `GET /api/v1/orders/{id}` - Get order details
- `PATCH /api/v1/orders/{id}/status` - Update order status

## 🔧 Configuration

Environment variables (`.env`):

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=sportcomplex
MYSQL_PASSWORD=password
MYSQL_DATABASE=sportcomplex_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# CouchDB
COUCHDB_HOST=localhost
COUCHDB_PORT=5984
COUCHDB_USER=admin
COUCHDB_PASSWORD=password

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 📝 Usage Examples

### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "role": "client"
  }'
```

### Create a product
```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Whey Protein 1kg",
    "price": 850.00,
    "quantity_in_stock": 50,
    "brand": "NutritionPro",
    "is_active": true
  }'
```

### Create an order
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "order_type": "in_store",
    "payment_method": "card",
    "items": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

## 🛠️ Development

### Run tests (when implemented)
```bash
pytest
```

### Code formatting
```bash
black app/
isort app/
```

## 📦 Features

- ✅ User authentication (JWT)
- ✅ Trainer management & scheduling
- ✅ Product catalog
- ✅ Order processing with stock management
- ✅ Service management
- ✅ RESTful API design
- ✅ Auto-generated API documentation
- ✅ Database connection pooling
- ✅ CORS support

## 🤝 Contributing

This is a course project. For educational purposes only.

## 📄 License

Educational project - No license.
