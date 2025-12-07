#!/usr/bin/env python
"""Seed products into the database via API."""

import requests
import json

API_BASE = "http://127.0.0.1:8000"

# Login as admin to get token
def get_auth_token():
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    print(f"Login failed: {response.text}")
    return None

def add_product(token, article, name, category, supplier, price, quantity):
    """Add a product via API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "article": article,
        "name": name,
        "category_name": category,
        "supplier_name": supplier,
        "price": price,
        "quantity": quantity,
        "min_stock": 10,
        "delivery_days": 7
    }
    response = requests.post(
        f"{API_BASE}/products/",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        print(f"✓ Added: {name} ({article})")
        return True
    else:
        print(f"✗ Failed to add {name}: {response.status_code} - {response.text}")
        return False

def main():
    token = get_auth_token()
    if not token:
        print("Failed to authenticate. Make sure the API is running and admin/admin123 works.")
        return

    products = [
        ("SKU-DUMBBELL-5", "Гантель 5кг", "Спортивне обладнання", "SportGear", 450, 25),
        ("SKU-DUMBBELL-10", "Гантель 10кг", "Спортивне обладнання", "SportGear", 750, 20),
        ("SKU-BARBELL-20", "Штанга 20кг", "Спортивне обладнання", "SportGear", 2500, 10),
        ("SKU-YOGA-MAT", "Коврик для йоги", "Аксесуари", "SportGear", 350, 30),
        ("SKU-RESISTANCE-BAND", "Еластична стрічка", "Аксесуари", "SportGear", 120, 50),
        ("SKU-PULL-UP-BAR", "Турнік", "Спортивне обладнання", "SportGear", 600, 8),
        ("SKU-KETTLEBELL-8", "Гиря 8кг", "Спортивне обладнання", "SportGear", 520, 15),
        ("SKU-JUMP-ROPE", "Скакалка", "Аксесуари", "SportGear", 85, 60),
        ("SKU-FOAM-ROLLER", "Масажний валик", "Аксесуари", "SportGear", 280, 22),
        ("SKU-MEDICINE-BALL-4", "Медицинбол 4кг", "Спортивне обладнання", "SportGear", 420, 12),
    ]

    print("Adding products...")
    for article, name, category, supplier, price, qty in products:
        add_product(token, article, name, category, supplier, price, qty)

    print("\n✅ Product seeding complete!")

if __name__ == "__main__":
    main()
