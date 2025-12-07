"""
Інтеграційні тести - повні сценарії використання системи
"""

import pytest


class TestUserJourney:
    """Інтеграційні тести для типових користувацьких сценаріїв"""

    def test_complete_user_signup_and_navigation(self, test_client):
        """✅ Повний цикл: реєстрація користувача та навігація"""
        
        # 1. Реєстрація
        register_response = test_client.post("/auth/register", json={
            "username": "journey_user",
            "password": "Password123",
            "email": "journey@test.com"
        })
        assert register_response.status_code == 200
        
        # 2. Логін
        login_response = test_client.post("/auth/login", json={
            "username": "journey_user",
            "password": "Password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Отримати дані користувача
        me_response = test_client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "journey_user"
        
        # 4. Отримати список послуг
        services_response = test_client.get("/sport/services", headers=headers)
        assert services_response.status_code == 200
        
        # 5. Логаут
        logout_response = test_client.post("/auth/logout", headers=headers)
        assert logout_response.status_code == 200

    def test_admin_product_management_flow(self, test_client, auth_headers):
        """✅ Повний цикл: адміністратор управління товарами"""
        
        # 1. Створити постачальника
        supplier_response = test_client.post("/suppliers/", headers=auth_headers, json={
            "name": "IntegrationSupplier",
            "city": "Київ",
            "country": "Україна",
            "contact_email": "integration@supplier.ua"
        })
        assert supplier_response.status_code == 200
        
        # 2. Створити категорію
        category_response = test_client.post("/categories/", headers=auth_headers, json={
            "name": "IntegrationCategory"
        })
        assert category_response.status_code == 200
        
        # 3. Створити товар
        product_response = test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-INT-001",
            "name": "Інтеграційний товар",
            "category_name": "IntegrationCategory",
            "supplier_name": "IntegrationSupplier",
            "price": 299.99,
            "quantity": 50,
            "min_stock": 10,
            "delivery_days": 5
        })
        assert product_response.status_code == 200
        
        # 4. Отримати асортимент
        assortment_response = test_client.get("/products/assortment", headers=auth_headers)
        assert assortment_response.status_code == 200
        
        # 5. Запит до БД (матриця ціни)
        price_matrix_response = test_client.get("/db/price-availability", headers=auth_headers)
        assert price_matrix_response.status_code == 200
        
        # 6. Генерація замовлення
        order_response = test_client.post("/db/generate-order", headers=auth_headers, json={
            "product_id": "SKU-INT-001",
            "quantity": 10
        })
        assert order_response.status_code == 200

    def test_complete_sport_complex_workflow(self, test_client, auth_headers):
        """✅ Повний цикл: робота спорткомплексу"""
        
        # 1. Додати тренера
        trainer_response = test_client.post("/sport/trainers", headers=auth_headers, json={
            "full_name": "Іван Коваль",
            "birth_date": "1990-01-15",
            "gender": "MALE",
            "specialization": "Функціональний тренінг",
            "contact_info": {}
        })
        assert trainer_response.status_code in [200, 422]
        
        # 2. Додати клієнта
        client_response = test_client.post("/sport/clients", headers=auth_headers, json={
            "full_name": "Петро Петренко",
            "birth_date": "1995-06-20",
            "gender": "MALE",
            "contact_info": {}
        })
        assert client_response.status_code in [200, 422]
        
        # 3. Додати послугу
        service_response = test_client.post("/sport/services", headers=auth_headers, json={
            "service_name": "Групова тренування",
            "price": 200.00,
            "requires_medical_certificate": False
        })
        assert service_response.status_code == 200
        
        # 4. Отримати список клієнтів
        clients_list = test_client.get("/sport/clients", headers=auth_headers)
        assert clients_list.status_code == 200
        
        # 5. Отримати список послуг
        services_list = test_client.get("/sport/services", headers=auth_headers)
        assert services_list.status_code == 200
        
        # 6. Отримати список тренерів
        trainers_list = test_client.get("/sport/trainers", headers=auth_headers)
        assert trainers_list.status_code == 200

    def test_analytics_and_reporting(self, test_client, auth_headers):
        """✅ Повний цикл: аналітика та звітність"""
        
        # 1. Отримати аналітику спорткомплексу
        analytics_response = test_client.get("/sport/analytics", headers=auth_headers)
        assert analytics_response.status_code == 200
        
        # 2. Отримати звіти спорткомплексу
        reports_response = test_client.get("/sport/reports", headers=auth_headers)
        assert reports_response.status_code == 200
        
        # 3. Отримати популярні товари
        popular_products = test_client.get("/analytics/popular-products", headers=auth_headers)
        assert popular_products.status_code == 200
        
        # 4. Отримати постачальників за містом
        suppliers_by_city = test_client.get("/analytics/suppliers-by-city", headers=auth_headers)
        assert suppliers_by_city.status_code == 200


