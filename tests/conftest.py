"""
Конфігурація для PyTest - спільні фіксчури та налаштування
"""

import pytest
import json
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import subprocess
import time
import requests

# Додати кореневу директорію до path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from app.config import SessionLocal, Base, engine

# Frontend сервер процес (глобальна змінна)
frontend_process = None

@pytest.fixture(scope="session", autouse=True)
def setup_frontend_server():
    """Запустити фронтенд-сервер для Selenium тестів (опційно)"""
    global frontend_process
    
    # Перевірити чи сервер вже запущений
    try:
        response = requests.get("http://127.0.0.1:8001", timeout=1)
        if response.status_code in [200, 404]:
            print("✓ Frontend server already running on port 8001")
            yield
            return
    except:
        pass
    
    # Спробуємо запустити фронтенд-сервер
    try:
        serve_frontend_path = Path(__file__).parent.parent / "serve-frontend.py"
        if serve_frontend_path.exists():
            print("Starting frontend server on port 8001...")
            frontend_process = subprocess.Popen(
                [sys.executable, str(serve_frontend_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Чекаємо на запуск сервера
            for _ in range(30):
                try:
                    requests.get("http://127.0.0.1:8001", timeout=1)
                    print("✓ Frontend server is running")
                    break
                except:
                    time.sleep(0.2)
        else:
            print("⚠ serve-frontend.py not found, skipping frontend server")
    except Exception as e:
        print(f"⚠ Could not start frontend server: {e}")
    
    yield
    
    # Зупинити сервер після тестів
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
            print("✓ Frontend server stopped")
        except:
            frontend_process.kill()

# Клієнт для тестування
@pytest.fixture(scope="session")
def test_client():
    """Створити test client для всіх тестів"""
    # Очистити та переcrear базу даних для тестування
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db_session():
    """Отримати сессію БД для тестування"""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def admin_token(test_client):
    """Отримати токен адміністратора"""
    # Логін адміна (користувач уже існує в системі)
    response = test_client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    data = response.json()
    token = data.get("access_token")
    return token

@pytest.fixture
def user_token(test_client):
    """Отримати токен звичайного користувача"""
    # Логін користувача (користувач уже існує в системі)
    response = test_client.post("/auth/login", json={
        "username": "user",
        "password": "user123"
    })
    
    data = response.json()
    return data.get("access_token")

@pytest.fixture
def auth_headers(admin_token):
    """Заголовки з авторизацією для адміна"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    """Заголовки з авторизацією для користувача"""
    return {"Authorization": f"Bearer {user_token}"}
