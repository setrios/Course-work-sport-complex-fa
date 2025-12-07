# Де використовуються CouchDB, Neo4j, Redis?

## 🔴 Redis (кеш-шар для швидкого доступу)

### Де знаходиться:
- **Конфіг**: `app/config.py` (строки 26-30)
- **Використання**: `app/services.py` (Supplier, Product сервіси)
- **Порт**: 6379 (localhost:6379 чи через Docker)

### Як підключається:
```python
# app/config.py
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
REDIS_TTL_SUPPLIERS = 120  # 2 хвилини
REDIS_TTL_PRODUCTS = 60    # 1 хвилина
```

### Конкретне використання 1️⃣ - Кешування списку постачальників:

**app/services.py (SupplierService.list)**
```python
def list(self, db: Session) -> List[dict]:
    """Get all suppliers from cache or database."""
    # 1️⃣ ШАГ 1: Спробуємо отримати з Redis
    cached = redis_client.get("all_suppliers")
    if cached:
        return json.loads(cached)  # ← Повертаємо з кешу (швидко!)
    
    # 2️⃣ ШАГ 2: Якщо нема в кеші → запит до MySQL
    suppliers = db.query(SupplierDB).all()
    result = [
        {
            "id": s.id,
            "name": s.name,
            "city": s.city,
            "country": s.country,
            "email": s.contact_email,
        }
        for s in suppliers
    ]
    
    # 3️⃣ ШАГ 3: Зберігаємо результат у Redis на 120 секунд
    redis_client.setex("all_suppliers", REDIS_TTL_SUPPLIERS, json.dumps(result))
    return result
```

**Коли кеш очищується?**
```python
# У ProductService.create() - при додаванні нового товару
redis_client.delete("product_list")  # Очищуємо кеш товарів

# У ProductService.update() - при оновленні товару
redis_client.delete("product_list")

# У SupplierService.create() - при додаванні нового постачальника
redis_client.delete("all_suppliers")  # Очищуємо кеш постачальників
```

### Конкретне використання 2️⃣ - Кешування списку товарів:

**app/services.py (ProductService.list)**
```python
def list(self, db: Session) -> List[dict]:
    """Get all products from cache or database."""
    # 1️⃣ ШАГ 1: Спробуємо отримати з Redis
    cached = redis_client.get("product_list")
    if cached:
        return json.loads(cached)  # ← Повертаємо з кешу
    
    # 2️⃣ ШАГ 2: Якщо нема → запит до MySQL з JOINами
    products = db.query(ProductDB).all()
    result = []
    for p in products:
        result.append({
            "article": p.article,
            "name": p.name,
            "category": p.category.name if p.category else "N/A",
            "supplier": p.supplier.name if p.supplier else "N/A",
            "price_uah": p.price / 100.0,
            "quantity": p.quantity,
            "min_stock": p.min_stock,
        })
    
    # 3️⃣ ШАГ 3: Кешуємо на 60 секунд
    redis_client.setex("product_list", REDIS_TTL_PRODUCTS, json.dumps(result))
    return result
```

### 📊 Переваги Redis:
- **Швидкість**: В пам'яті (не на диску)
- **Скорочення навантаження на БД**: Менше запитів до MySQL
- **TTL (Time To Live)**: Автоматична очистка кешу через X секунд

---

## 🔵 CouchDB (зберігання зображень товарів)

### Де знаходиться:
- **Конфіг**: `app/config.py` (строки 32-39)
- **Використання**: `app/services.py` (ProductService.upload_image, get_image)
- **Порт**: 5984 (localhost:5984/_utils)
- **Адміністратор**: couchdb / couchdb

### Як підключається:
```python
# app/config.py
COUCHDB_URL = os.getenv("COUCHDB_URL", "http://couchdb:couchdb@localhost:5984/")
try:
    couch_server = couchdb.Server(COUCHDB_URL)
    # Створюємо БД "product_images" якщо її нема
    db_couch = couch_server.create("product_images") if "product_images" not in couch_server else couch_server["product_images"]
except Exception as e:
    print(f"CouchDB Warning: {e}")
    db_couch = None
```

