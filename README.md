# 🏢 Система Управління Інтернет-Магазином + Спорткомплексом

**Курсова робота з бази даних**

Повнофункціональний backend на FastAPI з 4 типами БД (MySQL, Redis, Neo4j, CouchDB) + Frontend + Docker.

---

## 🚀 Швидкий Старт (з нуля)

### 1. Клонувати репозиторій
```bash
git clone https://github.com/setrios/Course-work-sport-complex-fa.git
cd Course-work-sport-complex-fa
```

### 2. Запустити Docker контейнери
```powershell
# Windows PowerShell
.\start-docker.ps1
# Чекаємо ~2-3 хвилини поки всі контейнери завантажаться
```

### 3. Встановити Python залежності
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Запустити Backend
```bash
python main.py
# Відкрити: http://localhost:8000
```

### 5. Запустити Frontend (опційно)
```bash
# Новий термінал
python serve-frontend.py
# Відкрити: http://localhost:8001
```

---

## 🗄️ Архітектура

### Бази Даних (4 типи)
- **MySQL** - Структуровані дані (товари, постачальники, замовлення)
- **Redis** - Кешування для швидкого доступу
- **Neo4j** - Графові зв'язки (мережа постачальників)
- **CouchDB** - Зображення товарів (blob storage)

### Backend
- **FastAPI** - REST API
- **SQLAlchemy** - ORM для MySQL
- **Uvicorn** - ASGI сервер

### Frontend
- Чистий HTML/CSS/JavaScript
- Single Page Application
- Responsive дизайн

---

## 📦 Docker Контейнери

```yaml
Сервіси:
- MySQL (порт 3306)
- Redis (порт 6379)
- Neo4j (порт 7474, 7687)
- CouchDB (порт 5984)
```

**Команди:**
```powershell
.\start-docker.ps1    # Запустити всі контейнери
.\stop-docker.ps1     # Зупинити всі контейнери
docker ps             # Перевірити статус
```

---

## 📚 API Ендпоінти

### Аутентифікація
```
POST /auth/register - Реєстрація
POST /auth/login    - Вхід
GET  /auth/me       - Поточний користувач
POST /auth/logout   - Вихід
```

### Товари
```
GET  /products/assortment        - Список товарів
POST /products/                  - Створити товар (admin)
GET  /products/search/{query}    - Пошук
GET  /products/stock-extremes    - Мін/макс запаси
GET  /products/by-article/{sku}  - Товар за артикулом
```

### Постачальники
```
GET  /suppliers/     - Список постачальників
POST /suppliers/     - Створити постачальника (admin)
```

### Спорткомплекс
```
GET  /sport/clients     - Клієнти
POST /sport/trainers    - Додати тренера
GET  /sport/services    - Послуги
GET  /sport/analytics   - Аналітика
```

### Database Queries (Admin)
```
GET  /db/products/images         - Зображення товарів
GET  /db/assortment             - Асортимент з деталями
GET  /db/price-availability     - Матриця цін
GET  /db/min-max-products       - Екстремальні значення
GET  /db/suppliers              - Мережа постачальників
POST /db/generate-order         - Генерація замовлення
```

**Swagger документація:** http://localhost:8000/docs

---

## 🧪 Тестування

### Запустити всі тести
```bash
pytest
# 61 тестів, 89% покриття, ~40 секунд
```

### Тести з покриттям
```bash
pytest --cov=app --cov=main --cov-report=html
# Відкрити: htmlcov/index.html
```

### Вибіркові тести
```bash
pytest tests/test_auth.py           # Тільки аутентифікація
pytest tests/test_ecommerce.py      # Тільки е-комерція
pytest tests/test_sport.py          # Тільки спорткомплекс
```

---

## 📁 Структура Проєкту

```
Course-work-sport-complex-fa/
├── app/
│   ├── auth.py           # Аутентифікація
│   ├── config.py         # Конфігурація БД
│   ├── db_models.py      # SQLAlchemy моделі
│   ├── schemas.py        # Pydantic схеми
│   ├── services.py       # Бізнес-логіка
│   └── sport_models.py   # Моделі спорткомплексу
├── frontend/             # HTML/CSS/JS
├── tests/                # Pytest тести (70 тестів)
├── main.py              # FastAPI додаток
├── docker-compose.yml   # Docker конфігурація
├── requirements.txt     # Python залежності
├── start-docker.ps1     # Запуск Docker
├── stop-docker.ps1      # Зупинка Docker
└── README.md            # Ця документація
```

---

## 🔧 Налаштування

### Змінні середовища (опційно)
Створіть `.env` файл:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root_password
MYSQL_DATABASE=sport_complex_db