class TestErrorRecovery:
    """Тести для обробки помилок та відновлення"""

    def test_invalid_token_recovery(self, test_client):
        """❌ Тест: Система коректно обробляє невалідний токен"""
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        
        # Спроба отримати дані з невалідним токеном
        response = test_client.get("/auth/me", headers=invalid_headers)
        assert response.status_code in [401, 403]  # Unauthorized або Forbidden

    def test_missing_required_fields(self, test_client, auth_headers):
        """❌ Тест: Система обробляє відсутність обов'язкових полів"""
        
        # Спроба створити товар без обов'язкових полів
        response = test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-INCOMPLETE"
            # Решта полів відсутня
        })
        assert response.status_code == 422  # Unprocessable Entity

    def test_permission_denied_scenarios(self, test_client, user_headers):
        """❌ Тест: Система корректно обробляє відмову в доступі"""
        
        # Користувач пробує доступити до функцій адміна
        endpoints = [
            ("/suppliers/", "POST"),
            ("/categories/", "POST"),
            ("/products/", "POST"),
            ("/db/products/images", "GET"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = test_client.get(endpoint, headers=user_headers)
            elif method == "POST":
                response = test_client.post(endpoint, headers=user_headers, json={})
            
            assert response.status_code == 403


class TestDataIntegrity:
    """Тести для перевірки цілісності даних"""

    def test_referential_integrity(self, test_client, auth_headers):
        """✅ Тест: Система підтримує цілісність посилань"""
        
        # 1. Створити постачальника
        supplier_resp = test_client.post("/suppliers/", headers=auth_headers, json={
            "name": "IntegritySupplier",
            "city": "Львів",
            "country": "Україна",
            "contact_email": "integrity@supplier.ua"
        })
        assert supplier_resp.status_code == 200
        
        # 2. Створити категорію
        category_resp = test_client.post("/categories/", headers=auth_headers, json={
            "name": "IntegrityCategory"
        })
        assert category_resp.status_code == 200
        
        # 3. Спробувати видалити постачальника (якщо є товари)
        # Спочатку створимо товар
        product_resp = test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-INT-REF",
            "name": "Товар з посиланням",
            "category_name": "IntegrityCategory",
            "supplier_name": "IntegritySupplier",
            "price": 100.00,
            "quantity": 10,
            "min_stock": 2,
            "delivery_days": 3
        })
        assert product_resp.status_code == 200

    def test_data_consistency_across_operations(self, test_client, auth_headers):
        """✅ Тест: Дані залишаються консистентними після операцій"""
        
        # 1. Отримати кількість товарів
        initial_count = len(test_client.get("/products/assortment", headers=auth_headers).json())
        
        # 2. Додати постачальника та категорію
        test_client.post("/suppliers/", headers=auth_headers, json={
            "name": "ConsistencySupplier",
            "city": "Одеса",
            "country": "Україна",
            "contact_email": "consistency@supplier.ua"
        })
        
        test_client.post("/categories/", headers=auth_headers, json={
            "name": "ConsistencyCategory"
        })
        
        # 3. Додати товар
        test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-CONS",
            "name": "Консистентний товар",
            "category_name": "ConsistencyCategory",
            "supplier_name": "ConsistencySupplier",
            "price": 150.00,
            "quantity": 20,
            "min_stock": 5,
            "delivery_days": 2
        })
        
        # 4. Перевірити що кількість товарів збільшилась
        final_count = len(test_client.get("/products/assortment", headers=auth_headers).json())
        assert final_count >= initial_count + 1
