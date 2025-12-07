# 🔧 Детальна Інструкція з Установки

## Передумови

### Необхідне ПЗ
- **Python 3.8+** - [Завантажити](https://www.python.org/downloads/)
- **Docker Desktop** - [Завантажити](https://www.docker.com/products/docker-desktop/)
- **Git** - [Завантажити](https://git-scm.com/downloads)

### Перевірка встановлення
```powershell
python --version     # Python 3.8+
docker --version     # Docker 20.10+
git --version        # Git 2.30+
```

---

## Крок 1: Клонування Репозиторію

```bash
git clone https://github.com/setrios/Course-work-sport-complex-fa.git
cd Course-work-sport-complex-fa
```

---

## Крок 2: Docker Контейнери

### 2.1. Запустити Docker Desktop
1. Відкрити Docker Desktop
2. Дочекатися повного запуску (зелений індикатор)

### 2.2. Запустити контейнери
```powershell
# Windows PowerShell
.\start-docker.ps1
```

**Що відбувається:**
- Завантажуються образи (якщо вперше): ~1-2 ГБ
- Запускаються 4 контейнери: MySQL, Redis, Neo4j, CouchDB
- Створюється мережа `sport-network`
- Ініціалізується база даних MySQL

**Час:** 2-5 хвилин (вперше), 30 секунд (наступні рази)

### 2.3. Перевірити статус
```bash
docker ps
```

Повинно бути **4 запущених контейнери:**
```
sport-mysql    (порт 3306)
sport-redis    (порт 6379)
sport-neo4j    (порт 7474, 7687)
sport-couchdb  (порт 5984)
```

---

## Крок 3: Python Віртуальне Середовище

### 3.1. Створити venv
```bash
python -m venv .venv
```

### 3.2. Активувати
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Якщо помилка виконання скриптів:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3.3. Оновити pip
```bash
python -m pip install --upgrade pip
```

---

## Крок 4: Встановити Залежності

```bash
pip install -r requirements.txt
```

**Встановлюється:**
- FastAPI, Uvicorn - Backend framework
- SQLAlchemy, PyMySQL - MySQL ORM
- Redis, neo4j, cloudant - Драйвери БД
- Pytest, Selenium - Тестування
- та інші залежності

**Час:** 2-3 хвилини

---

## Крок 5: Запустити Backend

```bash
python main.py
```

**Вивід:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Перевірка:**
- Відкрити: http://localhost:8000
- API документація: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Крок 6: Запустити Frontend (Опційно)

### У новому терміналі:
```bash
# Активувати venv
.\.venv\Scripts\Activate.ps1

# Запустити frontend сервер
python serve-frontend.py
```

**Відкрити:** http://localhost:8001

---

## Крок 7: Перевірка Роботи

### 7.1. Health Check
```bash
curl http://localhost:8000/health
```

Відповідь: `{"status": "ok"}`

### 7.2. Реєстрація користувача
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123", "email": "test@test.com"}'
```

### 7.3. Логін
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 7.4. Swagger UI
Відкрити http://localhost:8000/docs та протестувати ендпоінти

---

## Крок 8: Запустити Тести (Опційно)

```bash
pytest
```

**Очікуваний результат:**
```
61 passed, 9 skipped in ~40s
Coverage: 89%
```

---

## 🎯 Швидка Перевірка (Checklist)

- [ ] Docker Desktop запущений
- [ ] 4 контейнери працюють (`docker ps`)
- [ ] Python venv активовано
- [ ] Залежності встановлені
- [ ] Backend запущений (http://localhost:8000)
- [ ] Health check повертає OK
- [ ] Swagger UI доступний

---

## 🛠️ Розв'язання Проблем

### Помилка: "Docker daemon not running"
**Рішення:** Запустити Docker Desktop

### Помилка: "Port 3306 already in use"
**Рішення:**
```powershell
# Знайти процес
netstat -ano | findstr :3306
# Вбити процес
taskkill /PID <PID> /F
# Або змінити порт в docker-compose.yml
```

### Помилка: "Module not found"
**Рішення:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Помилка: "Cannot connect to MySQL"
**Рішення:**
```bash
# Перезапустити контейнери
.\stop-docker.ps1
.\start-docker.ps1
# Почекати 30 секунд
```

### Помилка: "Permission denied" (PowerShell)
**Рішення:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🗂️ Структура Після Установки

```
Course-work-sport-complex-fa/
├── .venv/              ✅ Віртуальне середовище
├── app/                ✅ Backend код
├── frontend/           ✅ Frontend файли
├── tests/              ✅ Тести
├── htmlcov/            ✅ Coverage report
├── main.py             ✅ Головний файл
├── docker-compose.yml  ✅ Docker конфігурація
└── requirements.txt    ✅ Залежності
```

---

## 📦 Docker Контейнери - Детально

### MySQL
```yaml
Образ: mysql:8.0
Порт: 3306
Користувач: root
Пароль: root_password
База: sport_complex_db
Ініціалізація: setup_mysql.sql
```

### Redis
```yaml
Образ: redis:7-alpine
Порт: 6379
Пароль: немає
Призначення: Кешування
```

### Neo4j
```yaml
Образ: neo4j:5.13
Порти: 7474 (HTTP), 7687 (Bolt)
Користувач: neo4j
Пароль: neo4j_password
Призначення: Графові зв'язки
```

### CouchDB
```yaml
Образ: couchdb:3.3
Порт: 5984
Користувач: admin
Пароль: admin_password
Призначення: Зберігання зображень
```

---

## 🔄 Lifecycle Команди

### Запуск
```powershell
.\start-docker.ps1    # Контейнери
python main.py        # Backend
python serve-frontend.py  # Frontend (опційно)
```

### Зупинка
```powershell
Ctrl+C               # Зупинити backend/frontend
.\stop-docker.ps1    # Зупинити контейнери
```

### Очистка
```powershell
docker-compose down -v    # Видалити контейнери + volumes
Remove-Item -Recurse .venv, htmlcov, __pycache__  # Очистити артефакти
```

### Перезапуск
```powershell
.\stop-docker.ps1
.\start-docker.ps1
python main.py
```

---

## 🧪 Тестування - Детально

### Базові команди
```bash
pytest                    # Всі тести
pytest -v                 # Verbose
pytest -q                 # Quiet
pytest --tb=short         # Короткий traceback
```

### Вибіркові тести
```bash
pytest tests/test_auth.py                      # Аутентифікація
pytest tests/test_ecommerce.py                 # Е-комерція
pytest tests/test_sport.py                     # Спорткомплекс
pytest tests/test_integration.py               # Інтеграція
pytest -k "test_login"                         # За назвою
```

### Coverage
```bash
pytest --cov=app --cov=main                    # Terminal report
pytest --cov=app --cov=main --cov-report=html  # HTML report
# Відкрити: htmlcov/index.html
```

### Frontend тести (Selenium)
```bash
# Потрібно запустити frontend
python serve-frontend.py &
pytest tests/test_frontend.py -v
```

---

## 🌐 Доступ до Сервісів

### Після запуску доступні:

| Сервіс | URL | Логін/Пароль |
|--------|-----|--------------|
| **Backend API** | http://localhost:8000 | admin/admin123 |
| **Swagger Docs** | http://localhost:8000/docs | - |
| **Frontend** | http://localhost:8001 | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j/neo4j_password |
| **CouchDB Fauxton** | http://localhost:5984/_utils | admin/admin_password |

---

## 📚 Наступні Кроки

1. ✅ Установка завершена
2. 🔍 Дослідити Swagger API (http://localhost:8000/docs)
3. 🧪 Запустити тести (`pytest`)
4. 👨‍💻 Почати розробку
5. 📖 Читати код у папці `app/`

---

**Повернутися до:** [README.md](README.md)
 Посібник з налаштування баз даних

## Передумови

Переконайтеся, що у вас встановлено:
- Python 3.8+
- MySQL Server 8.0+
- Redis Server
- CouchDB 3.0+
- Neo4j Community Edition 5.0+

---

## 1. Налаштування MySQL

### Windows:

1. Завантажте MySQL Installer з офіційного сайту
2. Встановіть MySQL Server
3. Відкрийте MySQL Workbench або командний рядок:

```bash
mysql -u root -p
```

4. Виконайте команди:

```sql
CREATE DATABASE `sport-complex-cw` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sport-complex-cw'@'127.0.0.1' IDENTIFIED BY 'sport-complex-cw';
GRANT ALL PRIVILEGES ON `sport-complex-cw`.* TO 'sport-complex-cw'@'127.0.0.1';
FLUSH PRIVILEGES;
```

### Перевірка підключення:

```bash
mysql -h 127.0.0.1 -u sport-complex-cw -p sport-complex-cw
# Пароль: sport-complex-cw
```

---

## 2. Налаштування Redis

### Windows:

1. Завантажте Redis для Windows (неофіційна збірка):
   - https://github.com/microsoftarchive/redis/releases

2. Або через WSL:
```bash
wsl --install
wsl
sudo apt update
sudo apt install redis-server
redis-server
```

3. Або через Docker:
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### Перевірка:

```bash
redis-cli ping
# Відповідь: PONG
```

**Налаштування в коді:**
```python
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
```

---

## 3. Налаштування CouchDB

### Windows:

1. Завантажте CouchDB Installer:
   - https://couchdb.apache.org/

2. Під час встановлення:
   - Оберіть "Standalone mode"
   - Встановіть логін: `couchdb`
   - Встановіть пароль: `couchdb`

3. CouchDB запуститься автоматично на порту 5984

### Перевірка:

Відкрийте браузер:
```
http://localhost:5984/_utils/
```

Або через curl:
```bash
curl http://localhost:5984/
```

**Відповідь:**
```json
{
  "couchdb": "Welcome",
  "version": "3.x.x"
}
```

### Створення бази (опціонально, програма створить автоматично):

```bash
curl -X PUT http://couchdb:couchdb@localhost:5984/product_images
```

**Налаштування в коді:**
```python
couch_server = couchdb.Server('http://couchdb:couchdb@localhost:5984/')
```

---

## 4. Налаштування Neo4j

### Windows:

1. Завантажте Neo4j Desktop:
   - https://neo4j.com/download/

2. Створіть новий проект
3. Створіть нову базу даних:
   - Name: `shop-graph`
   - Password: `neo4jneo4j`
   - Version: 5.x

4. Запустіть базу

### Альтернатива - Docker:

```bash
docker run -d ^
  --name neo4j ^
  -p 7474:7474 -p 7687:7687 ^
  -e NEO4J_AUTH=neo4j/neo4jneo4j ^
  neo4j:latest
```

### Перевірка:

Відкрийте браузер:
```
http://localhost:7474
```

Логін: `neo4j`
Пароль: `neo4jneo4j`

### Тестовий запит:

```cypher
RETURN "Hello Neo4j!" AS message
```

**Налаштування в коді:**
```python
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jneo4j"))
```

---

## 5. Встановлення Python залежностей

```bash
pip install -r requirements.txt
```

**Файл requirements.txt:**
```
fastapi
uvicorn
sqlalchemy
pymysql
redis
couchdb
neo4j
pydantic
```

---

## 6. Запуск програми

### Спосіб 1 (простий):
```bash
python main.py
```

### Спосіб 2 (з reload):
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Перевірка:

```bash
curl http://localhost:8000/suppliers/
```

---

## 7. Тестування

```bash
python test_requests.py
```

---

## 🐛 Вирішення проблем

### MySQL: Access Denied

```sql
-- Перевірте користувача
SELECT user, host FROM mysql.user WHERE user='sport-complex-cw';

-- Якщо немає, створіть:
CREATE USER 'sport-complex-cw'@'127.0.0.1' IDENTIFIED BY 'sport-complex-cw';
GRANT ALL PRIVILEGES ON `sport-complex-cw`.* TO 'sport-complex-cw'@'127.0.0.1';
FLUSH PRIVILEGES;
```

### Redis: Connection Refused

```bash
# Перевірте чи запущений Redis
redis-cli ping

# Якщо ні, запустіть:
redis-server

# Або через службу Windows:
services.msc -> Redis -> Start
```

### CouchDB: Connection Error

```bash
# Перевірте статус
curl http://localhost:5984/

# Перезапустіть службу
services.msc -> Apache CouchDB -> Restart
```

### Neo4j: Authentication Failed

1. Відкрийте Neo4j Desktop
2. Зупиніть базу
3. Змініть пароль через Settings -> DBMS Settings
4. Перезапустіть

Або скиньте пароль:
```bash
neo4j-admin set-initial-password neo4jneo4j
```

---

## 📊 Моніторинг

### MySQL:
```sql
SHOW PROCESSLIST;
SHOW STATUS;
```

### Redis:
```bash
redis-cli info
redis-cli monitor
```

### CouchDB:
```
http://localhost:5984/_utils/#/_all_dbs
```

### Neo4j:
```cypher
CALL dbms.listConnections();
:sysinfo
```

---

## 🔒 Безпека (для продакшену)

**Змініть паролі на більш безпечні!**

MySQL:
```sql
ALTER USER 'sport-complex-cw'@'127.0.0.1' IDENTIFIED BY 'strong_password_123!';
```

CouchDB:
```bash
curl -X PUT http://admin:admin@localhost:5984/_node/_local/_config/admins/newadmin -d '"newpassword"'
```

Neo4j:
```cypher
ALTER CURRENT USER SET PASSWORD FROM 'neo4jneo4j' TO 'new_secure_password';
```

---

## ✅ Контрольний список

- [ ] MySQL запущений і доступний на 127.0.0.1:3306
- [ ] База даних `sport-complex-cw` створена
- [ ] Користувач MySQL має права доступу
- [ ] Redis запущений на 127.0.0.1:6379
- [ ] CouchDB доступний на http://localhost:5984
- [ ] Neo4j запущений на bolt://localhost:7687
- [ ] Python 3.8+ встановлено
- [ ] Всі залежності встановлено (`pip install -r requirements.txt`)
- [ ] Програма запускається без помилок

---

## 📞 Корисні посилання

- MySQL: https://dev.mysql.com/doc/
- Redis: https://redis.io/documentation
- CouchDB: https://docs.couchdb.org/
- Neo4j: https://neo4j.com/docs/
- FastAPI: https://fastapi.tiangolo.com/
