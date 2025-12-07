"""
Тести для системи аутентифікації
"""

import pytest


class TestAuthentication:
    """Тести реєстрації, логіну та авторизації"""

    def test_health_check(self, test_client):
        """✅ Тест: Сервер живий і відповідає"""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_register_success(self, test_client):
        """✅ Тест: Успішна реєстрація користувача"""
        response = test_client.post("/auth/register", json={
            "username": "newuser",
            "password": "password123",
            "email": "newuser@test.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "user"

    def test_register_duplicate_username(self, test_client):
        """❌ Тест: Реєстрація з дублікатним ім'ям користувача"""
        # Перша реєстрація
        test_client.post("/auth/register", json={
            "username": "duplicate_user",
            "password": "password123",
            "email": "user1@test.com"
        })
        
        # Друга спроба з тим же ім'ям
        response = test_client.post("/auth/register", json={
            "username": "duplicate_user",
            "password": "password456",
            "email": "user2@test.com"
        })
        assert response.status_code == 400  # Bad Request

    def test_login_success(self, test_client):
        """✅ Тест: Успішний логін"""
        # Реєстрація
        test_client.post("/auth/register", json={
            "username": "loginuser",
            "password": "password123",
            "email": "loginuser@test.com"
        })
        
        # Логін
        response = test_client.post("/auth/login", json={
            "username": "loginuser",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"

    def test_login_wrong_password(self, test_client):
        """❌ Тест: Логін з неправильним паролем"""
        # Реєстрація
        test_client.post("/auth/register", json={
            "username": "testuser",
            "password": "correct_password",
            "email": "testuser@test.com"
        })
        
        # Спроба логіну з неправильним паролем
        response = test_client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrong_password"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, test_client):
        """❌ Тест: Логін користувача, що не існує"""
        response = test_client.post("/auth/login", json={
            "username": "nonexistent_user",
            "password": "password123"
        })
        assert response.status_code == 401  # Unauthorized (invalid credentials)

    def test_me_with_token(self, test_client, user_token):
        """✅ Тест: Отримати дані поточного користувача"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = test_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "user"
        assert data["role"] == "user"

    def test_me_without_token(self, test_client):
        """❌ Тест: Доступ до /auth/me без токена"""
        response = test_client.get("/auth/me")
        assert response.status_code == 401  # Unauthorized (missing token)

    def test_logout(self, test_client, user_token):
        """✅ Тест: Логаут користувача"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = test_client.post("/auth/logout", headers=headers)
        assert response.status_code == 200
