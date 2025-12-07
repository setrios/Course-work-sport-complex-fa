"""
Тести для Database Query API (адмін запити до БД)
"""

import pytest


class TestDatabaseQueries:
    """Тести для передових запитів до БД для адміністраторів"""

    @pytest.fixture(autouse=True)
    def setup_data(self, test_client, auth_headers):
        """Підготувати дані для тестів"""
        # Створити категорію
        test_client.post("/categories/", headers=auth_headers, json={
            "name": "Тестова категорія"
        })
        
        # Створити постачальника
        test_client.post("/suppliers/", headers=auth_headers, json={
            "name": "TestSupplier",
            "city": "Київ",
            "country": "Україна",
            "contact_email": "test@supplier.ua"
        })
        
        # Створити товари
        for i in range(3):
            test_client.post("/products/", headers=auth_headers, json={
                "article": f"SKU-QRY-{i:03d}",
                "name": f"Тестовий товар {i+1}",
                "category_name": "Тестова категорія",
                "supplier_name": "TestSupplier",
                "price": 100.00 + (i * 50),
                "quantity": 10 + (i * 5),
                "min_stock": 2,
                "delivery_days": 2
            })

    def test_query_products_images(self, test_client, auth_headers):
        """✅ Тест: Запит зображень товарів"""
        response = test_client.get("/db/products/images", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "products" in data
        assert isinstance(data["products"], list)

    def test_query_products_images_unauthorized(self, test_client, user_headers):
        """❌ Тест: Звичайний користувач не може виконати запит до БД"""
        response = test_client.get("/db/products/images", headers=user_headers)
        assert response.status_code == 403

    def test_query_assortment(self, test_client, auth_headers):
        """✅ Тест: Запит асортименту товарів"""
        response = test_client.get("/db/assortment", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "assortment" in data
        assert isinstance(data["assortment"], list)

    def test_query_price_availability(self, test_client, auth_headers):
        """✅ Тест: Запит матриці ціни та доступності"""
        response = test_client.get("/db/price-availability", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "price_matrix" in data
        
        # Перевірити структуру товарів
        for product in data["price_matrix"]:
            assert "article" in product
            assert "name" in product
            assert "price" in product
            assert "quantity" in product
            assert "status" in product
            assert product["status"] in ["In Stock", "Low Stock"]

    def test_query_min_max_products(self, test_client, auth_headers):
        """✅ Тест: Запит мін/макс товарів"""
        response = test_client.get("/db/min-max-products", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "min_products" in data
        assert "max_products" in data
        assert isinstance(data["min_products"], list)
        assert isinstance(data["max_products"], list)

    def test_query_suppliers(self, test_client, auth_headers):
        """✅ Тест: Запит постачальників"""
        response = test_client.get("/db/suppliers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "suppliers" in data
        assert isinstance(data["suppliers"], list)
        
        # Перевірити наявність тестового постачальника
        suppliers = data["suppliers"]
        assert len(suppliers) > 0

    def test_query_inventory_history(self, test_client, auth_headers):
        """✅ Тест: Запит історії запасів"""
        response = test_client.get("/db/inventory-history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "history" in data
        assert isinstance(data["history"], list)

    def test_query_inventory_history_by_article(self, test_client, auth_headers):
        """✅ Тест: Запит історії запасів за артиклем"""
        response = test_client.get("/db/inventory-history?article=SKU-QRY-000", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "history" in data

    def test_query_inventory_history_nonexistent(self, test_client, auth_headers):
        """❌ Тест: Запит історії для неіснуючого товару"""
        response = test_client.get(
            "/db/inventory-history?article=SKU-NONEXISTENT",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # API повертає помилку якщо товар не знайдено
        assert "history" in data or "message" in data or "error" in data

    def test_generate_order(self, test_client, auth_headers):
        """✅ Тест: Генерація ділового листа замовлення"""
        response = test_client.post("/db/generate-order", headers=auth_headers, json={
            "product_id": "SKU-QRY-000",
            "quantity": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "generated"
        assert "order" in data
        
        order = data["order"]
        assert order["article"] == "SKU-QRY-000"
        assert order["quantity"] == 10
        assert "total_price" in order
        assert "supplier" in order

    def test_generate_order_nonexistent_product(self, test_client, auth_headers):
        """❌ Тест: Генерація замовлення для неіснуючого товару"""
        response = test_client.post("/db/generate-order", headers=auth_headers, json={
            "product_id": "SKU-NONEXISTENT",
            "quantity": 5
        })
        assert response.status_code in [200, 404]
        data = response.json()
        # Може бути успішна відповідь з помилкою або код 404
        assert "status" in data or "message" in data

    def test_db_queries_no_auth(self, test_client):
        """❌ Тест: DB запити без авторизації (no token)"""
        endpoints = [
            "/db/products/images",
            "/db/assortment",
            "/db/price-availability",
            "/db/min-max-products",
            "/db/suppliers",
            "/db/inventory-history"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            # API повертає 401 якщо немає токена, 403 якщо користувач не адмін
            assert response.status_code in [401, 403]
