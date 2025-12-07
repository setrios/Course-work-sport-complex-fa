"""
Тести для функціоналу е-комерції (товари, постачальники, категорії)
"""

import pytest


class TestSuppliers:
    """Тести управління постачальниками"""

    def test_create_supplier(self, test_client, auth_headers):
        """✅ Тест: Створити постачальника"""
        response = test_client.post("/suppliers/", headers=auth_headers, json={
            "name": "ООО Спортмаг",
            "city": "Київ",
            "country": "Україна",
            "contact_email": "info@sportmag.ua"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["name"] == "ООО Спортмаг"
        assert "id" in data

    def test_create_supplier_duplicate(self, test_client, auth_headers):
        """❌ Тест: Неможливо створити дублікат постачальника"""
        supplier_data = {
            "name": "Дублікатний постачальник",
            "city": "Львів",
            "country": "Україна",
            "contact_email": "dup@test.ua"
        }
        
        # Перша спроба
        test_client.post("/suppliers/", headers=auth_headers, json=supplier_data)
        
        # Друга спроба
        response = test_client.post("/suppliers/", headers=auth_headers, json=supplier_data)
        assert response.status_code == 409  # Conflict

    def test_list_suppliers(self, test_client, user_headers):
        """✅ Тест: Отримати список постачальників"""
        response = test_client.get("/suppliers/", headers=user_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_supplier_unauthorized(self, test_client, user_headers):
        """❌ Тест: Звичайний користувач не може створити постачальника"""
        response = test_client.post("/suppliers/", headers=user_headers, json={
            "name": "Неавторизований постачальник",
            "city": "Одеса",
            "country": "Україна",
            "contact_email": "unauth@test.ua"
        })
        assert response.status_code == 403


class TestCategories:
    """Тести управління категоріями товарів"""

    def test_create_category(self, test_client, auth_headers):
        """✅ Тест: Створити категорію товарів"""
        response = test_client.post("/categories/", headers=auth_headers, json={
            "name": "Гантелі та гирі"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Гантелі та гирі"

    def test_create_category_duplicate(self, test_client, auth_headers):
        """❌ Тест: Неможливо створити дублікат категорії"""
        category_name = "Йога"
        
        # Перша спроба
        test_client.post("/categories/", headers=auth_headers, json={"name": category_name})
        
        # Друга спроба
        response = test_client.post("/categories/", headers=auth_headers, json={"name": category_name})
        assert response.status_code == 409

    def test_create_category_unauthorized(self, test_client, user_headers):
        """❌ Тест: Звичайний користувач не може створити категорію"""
        response = test_client.post("/categories/", headers=user_headers, json={
            "name": "Інвентар"
        })
        assert response.status_code == 403


class TestProducts:
    """Тести управління товарами"""

    @pytest.fixture(autouse=True)
    def setup_data(self, test_client, auth_headers):
        """Підготувати дані для тестів"""
        # Створити категорію
        test_client.post("/categories/", headers=auth_headers, json={
            "name": "Спортивний інвентар"
        })
        
        # Створити постачальника
        test_client.post("/suppliers/", headers=auth_headers, json={
            "name": "GlobalSport",
            "city": "Київ",
            "country": "Україна",
            "contact_email": "global@sport.ua"
        })

    def test_create_product(self, test_client, auth_headers):
        """✅ Тест: Створити товар"""
        response = test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-001",
            "name": "Гантель 5кг",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 450.00,
            "quantity": 12,
            "min_stock": 5,
            "delivery_days": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["article"] == "SKU-001"
        assert "id" in data

    def test_create_product_duplicate_article(self, test_client, auth_headers):
        """❌ Тест: Неможливо створити товар з дублікатним артиклем"""
        product_data = {
            "article": "SKU-DUP",
            "name": "Дублікатний товар",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 100.00,
            "quantity": 10,
            "min_stock": 2,
            "delivery_days": 2
        }
        
        # Перша спроба
        test_client.post("/products/", headers=auth_headers, json=product_data)
        
        # Друга спроба
        response = test_client.post("/products/", headers=auth_headers, json=product_data)
        assert response.status_code == 409

    def test_create_product_negative_price(self, test_client, auth_headers):
        """❌ Тест: Неможливо створити товар з негативною ціною"""
        response = test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-NEG",
            "name": "Помилковий товар",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": -50.00,
            "quantity": 5,
            "min_stock": 1,
            "delivery_days": 1
        })
        assert response.status_code == 400

    def test_create_product_negative_quantity(self, test_client, auth_headers):
        """❌ Тест: Неможливо створити товар з негативною кількістю"""
        response = test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-NEG-QTY",
            "name": "Помилковий товар",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 50.00,
            "quantity": -5,
            "min_stock": 1,
            "delivery_days": 1
        })
        assert response.status_code == 400

    def test_list_products_assortment(self, test_client, user_headers):
        """✅ Тест: Отримати асортимент товарів"""
        response = test_client.get("/products/assortment", headers=user_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_product(self, test_client, auth_headers, user_headers):
        """✅ Тест: Пошук товару за назвою"""
        # Створити товар
        test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-SEARCH",
            "name": "Тестовий товар для пошуку",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 100.00,
            "quantity": 5,
            "min_stock": 1,
            "delivery_days": 2
        })
        
        # Шукати товар
        response = test_client.get("/products/search/Тестовий", headers=user_headers)
        assert response.status_code == 200

    def test_product_stock_extremes(self, test_client, auth_headers, user_headers):
        """✅ Тест: Отримати товари з екстремальними запасами"""
        # Створити товари з різними кількостями
        test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-MIN",
            "name": "Мінімальний запас",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 100.00,
            "quantity": 1,
            "min_stock": 5,
            "delivery_days": 1
        })
        
        test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-MAX",
            "name": "Максимальний запас",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 100.00,
            "quantity": 1000,
            "min_stock": 5,
            "delivery_days": 1
        })
        
        # Отримати екстремальні товари
        response = test_client.get("/products/stock-extremes", headers=user_headers)
        assert response.status_code == 200

    def test_product_by_article(self, test_client, auth_headers, user_headers):
        """✅ Тест: Отримати товар за артиклем"""
        # Створити товар
        test_client.post("/products/", headers=auth_headers, json={
            "article": "SKU-BY-ARTICLE",
            "name": "Товар за артиклем",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 100.00,
            "quantity": 5,
            "min_stock": 1,
            "delivery_days": 2
        })
        
        # Отримати товар
        response = test_client.get("/products/by-article/SKU-BY-ARTICLE", headers=user_headers)
        assert response.status_code == 200

    def test_create_product_unauthorized(self, test_client, user_headers):
        """❌ Тест: Звичайний користувач не може створити товар"""
        response = test_client.post("/products/", headers=user_headers, json={
            "article": "SKU-UNAUTH",
            "name": "Неавторизований товар",
            "category_name": "Спортивний інвентар",
            "supplier_name": "GlobalSport",
            "price": 100.00,
            "quantity": 5,
            "min_stock": 1,
            "delivery_days": 2
        })
        assert response.status_code == 403