REDIS_HOST=localhost
REDIS_PORT=6379

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

COUCHDB_URL=http://admin:admin_password@localhost:5984
```

### Порти за замовчуванням
```
Backend API:    8000
Frontend:       8001
MySQL:          3306
Redis:          6379
Neo4j Browser:  7474
Neo4j Bolt:     7687
CouchDB:        5984
```

---

## 👥 Користувачі за замовчуванням

### Backend
```
Адміністратор:
  username: admin
  password: admin123

Користувач:
  username: user
  password: user123
```

### Neo4j
```
username: neo4j
password: neo4j_password
```

### CouchDB
```
username: admin
password: admin_password
```

---

## 🛠️ Розв'язання Проблем

### Docker не запускається
```powershell
# Перевірити чи Docker Desktop запущений
docker --version

# Перезапустити Docker Desktop
# Або перезавантажити систему
```

### Порт вже зайнятий
```powershell
# Знайти процес на порту 8000
netstat -ano | findstr :8000

# Вбити процес (замініть PID)
taskkill /PID <PID> /F
```

### База даних не підключається
```bash
# Перевірити статус контейнерів
docker ps

# Перезапустити контейнери
.\stop-docker.ps1
.\start-docker.ps1
```

### Помилки pip install
```bash
# Оновити pip
python -m pip install --upgrade pip

# Встановити з чистого стану
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Статистика

- **Backend тести:** 61 ✅ PASSED
- **Покриття коду:** 89%
- **Ендпоінтів API:** 40+
- **Типів БД:** 4
- **Часу розробки:** ~6 тижнів

---

## 📖 Детальна Документація

Для детальної інформації див. **SETUP_GUIDE.md**

---

## 🎓 Автор

**Курсова робота**  
Дисципліна: Бази даних  
Рік: 2025

---

## 📝 Ліцензія

Освітній проєкт


**Чому MySQL:**
- Транзакційність (ACID)
- Складні JOIN запити
- Foreign Keys для цілісності даних
- Швидкий пошук за індексами

### 2. **Redis** (In-memory кеш)
**Призначення:** Прискорення читання часто запитуваних даних

**Що кешується:**
- Список товарів (TTL: 60 сек)
- Список постачальників (TTL: 120 сек)

**Чому Redis:**
- Надшвидкий доступ (мілісекунди)
- Зменшення навантаження на MySQL
- Автоматичне оновлення через TTL

### 3. **CouchDB** (Документна NoSQL)
**Призначення:** Зберігання неструктурованих даних (зображень продукції)

**База:** `product_images`

**Структура документу:**
```json
{
  "type": "product_image",
  "article": "LAPTOP-001",
  "product_name": "Ноутбук Dell XPS 15",
  "mime_type": "image/jpeg",
  "image_base64": "iVBORw0KGgo...",
  "uploaded_at": "2025-12-05T14:30:00"
}
```

**Чому CouchDB:**
- Гнучка схема (без жорсткої структури)
- Зберігання бінарних даних (Base64)
- RESTful API з коробки
- Реплікація для розподілених систем

### 4. **Neo4j** (Графова БД)
**Призначення:** Аналітика зв'язків між постачальниками, товарами та категоріями

**Граф:**
```
(Supplier)-[:SUPPLIES]->(Product)-[:BELONGS_TO]->(Category)
```

**Запити:**
- Аналіз популярності товарів
- Постачальники по містах/країнах
- Пошук альтернативних постачальників

**Чому Neo4j:**
- Швидкі запити по зв'язках
- Візуалізація даних
- Рекомендаційні системи
- Граф краще таблиць для багаторівневих зв'язків

---

## 🏗️ Структура сутностей БД

### Основні сутності:

#### Постачальник (Supplier)
```python
{
  "id": int,
  "name": str,           # Назва компанії
  "city": str,           # Місто
  "country": str,        # Країна
  "contact_email": str   # Email для зв'язку
}
```

#### Товар (Product)
```python
{
  "id": int,
  "article": str,        # Артикул (унікальний код)
  "name": str,           # Найменування
  "category_id": int,    # FK -> categories
  "supplier_id": int,    # FK -> suppliers
  "price": int,          # Вартість (в копійках)
  "quantity": int,       # Наявна кількість
  "min_stock": int,      # Мінімальний запас
  "delivery_days": int,  # Час постачання (днів)
  "image_doc_id": str    # Посилання на CouchDB
}
```

#### Категорія (Category)
```python
{
  "id": int,
  "name": str  # Назва категорії
}
```

---

## 🚀 Встановлення та запуск

### Крок 1: Встановлення залежностей

```bash
pip install -r requirements.txt
```

