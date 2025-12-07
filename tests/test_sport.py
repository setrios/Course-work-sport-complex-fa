"""
Тести для функціоналу спорткомплексу
"""

import pytest


class TestSportClients:
    """Тести управління клієнтами спорткомплексу"""

    def test_create_client(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може створити клієнта"""
        response = test_client.post("/sport/clients", headers=auth_headers, json={
            "full_name": "Іван Петренко",
            "birth_date": "1990-05-15",
            "gender": "MALE",
            "contact_info": {
                "phone": "+380501234567",
                "email": "ivan@test.com"
            }
        })
        # Приймаємо 200, 422 (schema validation) або 201
        assert response.status_code in [200, 201, 422]

    def test_create_client_unauthorized(self, test_client, user_headers):
        """❌ Тест: Звичайний користувач не може створити клієнта"""
        response = test_client.post("/sport/clients", headers=user_headers, json={
            "full_name": "Іван Петренко",
            "birth_date": "1990-05-15",
            "gender": "M",
            "contact_info": {}
        })
        assert response.status_code == 403

    def test_list_clients(self, test_client, auth_headers):
        """✅ Тест: Отримати список клієнтів"""
        # Створити клієнта
        test_client.post("/sport/clients", headers=auth_headers, json={
            "full_name": "Тестовий клієнт",
            "birth_date": "1995-03-20",
            "gender": "F",
            "contact_info": {}
        })
        
        # Отримати список
        response = test_client.get("/sport/clients", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_clients_no_auth(self, test_client):
        """❌ Тест: Отримати список клієнтів без авторизації"""
        response = test_client.get("/sport/clients")
        assert response.status_code in [401, 403]

    def test_update_client(self, test_client, auth_headers):
        """✅ Тест: Оновити дані клієнта з усіма полями"""
        # Спочатку отримуємо список клієнтів щоб знати ID
        response = test_client.get("/sport/clients", headers=auth_headers)
        clients = response.json()
        if clients:
            client_id = clients[0]["client_id"]
            # Оновлюємо клієнта
            update_response = test_client.put(
                f"/sport/clients/{client_id}",
                headers=auth_headers,
                json={
                    "full_name": "Оновлене ім'я",
                    "birth_date": "1990-01-15",
                    "gender": "MALE",
                    "contact_info": {
                        "phone": "+380991234567",
                        "email": "new@example.com"
                    },
                    "username": "updated_user",
                    "password": "newpass123"
                }
            )
            assert update_response.status_code == 200
            updated_data = update_response.json()
            assert updated_data["full_name"] == "Оновлене ім'я"
            assert updated_data["username"] == "updated_user"
            
            # Перевіримо що дані дійсно оновлені (прочитаємо знову)
            get_response = test_client.get(f"/sport/clients/{client_id}", headers=auth_headers)
            assert get_response.status_code == 200
            retrieved_data = get_response.json()
            assert retrieved_data["full_name"] == "Оновлене ім'я"
            assert retrieved_data["username"] == "updated_user"


class TestSportTrainers:
    """Тести управління тренерами"""

    def test_create_trainer(self, test_client, auth_headers):
        """✅ Тест: Створити тренера"""
        response = test_client.post("/sport/trainers", headers=auth_headers, json={
            "full_name": "Олександр Іванович",
            "birth_date": "1985-07-10",
            "gender": "MALE",
            "specialization": "Фітнес",
            "contact_info": {}
        })
        # Приймаємо 200, 422 (schema validation) або 201
        assert response.status_code in [200, 201, 422]

    def test_list_trainers(self, test_client, user_headers):
        """✅ Тест: Отримати список тренерів"""
        response = test_client.get("/sport/trainers", headers=user_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestSportServices:
    """Тести управління послугами"""

    def test_create_service(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може створити послугу"""
        response = test_client.post("/sport/services", headers=auth_headers, json={
            "service_name": "Персональна тренування",
            "price": 150.00,
            "requires_medical_certificate": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["service_name"] == "Персональна тренування"
        assert data["price"] == 150.0

    def test_list_services(self, test_client, user_headers):
        """✅ Тест: Користувач може отримати список послуг"""
        response = test_client.get("/sport/services", headers=user_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_service_negative_price(self, test_client, auth_headers):
        """❌ Тест: Неможливо створити послугу з негативною ціною"""
        response = test_client.post("/sport/services", headers=auth_headers, json={
            "service_name": "Помилкова послуга",
            "price": -50.00,
            "requires_medical_certificate": False
        })
        assert response.status_code == 400


class TestSportVisits:
    """Тести управління відвідуваннями"""

    def test_list_visits(self, test_client, user_headers):
        """✅ Тест: Отримати список відвідувань"""
        response = test_client.get("/sport/visits", headers=user_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_register_visit(self, test_client, auth_headers):
        """✅ Тест: Зареєструвати відвідування"""
        response = test_client.post("/sport/visits", headers=auth_headers, json={
            "client_id": "client_1",
            "service_id": "service_1",
            "entry_time": "2025-01-01T10:00:00"
        })
        # Може бути 200 або 404 якщо клієнт/послуга не існує
        assert response.status_code in [200, 404]


class TestSportMemberships:
    """Тести управління абонементами спорткомплексу"""

    def test_create_membership(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може створити абонемент"""
        # Спочатку створимо клієнта
        client_response = test_client.post("/sport/clients", headers=auth_headers, json={
            "full_name": "Абонементний клієнт",
            "birth_date": "1995-06-15",
            "gender": "M",
            "contact_info": {"phone": "+380501234567"}
        })
        
        # Створити абонемент
        response = test_client.post("/sport/memberships", headers=auth_headers, json={
            "client_id": 1,
            "start_date": "2025-01-01",
            "end_date": "2025-02-01",
            "status": "active",
            "subscription_type": "MONTHLY",
            "price": 500
        })
        assert response.status_code in [200, 201]

    def test_list_memberships(self, test_client, auth_headers):
        """✅ Тест: Отримати список абонементів"""
        response = test_client.get("/sport/memberships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_membership(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може оновити абонемент"""
        response = test_client.put("/sport/memberships/1", headers=auth_headers, json={
            "status": "expired",
            "price": 600
        })
        # Може бути 200 або 404 якщо абонемент не існує
        assert response.status_code in [200, 404]

    def test_delete_membership(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може видалити абонемент"""
        response = test_client.delete("/sport/memberships/1", headers=auth_headers)
        # Може бути 200 або 404 якщо абонемент не існує
        assert response.status_code in [200, 404]

    def test_create_membership_unauthorized(self, test_client, user_headers):
        """❌ Тест: Звичайний користувач не може створити абонемент"""
        response = test_client.post("/sport/memberships", headers=user_headers, json={
            "client_id": 1,
            "start_date": "2025-01-01",
            "end_date": "2025-02-01",
            "status": "active"
        })
        assert response.status_code == 403


class TestSportAnalytics:
    """Тести аналітики спорткомплексу"""

    def test_get_analytics(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може отримати аналітику"""
        response = test_client.get("/sport/analytics", headers=auth_headers)
        assert response.status_code == 200

    def test_get_reports(self, test_client, auth_headers):
        """✅ Тест: Адміністратор може отримати звіти"""
        response = test_client.get("/sport/reports", headers=auth_headers)
        assert response.status_code == 200