### Конкретне використання 1️⃣ - Завантаження зображення:

**app/services.py (ProductService.upload_image)**
```python
def upload_image(self, db: Session, article: str, image_base64: str, mime_type: str) -> dict:
    """Upload product image to CouchDB."""
    if not db_couch:
        raise ValueError("CouchDB is not available")
    
    # 1️⃣ Отримуємо товар з MySQL
    product = db.query(ProductDB).filter(ProductDB.article == article).first()
    if not product:
        raise ValueError(f"Product with article '{article}' not found")
    
    # 2️⃣ Підготовуємо документ для CouchDB
    document = {
        "type": "product_image",
        "article": article,
        "product_name": product.name,
        "mime_type": mime_type,  # наприклад "image/jpeg", "image/png"
        "image_base64": image_base64,  # Кодоване зображення
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    
    # 3️⃣ Зберігаємо в CouchDB
    try:
        doc_id, _ = db_couch.save(document)  # ← CouchDB генерує ID
        
        # 4️⃣ Зберігаємо посилання на CouchDB в MySQL
        product.image_doc_id = doc_id  # Посилання типу "abc123def456"
        db.commit()  # Зберігаємо в MySQL
        
        return {"status": "uploaded", "couchdb_id": doc_id, "article": article}
    except Exception as e:
        raise ValueError(f"Failed to upload image: {str(e)}")
```

### Конкретне використання 2️⃣ - Отримання зображення:

**app/services.py (ProductService.get_image)**
```python
def get_image(self, db: Session, article: str) -> dict:
    """Get product image from CouchDB."""
    if not db_couch:
        raise ValueError("CouchDB is not available")
    
    # 1️⃣ Отримуємо товар з MySQL
    product = db.query(ProductDB).filter(ProductDB.article == article).first()
    if not product or not product.image_doc_id:
        raise ValueError(f"No image found for product '{article}'")
    
    # 2️⃣ Отримуємо документ з CouchDB по ID
    try:
        doc = db_couch[product.image_doc_id]  # ← Запит до CouchDB
        
        return {
            "article": article,
            "mime_type": doc.get("mime_type", "image/jpeg"),
            "image_base64": doc.get("image_base64", ""),
            "uploaded_at": doc.get("uploaded_at"),
        }
    except Exception as e:
        raise ValueError(f"Failed to retrieve image: {str(e)}")
```

### 📊 Структура CouchDB документу:
```json
{
  "_id": "abc123def456",  // Генерується CouchDB
  "_rev": "1-xxxx",
  "type": "product_image",
  "article": "sko33",
  "product_name": "Спортивні кроссовки",
  "mime_type": "image/jpeg",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...",
  "uploaded_at": "2025-12-07T15:30:45.123456"
}
```

### 📊 Зв'язок MySQL ↔ CouchDB:
```
┌─────────────────────┐
│ MySQL (ProductDB)   │
├─────────────────────┤
│ id: 1               │
│ article: "sko33"    │
│ name: "Кроссовки"   │
│ image_doc_id: ───┐  │  (посилання на CouchDB)
│ ...             │  │
└────────────────│──┘
                 │
                 └──────────────┐
                                ▼
                    ┌──────────────────────────┐
                    │ CouchDB (product_images) │
                    ├──────────────────────────┤
                    │ _id: "abc123def456"      │
                    │ article: "sko33"         │
                    │ image_base64: "..."      │
                    │ mime_type: "image/jpeg"  │
                    │ uploaded_at: "2025-..."  │
                    └──────────────────────────┘
```

### 💡 Чому CouchDB для зображень?
- **Масштабованість**: Не переповнює MySQL
- **Гнучка схема**: JSON документи з будь-якою структурою
- **Репліцирування**: Можемо дублювати базу
- **Binary safe**: Зберігає Base64 зображення без проблем

---

## 🟣 Neo4j (графова БД для зв'язків)