### Крок 2: Налаштування баз даних

**MySQL:**
```sql
CREATE DATABASE `sport-complex-cw`;
CREATE USER 'sport-complex-cw'@'127.0.0.1' IDENTIFIED BY 'sport-complex-cw';
GRANT ALL PRIVILEGES ON `sport-complex-cw`.* TO 'sport-complex-cw'@'127.0.0.1';
```

**Redis:**
```bash
# Запуск на порту 6379 (за замовчуванням)
redis-server
```

**CouchDB:**
```bash
# Доступ: http://localhost:5984
# Логін: couchdb
# Пароль: couchdb
```

**Neo4j:**
```bash
# Bolt: bolt://localhost:7687
# Логін: neo4j
# Пароль: neo4jneo4j
```

### Крок 3: Запуск сервера

```bash
python main.py
```

Або через uvicorn:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**API доступне за адресою:** http://127.0.0.1:8000

**Swagger документація:** http://127.0.0.1:8000/docs

---

## 🧪 Тестування

### Автоматичні тести:

```bash
python test_requests.py
```

Скрипт протестує:
- ✅ Створення постачальників
- ✅ Додавання товарів
- ✅ Всі 7 запитів згідно завдання
- ✅ Завантаження зображень (CouchDB)
- ✅ Графову аналітику (Neo4j)
- ✅ Генерацію ділових листів

### Ручне тестування через Swagger:

1. Відкрийте http://127.0.0.1:8000/docs
2. Використовуйте інтерактивний інтерфейс
3. Кожен endpoint можна протестувати безпосередньо

---

## 📊 Приклади використання

### 1. Додавання постачальника

```bash
curl -X POST http://localhost:8000/suppliers/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechWorld",
    "city": "Київ",
    "country": "Україна",
    "contact_email": "info@techworld.ua"
  }'
```

### 2. Додавання товару

```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "article": "LAPTOP-001",
    "name": "Ноутбук Dell XPS 15",
    "category_name": "Електроніка",
    "supplier_name": "TechWorld",
    "price": 35000.50,
    "quantity": 3,
    "min_stock": 5,
    "delivery_days": 10
  }'
```

### 3. Пошук товару

```bash
curl http://localhost:8000/products/search/ноутбук
```

### 4. Генерація листів про низькі запаси

```bash
curl http://localhost:8000/orders/low-stock-report
```

**Відповідь:**
```json
{
  "total_letters": 1,
  "letters": [
    {
      "supplier": "TechWorld",
      "email": "info@techworld.ua",
      "letter": "Шановний постачальнику TechWorld,\n\n
                 Звертаємося до Вас з приводу необхідності 
                 поповнення асортименту...\n\n
                 - Ноутбук Dell XPS 15 (Артикул: LAPTOP-001)\n
                   Поточна кількість: 3 шт.\n
                   Мінімальний запас: 5 шт.\n
                   Необхідна кількість: 7 шт.\n
                   Час постачання: 10 днів\n\n..."
    }
  ]
}
```

---

## 📁 Структура проекту

```
Course-work-sport-complex-fa/
│
├── main.py                    # Основний код FastAPI додатку
├── requirements.txt           # Залежності Python
├── API_DOCUMENTATION.md       # Детальна документація API
├── test_requests.py           # Автоматичні тести
├── README.md                  # Цей файл
└── instructions.md            # Початкове завдання
```

---

## 🔧 Технології

- **Backend:** FastAPI (Python 3.8+)
- **MySQL:** SQLAlchemy ORM
- **Redis:** redis-py
- **CouchDB:** python-couchdb
- **Neo4j:** neo4j-driver
- **Валідація:** Pydantic

---

## 📝 Відповідність вимогам курсової

| Вимога | Реалізація | Бази даних |
|--------|------------|------------|
| Рисунки продукції | ✅ POST/GET /products/upload-image/ | CouchDB |
| Асортиментний список | ✅ GET /products/assortment | MySQL + Redis |
| Наявність/вартість | ✅ GET /products/search/{name} | MySQL + Redis |
| Мін/макс кількість | ✅ GET /products/stock-extremes | MySQL |
| Список постачальників | ✅ GET /suppliers/ | MySQL + Redis |
| Інфо за артикулом | ✅ GET /products/by-article/{article} | MySQL |
| Ділові листи | ✅ GET /orders/low-stock-report | MySQL + Neo4j |
| Аналітика | ✅ GET /analytics/* | Neo4j |

---

## 👨‍💻 Автор

**Курсова робота з бази даних**
Тема: База даних товарного асортименту інтернет-магазину

---

## 📄 Ліцензія

MIT License - використовуйте вільно для навчальних цілей