### Де знаходиться:
- **Конфіг**: `app/config.py` (строки 41-44)
- **Використання**: `app/services.py` (в усіх Service класах)
- **Порт**: 7474 (http://localhost:7474), 7687 (bolt)
- **Адміністратор**: neo4j / neo4jneo4j

### Як підключається:
```python
# app/config.py
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jneo4j")
neo4j_driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
```

### Конкретне використання 1️⃣ - Запис категорії:

**app/services.py (CategoryService.create)**
```python
def create(self, db: Session, name: str) -> dict:
    # 1️⃣ Зберігаємо в MySQL
    category = CategoryDB(name=name)
    db.add(category)
    db.commit()
    
    # 2️⃣ Зберігаємо в Neo4j
    with neo4j_driver.session() as session:
        session.run(
            "MERGE (c:Category {name: $name})",
            name=category.name
        )
    
    return {"status": "created", "id": category.id, "name": category.name}
```

**Запит Cypher для Neo4j:**
```cypher
MERGE (c:Category {name: 'Одяг'})
```

**Результат в Neo4j:**
```
(Category {name: 'Одяг'})
```

### Конкретне використання 2️⃣ - Запис постачальника:

**app/services.py (SupplierService.create)**
```python
def create(self, db: Session, name: str, city: str, country: str, email: str) -> dict:
    # 1️⃣ Зберігаємо в MySQL
    supplier = SupplierDB(name=name, city=city, country=country, contact_email=email)
    db.add(supplier)
    db.commit()
    
    # 2️⃣ Зберігаємо в Neo4j з властивостями
    with neo4j_driver.session() as session:
        session.run(
            "MERGE (s:Supplier {mysql_id: $sid, name: $name, city: $city, country: $country})",
            sid=supplier.id,
            name=supplier.name,
            city=supplier.city,
            country=supplier.country,
        )
    
    redis_client.delete("all_suppliers")
    return {"status": "created", "id": supplier.id, "name": supplier.name}
```

**Запит Cypher:**
```cypher
MERGE (s:Supplier {
  mysql_id: 1,
  name: 'SportGear',
  city: 'Київ',
  country: 'Україна'
})
```

**Результат в Neo4j:**
```
(Supplier {mysql_id: 1, name: 'SportGear', city: 'Київ', country: 'Україна'})
```

### Конкретне використання 3️⃣ - Запис товару з зв'язками:

**app/services.py (ProductService.create)**
```python
def create(self, db: Session, payload) -> dict:
    # 1️⃣ Отримуємо категорію та постачальника
    category = db.query(CategoryDB).filter(CategoryDB.name == payload.category_name).first()
    supplier = db.query(SupplierDB).filter(SupplierDB.name == payload.supplier_name).first()
    
    # 2️⃣ Зберігаємо товар в MySQL
    product = ProductDB(
        article=payload.article,
        name=payload.name,
        category_id=category.id,
        supplier_id=supplier.id,
        # ...
    )
    db.add(product)
    db.commit()
    
    # 3️⃣ Зберігаємо в Neo4j зі зв'язками
    with neo4j_driver.session() as session:
        session.run(
            """
            MERGE (p:Product {mysql_id: $pid, article: $article, name: $name})
            WITH p
            MATCH (c:Category {name: $cat_name})
            MATCH (s:Supplier {mysql_id: $sup_id})
            MERGE (p)-[:IN_CATEGORY]->(c)
            MERGE (p)-[:SUPPLIED_BY]->(s)
            """,
            pid=product.id,
            article=product.article,
            name=product.name,
            cat_name=category.name,
            sup_id=supplier.id,
        )
    
    redis_client.delete("product_list")
    return {"status": "created", "article": product.article}
```

**Запит Cypher:**
```cypher
MERGE (p:Product {mysql_id: 1, article: 'sko33', name: 'Кроссовки'})
WITH p
MATCH (c:Category {name: 'Спортивне обладнання'})
MATCH (s:Supplier {mysql_id: 2})
MERGE (p)-[:IN_CATEGORY]->(c)
MERGE (p)-[:SUPPLIED_BY]->(s)
```

**Графовизуалізація:**
```
    ┌──────────────────┐
    │    Category      │
    │ (Спортивне обл.) │
    └────────┬─────────┘
             ▲
             │ IN_CATEGORY
             │
    ┌────────┴──────────┐
    │    Product        │
    │ (sko33 - Кроссо)  │
    └────────┬──────────┘
             │
             │ SUPPLIED_BY
             ▼
    ┌──────────────────┐
    │    Supplier      │
    │   (SportGear)    │
    └──────────────────┘
```

### Конкретне використання 4️⃣ - Оновлення товару:

**app/services.py (ProductService.update)**
```python
def update(self, db: Session, article: str, payload) -> dict:
    # 1️⃣ Оновлюємо в MySQL
    product.name = payload.name
    db.commit()
    
    # 2️⃣ Оновлюємо в Neo4j
    with neo4j_driver.session() as session:
        session.run(
            "MATCH (p:Product {mysql_id: $pid}) SET p.name = $name",
            pid=product.id,
            name=product.name
        )
    
    redis_client.delete("product_list")
    return {"status": "updated", "article": product.article, "name": product.name}
```

### Конкретне використання 5️⃣ - Видалення товару:

**app/services.py (ProductService.delete)**
```python
def delete(self, db: Session, article: str) -> dict:
    product_id = product.id
    
    # 1️⃣ Видаляємо з MySQL
    db.delete(product)
    db.commit()
    
    # 2️⃣ Видаляємо з Neo4j (DELETE зв'язки теж)
    with neo4j_driver.session() as session:
        session.run(
            "MATCH (p:Product {mysql_id: $pid}) DETACH DELETE p",
            pid=product_id
        )
    
    return {"status": "deleted", "article": product.article}
```

**Запит Cypher:** `DETACH DELETE` видалить вузол і ВСІ його зв'язки

### 📊 Neo4j запити (можна тестувати в http://localhost:7474):

```cypher
-- Показати всі категорії
MATCH (c:Category) RETURN c

-- Показати всіх постачальників
MATCH (s:Supplier) RETURN s

-- Показати всі товари та їх категорії
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category) RETURN p, c

-- Показати товари від конкретного постачальника
MATCH (p:Product)-[:SUPPLIED_BY]->(s:Supplier {name: 'SportGear'}) RETURN p, s

-- Показати повну граф (Category - Product - Supplier)
MATCH (c:Category)<-[:IN_CATEGORY]-(p:Product)-[:SUPPLIED_BY]->(s:Supplier) RETURN c, p, s

-- Підрахувати товари в категорії
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category {name: 'Спортивне обладнання'}) RETURN COUNT(p)

-- Знайти крім categoria категорії мають товари
MATCH (c:Category)<-[:IN_CATEGORY]-(p:Product) RETURN c.name, COUNT(p) as product_count

-- Знайти постачальників, що поставляють більше 5 товарів
MATCH (s:Supplier)<-[:SUPPLIED_BY]-(p:Product) 
WITH s, COUNT(p) as cnt 
WHERE cnt > 5 
RETURN s.name, cnt
```

---

## 📋 Зведена таблиця: Як і де використовуються БД

| БД | Порт | Призначення | Конкретне використання | Де |
|-------|------|------------|---------------------|-----|
| **Redis** | 6379 | Кеш | Товари, Постачальники | `app/services.py` |
| **CouchDB** | 5984 | Зображення | Завантаження/отримання зображень | `ProductService.upload_image()`, `get_image()` |
| **Neo4j** | 7687 | Граф зв'язків | Зв'язки Category-Product-Supplier | Усі операції CREATE/UPDATE/DELETE в `app/services.py` |
| **MySQL** | 3306 | Основні дані | Товари, Категорії, Постачальники | Основне сховище |

---

## 🔄 Повний цикл життя товару з усіма БД

### 1️⃣ Користувач клікає "Створити товар"

```
┌─────────────────────────────────────────────────────┐
│ Frontend: POST /api/products                        │
├─────────────────────────────────────────────────────┤
│ {"article": "sko33", "name": "Кроссовки", ...}     │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ main.py: POST /api/products/create                  │
├─────────────────────────────────────────────────────┤
│ → ProductService.create(db, payload)                │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 🟡 MySQL: INSERT INTO products (...)                │
│    UPDATE categories SET ...                        │
│    UPDATE suppliers SET ...                         │
├─────────────────────────────────────────────────────┤
│ ✅ Товар створений в БД                             │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 🟣 Neo4j: MERGE (p:Product)-[:IN_CATEGORY]-> ...   │
│          MERGE (p)-[:SUPPLIED_BY]->(:Supplier)     │
├─────────────────────────────────────────────────────┤
│ ✅ Граф зв'язків створений                          │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 🔴 Redis: DELETE "product_list"                     │
├─────────────────────────────────────────────────────┤
│ ✅ Кеш очищений (нова версія завантажиться)        │
└──────────────────────────────────────────────────────┘
```

### 2️⃣ Користувач завантажує зображення товару

```
┌──────────────────────────────────────────────────┐
│ Frontend: POST /api/products/sko33/image         │
│ Content: base64-encoded image                    │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│ main.py: POST /api/products/{article}/image      │
├──────────────────────────────────────────────────┤
│ → ProductService.upload_image(db, article, ...) │
└────────┬─────────────────────────────────────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
    ┌─────────────┐      ┌──────────────────┐
    │ 🟡 MySQL    │      │ 🔵 CouchDB       │
    ├─────────────┤      ├──────────────────┤
    │ UPDATE      │      │ SAVE document    │
    │ product SET │      │ {                │
    │ image_doc.. │      │   article: ...   │
    │             │      │   image_base64:..│
    │ image_doc_  │      │   mime_type: ... │
    │ id=abc123   │      │ }                │
    └─────────────┘      │ _id: abc123      │
                         └──────────────────┘
```

### 3️⃣ Користувач запитує список товарів

```
┌─────────────────────────────────────────┐
│ Frontend: GET /api/products             │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 🔴 Redis: GET "product_list"            │
├─────────────────────────────────────────┤
│ Знайдено? → Return (ШВИДКО!)            │
│ Не знайдено? ↓                          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 🟡 MySQL: SELECT * FROM products        │
│          LEFT JOIN categories ...       │
│          LEFT JOIN suppliers ...        │
├─────────────────────────────────────────┤
│ Результат → JSON                        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 🔴 Redis: SET "product_list" = JSON     │
│           TTL = 60 секунд               │
├─────────────────────────────────────────┤
│ Return JSON → Frontend                  │
└──────────────────────────────────────────┘
```

---

## 💾 Настройки для docker-compose

```yaml
# docker-compose.yml
services:
  sport-mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_DATABASE: sport-complex-cw
      MYSQL_USER: sport-complex-cw
      MYSQL_PASSWORD: sport-complex-cw

  sport-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  sport-couchdb:
    image: couchdb:3.3
    ports:
      - "5984:5984"
    environment:
      COUCHDB_USER: couchdb
      COUCHDB_PASSWORD: couchdb

  sport-neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/neo4jneo4j
```

---

## 🧪 Як тестувати кожну БД

### Redis тест:
```bash
# Перевірити підключення
redis-cli ping
# Результат: PONG

# Переглянути кешовані дані
redis-cli GET "product_list"
redis-cli GET "all_suppliers"
```

### CouchDB тест:
```bash
# Відкрити в браузері
http://localhost:5984/_utils

# Запит до API
curl http://couchdb:couchdb@localhost:5984/product_images

# Переглянути документи
curl http://couchdb:couchdb@localhost:5984/product_images/_all_docs
```

### Neo4j тест:
```bash
# Відкрити в браузері
http://localhost:7474

# Пароль: neo4jneo4j
# Запити писати в редакторі Cypher
MATCH (p:Product) RETURN p LIMIT 10
```

---

*Документ оновлено: 7 грудня 2025*
