from __future__ import annotations

import json
from datetime import datetime, date
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import REDIS_TTL_PRODUCTS, REDIS_TTL_SUPPLIERS, db_couch, neo4j_driver, redis_client, sport_system
from app.db_models import CategoryDB, OrderItemDB, OrderDB, ProductDB, SupplierDB
from app.sport_store import SportStore
from sport_complex import ContactInfo


class SupplierService:
    def create(self, db: Session, name: str, city: str, country: str, email: str) -> dict:
        """Create new supplier with validation."""
        if not name or not name.strip():
            raise ValueError("Supplier name is required")
        if not email or not email.strip():
            raise ValueError("Email is required")
        
        exists = db.query(SupplierDB).filter(SupplierDB.name == name).first()
        if exists:
            raise ValueError(f"Supplier '{name}' already exists")
        
        supplier = SupplierDB(name=name, city=city, country=country, contact_email=email)
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        
        # Create in Neo4j
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

    def list(self, db: Session) -> List[dict]:
        """Get all suppliers from cache or database."""
        cached = redis_client.get("all_suppliers")
        if cached:
            return json.loads(cached)
        
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
        redis_client.setex("all_suppliers", REDIS_TTL_SUPPLIERS, json.dumps(result))
        return result


class CategoryService:
    def create(self, db: Session, name: str) -> dict:
        """Create new category with validation."""
        if not name or not name.strip():
            raise ValueError("Category name is required")
        
        exists = db.query(CategoryDB).filter(CategoryDB.name == name).first()
        if exists:
            raise ValueError(f"Category '{name}' already exists")
        
        category = CategoryDB(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
        
        # Create in Neo4j
        with neo4j_driver.session() as session:
            session.run("MERGE (c:Category {name: $name})", name=category.name)
        
        return {"status": "created", "id": category.id, "name": category.name}


class ProductService:
    def create(self, db: Session, payload) -> dict:
        """Create new product with comprehensive validation."""
        category = db.query(CategoryDB).filter(CategoryDB.name == payload.category_name).first()
        supplier = db.query(SupplierDB).filter(SupplierDB.name == payload.supplier_name).first()
        
        if not category:
            raise ValueError(f"Category '{payload.category_name}' not found")
        if not supplier:
            raise ValueError(f"Supplier '{payload.supplier_name}' not found")
        
        existing_product = db.query(ProductDB).filter(ProductDB.article == payload.article).first()
        if existing_product:
            raise ValueError(f"Product with article '{payload.article}' already exists")
        
        # Validate numeric fields
        if payload.price < 0:
            raise ValueError("Price must be non-negative")
        if payload.quantity < 0:
            raise ValueError("Quantity must be non-negative")
        if payload.min_stock < 0:
            raise ValueError("Minimum stock must be non-negative")
        if payload.delivery_days < 0:
            raise ValueError("Delivery days must be non-negative")
        
        # Validate required fields
        if not payload.article or not payload.article.strip():
            raise ValueError("Product article is required")
        if not payload.name or not payload.name.strip():
            raise ValueError("Product name is required")
        
        price_kopiyky = int(round(payload.price * 100))
        product = ProductDB(
            article=payload.article,
            name=payload.name,
            category_id=category.id,
            supplier_id=supplier.id,
            price=price_kopiyky,
            quantity=payload.quantity,
            min_stock=payload.min_stock,
            delivery_days=payload.delivery_days,
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Create in Neo4j
        with neo4j_driver.session() as session:
            session.run(
                "MERGE (p:Product {mysql_id: $pid, article: $article, name: $name})",
                pid=product.id,
                article=product.article,
                name=product.name,
            )
            session.run(
                """
                MATCH (p:Product {mysql_id: $pid})
                MATCH (c:Category {name: $cat})
                MERGE (p)-[:BELONGS_TO]->(c)
                """,
                pid=product.id,
                cat=category.name,
            )
            session.run(
                """
                MATCH (p:Product {mysql_id: $pid})
                MATCH (s:Supplier {mysql_id: $sid})
                MERGE (s)-[:SUPPLIES]->(p)
                """,
                pid=product.id,
                sid=supplier.id,
            )

        redis_client.delete("product_list")
        return {"status": "created", "id": product.id, "article": product.article}

    def list(self, db: Session, query_params=None) -> dict:
        """List products with pagination, filtering, and sorting."""
        # Build base query
        base_query = db.query(ProductDB)
        
        # Apply filters if query_params provided
        if query_params:
            if query_params.category:
                category = db.query(CategoryDB).filter(CategoryDB.name == query_params.category).first()
                if category:
                    base_query = base_query.filter(ProductDB.category_id == category.id)
            
            if query_params.supplier:
                supplier = db.query(SupplierDB).filter(SupplierDB.name == query_params.supplier).first()
                if supplier:
                    base_query = base_query.filter(ProductDB.supplier_id == supplier.id)
            
            if query_params.min_price is not None:
                base_query = base_query.filter(ProductDB.price >= int(query_params.min_price * 100))
            
            if query_params.max_price is not None:
                base_query = base_query.filter(ProductDB.price <= int(query_params.max_price * 100))
            
            if query_params.in_stock:
                base_query = base_query.filter(ProductDB.quantity > 0)
            
            if query_params.search:
                base_query = base_query.filter(ProductDB.name.like(f"%{query_params.search}%"))
            
            # Apply sorting
            sort_column = ProductDB.name
            if query_params.sort_by == "price":
                sort_column = ProductDB.price
            elif query_params.sort_by == "quantity":
                sort_column = ProductDB.quantity
            
            if query_params.sort_order == "desc":
                base_query = base_query.order_by(sort_column.desc())
            else:
                base_query = base_query.order_by(sort_column.asc())
            
            # Get total count before pagination
            total = base_query.count()
            
            # Apply pagination
            offset = (query_params.page - 1) * query_params.page_size
            products = base_query.offset(offset).limit(query_params.page_size).all()
            
            result = [
                {
                    "article": p.article,
                    "name": p.name,
                    "quantity": p.quantity,
                    "price_uah": p.price / 100.0,
                    "category": p.category.name if p.category else None,
                    "supplier": p.supplier.name if p.supplier else None,
                }
                for p in products
            ]
            
            return {
                "items": result,
                "total": total,
                "page": query_params.page,
                "page_size": query_params.page_size,
                "total_pages": (total + query_params.page_size - 1) // query_params.page_size,
            }
        else:
            # Legacy behavior without pagination
            cached = redis_client.get("product_list")
            if cached:
                return json.loads(cached)
            products = db.query(ProductDB).all()
            result = [
                {
                    "article": p.article,
                    "name": p.name,
                    "quantity": p.quantity,
                    "price_uah": p.price / 100.0,
                }
                for p in products
            ]
            redis_client.setex("product_list", REDIS_TTL_PRODUCTS, json.dumps(result))
            return result

    def search(self, db: Session, name_query: str) -> List[dict]:
        """Search products by name."""
        if not name_query or not name_query.strip():
            raise ValueError("Search query is required")
        
        products = db.query(ProductDB).filter(ProductDB.name.like(f"%{name_query}%")).all()
        if not products:
            raise ValueError(f"No products found for query '{name_query}'")
        
        return [
            {
                "article": p.article,
                "name": p.name,
                "quantity": p.quantity,
                "price_uah": p.price / 100.0,
                "supplier": p.supplier.name if p.supplier else "N/A",
                "delivery_days": p.delivery_days,
            }
            for p in products
        ]

    def stock_extremes(self, db: Session) -> dict:
        """Get min and max stock products."""
        min_product = db.query(ProductDB).order_by(ProductDB.quantity.asc()).first()
        max_product = db.query(ProductDB).order_by(ProductDB.quantity.desc()).first()
        return {
            "minimum": {
                "article": min_product.article,
                "name": min_product.name,
                "quantity": min_product.quantity
            } if min_product else None,
            "maximum": {
                "article": max_product.article,
                "name": max_product.name,
                "quantity": max_product.quantity
            } if max_product else None,
        }

    def by_article(self, db: Session, article: str) -> dict:
        """Get product by article."""
        if not article or not article.strip():
            raise ValueError("Article is required")
        
        product = db.query(ProductDB).filter(ProductDB.article == article).first()
        if not product:
            raise ValueError(f"Product with article '{article}' not found")
        
        return {
            "article": product.article,
            "name": product.name,
            "quantity": product.quantity,
            "price_uah": product.price / 100.0,
            "delivery_days": product.delivery_days,
            "supplier": product.supplier.name if product.supplier else "N/A",
            "category": product.category.name if product.category else "N/A",
        }

    def upload_image(self, db: Session, article: str, image_base64: str, mime_type: str) -> dict:
        """Upload product image to CouchDB."""
        if not db_couch:
            raise ValueError("CouchDB is not available")
        
        if not article or not article.strip():
            raise ValueError("Article is required")
        
        product = db.query(ProductDB).filter(ProductDB.article == article).first()
        if not product:
            raise ValueError(f"Product with article '{article}' not found")
        
        if not image_base64 or not image_base64.strip():
            raise ValueError("Image data (base64) is required")
        
        document = {
            "type": "product_image",
            "article": article,
            "product_name": product.name,
            "mime_type": mime_type,
            "image_base64": image_base64,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        try:
            doc_id, _ = db_couch.save(document)
            product.image_doc_id = doc_id
            db.commit()
            return {"status": "uploaded", "couchdb_id": doc_id, "article": article}
        except Exception as e:
            raise ValueError(f"Failed to upload image: {str(e)}")

    def get_image(self, db: Session, article: str) -> dict:
        """Get product image from CouchDB."""
        if not db_couch:
            raise ValueError("CouchDB is not available")
        
        if not article or not article.strip():
            raise ValueError("Article is required")
        
        product = db.query(ProductDB).filter(ProductDB.article == article).first()
        if not product or not product.image_doc_id:
            raise ValueError(f"No image found for product '{article}'")
        
        try:
            doc = db_couch[product.image_doc_id]
            return {
                "article": article,
                "mime_type": doc.get("mime_type", "image/jpeg"),
                "image_base64": doc.get("image_base64", ""),
                "uploaded_at": doc.get("uploaded_at"),
            }
        except Exception as e:
            raise ValueError(f"Failed to retrieve image: {str(e)}")

    def update(self, db: Session, article: str, payload) -> dict:
        """Update an existing product."""
        product = db.query(ProductDB).filter(ProductDB.article == article).first()
        if not product:
            raise ValueError(f"Product with article '{article}' not found")
        
        # Validate and get category/supplier
        category = db.query(CategoryDB).filter(CategoryDB.name == payload.category_name).first()
        supplier = db.query(SupplierDB).filter(SupplierDB.name == payload.supplier_name).first()
        
        if not category:
            raise ValueError(f"Category '{payload.category_name}' not found")
        if not supplier:
            raise ValueError(f"Supplier '{payload.supplier_name}' not found")
        
        # Validate numeric fields
        if payload.price < 0:
            raise ValueError("Price must be non-negative")
        if payload.quantity < 0:
            raise ValueError("Quantity must be non-negative")
        
        # Update product
        product.name = payload.name
        product.category_id = category.id
        product.supplier_id = supplier.id
        product.price = int(round(payload.price * 100))
        product.quantity = payload.quantity
        product.min_stock = payload.min_stock
        product.delivery_days = payload.delivery_days
        
        db.commit()
        db.refresh(product)
        
        # Update Neo4j
        with neo4j_driver.session() as session:
            session.run(
                "MATCH (p:Product {mysql_id: $pid}) SET p.name = $name",
                pid=product.id,
                name=product.name
            )
        
        redis_client.delete("product_list")
        return {"status": "updated", "article": product.article, "name": product.name}

    def delete(self, db: Session, article: str) -> dict:
        """Delete a product."""
        product = db.query(ProductDB).filter(ProductDB.article == article).first()
        if not product:
            raise ValueError(f"Product with article '{article}' not found")
        
        product_name = product.name
        product_id = product.id
        
        # Delete from Neo4j
        with neo4j_driver.session() as session:
            session.run("MATCH (p:Product {mysql_id: $pid}) DETACH DELETE p", pid=product_id)
        
        db.delete(product)
        db.commit()
        
        redis_client.delete("product_list")
        return {"status": "deleted", "article": article, "name": product_name}


class OrderService:
    def low_stock_report(self, db: Session) -> dict:
        """Generate low stock report with business letters."""
        low_stock_products = db.query(ProductDB).filter(ProductDB.quantity < ProductDB.min_stock).all()
        if not low_stock_products:
            return {"total_letters": 0, "letters": []}

        # Group products by supplier
        letters: Dict[str, dict] = {}
        for product in low_stock_products:
            supplier = product.supplier
            if not supplier:
                continue
            
            if supplier.name not in letters:
                letters[supplier.name] = {
                    "supplier_name": supplier.name,
                    "supplier_email": supplier.contact_email,
                    "city": supplier.city,
                    "products": [],
                }
            
            needed_quantity = product.min_stock * 2 - product.quantity
            letters[supplier.name]["products"].append(
                {
                    "article": product.article,
                    "name": product.name,
                    "current_quantity": product.quantity,
                    "min_stock": product.min_stock,
                    "needed_quantity": needed_quantity,
                    "delivery_days": product.delivery_days,
                }
            )

        # Generate business letters
        business_letters = []
        for supplier_name, data in letters.items():
            letter_lines = [
                f"Шановний постачальнику {data['supplier_name']},",
                "",
                "Звертаємося до Вас з приводу необхідності поповнення асортименту нашого інтернет-магазину.",
                "На даний момент у нас виявлено дефіцит наступних позицій:",
                "",
            ]
            
            for p in data["products"]:
                letter_lines.extend([
                    f"- {p['name']} (Артикул: {p['article']})",
                    f"  Поточна кількість: {p['current_quantity']} шт.",
                    f"  Мінімальний запас: {p['min_stock']} шт.",
                    f"  Необхідна кількість до постачання: {p['needed_quantity']} шт.",
                    f"  Очікуваний час постачання: {p['delivery_days']} днів",
                    "",
                ])
            
            letter_lines.extend([
                "Просимо Вас розглянути можливість термінового постачання зазначених товарів.",
                "",
                "З повагою,",
                "Адміністрація інтернет-магазину",
                "",
                f"Контактна інформація:",
                f"Email: {data['supplier_email']}",
                f"Місто постачальника: {data['city']}",
            ])
            
            business_letters.append({
                "supplier": supplier_name,
                "email": data["supplier_email"],
                "letter": "\n".join(letter_lines),
            })
        
        return {"total_letters": len(business_letters), "letters": business_letters}


class AnalyticsService:
    def popular_products(self) -> dict:
        query = """
        MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)
        RETURN p.name AS Product, p.article AS Article, s.name AS Supplier, count(s) AS SupplierCount
        ORDER BY SupplierCount DESC
        LIMIT 10
        """
        results = []
        with neo4j_driver.session() as session:
            data = session.run(query)
            for record in data:
                results.append(
                    {
                        "product": record["Product"],
                        "article": record["Article"],
                        "supplier": record["Supplier"],
                        "supplier_count": record["SupplierCount"],
                    }
                )
        return {"report_type": "Popular Products Analysis", "data": results}

    def suppliers_by_city(self) -> dict:
        query = """
        MATCH (s:Supplier)
        RETURN s.city AS City, collect(s.name) AS Suppliers, count(s) AS Count
        ORDER BY Count DESC
        """
        results = []
        with neo4j_driver.session() as session:
            data = session.run(query)
            for record in data:
                results.append(
                    {"city": record["City"], "suppliers": record["Suppliers"], "count": record["Count"]}
                )
        return {"report_type": "Suppliers by City", "data": results}


class SportService:
    def __init__(self):
        self.store = SportStore()

    def _find_client_by_username(self, username: str):
        for client in self.store.list_all("clients"):
            if client.get("username") == username:
                return client
        return None

    def _extract_contact_info(self, contact_data) -> ContactInfo:
        """Extract and normalize contact information from various formats."""
        if not contact_data:
            return ContactInfo()
        if isinstance(contact_data, dict):
            return ContactInfo(**contact_data)
        if hasattr(contact_data, 'dict'):
            return ContactInfo(**contact_data.dict())
        return contact_data if isinstance(contact_data, ContactInfo) else ContactInfo()

    # ---------------- Clients ----------------
    def create_client(self, payload, user_role: str = "admin", auth_service=None) -> dict:
        if not payload.full_name or not payload.full_name.strip():
            raise ValueError("Client full name is required and cannot be empty")
        if payload.birth_date >= date.today():
            raise ValueError("Birth date cannot be today or in the future")
        if not payload.username or not payload.username.strip():
            raise ValueError("Username is required and cannot be empty")
        if not payload.password or len(payload.password) < 6:
            raise ValueError("Password must be at least 6 characters")

        contact = self._extract_contact_info(payload.contact_info)
        email = contact.email if contact else None

        # uniqueness checks
        for c in self.store.list_all("clients"):
            if email and c.get("contact_info", {}).get("email") == email:
                raise ValueError(f"Client with email '{email}' already exists")
            if c.get("username") == payload.username:
                raise ValueError(f"Username '{payload.username}' already exists")

        # Register user account if auth_service is provided
        if auth_service:
            auth_service.register(payload.username, payload.password, email)

        client_obj = {
            "full_name": payload.full_name,
            "birth_date": payload.birth_date.isoformat(),
            "gender": payload.gender,
            "contact_info": {
                "phone": contact.phone if contact else None,
                "email": email,
                "address": getattr(contact, "address", None),
            },
            "username": payload.username,
            "has_valid_cert": False,
        }
        saved = self.store.add("clients", client_obj, "client_id")

        age = datetime.now().year - payload.birth_date.year
        if (datetime.now().month, datetime.now().day) < (payload.birth_date.month, payload.birth_date.day):
            age -= 1

        return {
            "client_id": saved["client_id"],
            "full_name": saved["full_name"],
            "age": age,
            "username": payload.username,
            "message": "Client created successfully",
        }

    def list_clients(self, query_params=None) -> dict:
        """List clients with optional pagination and filtering."""
        clients = self.store.list_all("clients")
        
        # Apply filters
        if query_params:
            if query_params.search:
                search_lower = query_params.search.lower()
                clients = [c for c in clients if search_lower in c.get("full_name", "").lower()]
            
            if query_params.has_membership is not None:
                memberships = self.store.list_all("memberships")
                active_client_ids = {m["client_id"] for m in memberships if m.get("status") == "active"}
                if query_params.has_membership:
                    clients = [c for c in clients if c["client_id"] in active_client_ids]
                else:
                    clients = [c for c in clients if c["client_id"] not in active_client_ids]
            
            # Sort
            reverse = query_params.sort_order == "desc"
            if query_params.sort_by == "full_name":
                clients = sorted(clients, key=lambda c: c.get("full_name", ""), reverse=reverse)
            
            # Pagination
            total = len(clients)
            offset = (query_params.page - 1) * query_params.page_size
            clients = clients[offset:offset + query_params.page_size]
        else:
            total = len(clients)
        
        result = []
        for c in clients:
            bd = datetime.fromisoformat(c["birth_date"]).date() if c.get("birth_date") else None
            age = datetime.now().year - bd.year if bd else 0
            if bd and (datetime.now().month, datetime.now().day) < (bd.month, bd.day):
                age -= 1
            result.append({
                "client_id": c["client_id"],
                "full_name": c["full_name"],
                "birth_date": c.get("birth_date"),
                "age": age,
                "gender": c.get("gender"),
                "contact_info": c.get("contact_info", {}),
                "username": c.get("username"),
            })
        
        if query_params:
            return {
                "items": result,
                "total": total,
                "page": query_params.page,
                "page_size": query_params.page_size,
                "total_pages": (total + query_params.page_size - 1) // query_params.page_size,
            }
        return result

    def get_client(self, client_id: int) -> dict:
        client = self.store.get("clients", "client_id", client_id)
        if not client:
            raise ValueError("Client not found")
        bd = datetime.fromisoformat(client["birth_date"]).date() if client.get("birth_date") else None
        age = datetime.now().year - bd.year if bd else 0
        if bd and (datetime.now().month, datetime.now().day) < (bd.month, bd.day):
            age -= 1
        return {
            "client_id": client["client_id"],
            "full_name": client["full_name"],
            "birth_date": client.get("birth_date"),
            "age": age,
            "gender": client.get("gender"),
            "contact_info": client.get("contact_info", {}),
            "username": client.get("username"),
        }

    def get_user_profile(self, username: str) -> dict:
        client = self._find_client_by_username(username)
        if not client:
            raise ValueError("Client not found")

        contact = client.get("contact_info") or {}
        return {
            "client_id": client.get("client_id"),
            "username": client.get("username"),
            "full_name": client.get("full_name"),
            "contact_info": {
                "phone": contact.get("phone"),
                "email": contact.get("email"),
                "address": contact.get("address"),
            },
        }

    def update_user_profile(self, username: str, payload) -> dict:
        if payload.email is None and payload.phone is None:
            raise ValueError("No profile fields provided")

        client = self._find_client_by_username(username)
        if not client:
            raise ValueError("Client not found")

        contact = client.get("contact_info") or {}
        new_contact = contact.copy()

        if payload.phone is not None:
            new_contact["phone"] = payload.phone
        if payload.email is not None:
            new_contact["email"] = payload.email

        updated = self.store.update(
            "clients",
            "client_id",
            client["client_id"],
            {"contact_info": new_contact},
        )

        try:
            from app.auth import USERS
            if payload.email is not None and username in USERS:
                USERS[username]["email"] = payload.email
        except Exception:
            pass

        return {
            "client_id": updated.get("client_id"),
            "username": updated.get("username"),
            "full_name": updated.get("full_name"),
            "contact_info": new_contact,
            "message": "Profile updated successfully",
        }

    def update_client(self, client_id: int, payload) -> dict:
        if not payload.full_name or not payload.full_name.strip():
            raise ValueError("Client full name is required and cannot be empty")
        if payload.birth_date >= date.today():
            raise ValueError("Birth date cannot be today or in the future")
        
        if payload.username and not payload.username.strip():
            raise ValueError("Username cannot be empty")
        
        if payload.password and len(payload.password) < 6:
            raise ValueError("Password must be at least 6 characters")

        contact = self._extract_contact_info(payload.contact_info)
        update_data = {
            "full_name": payload.full_name,
            "birth_date": payload.birth_date.isoformat(),
            "gender": payload.gender,
            "contact_info": {
                "phone": contact.phone if contact else None,
                "email": contact.email if contact else None,
                "address": getattr(contact, "address", None),
            },
        }
        
        # Add username if provided
        if payload.username:
            update_data["username"] = payload.username
        
        # Add password if provided
        if payload.password:
            update_data["password"] = payload.password
        
        print(f"[DEBUG] Updating client {client_id} with data: {update_data}")
        
        updated = self.store.update(
            "clients",
            "client_id",
            client_id,
            update_data,
        )
        
        print(f"[DEBUG] Updated client data: {updated}")
        
        bd = datetime.fromisoformat(updated["birth_date"]).date() if updated.get("birth_date") else None
        age = datetime.now().year - bd.year if bd else 0
        if bd and (datetime.now().month, datetime.now().day) < (bd.month, bd.day):
            age -= 1
        return {
            "client_id": updated["client_id"],
            "full_name": updated["full_name"],
            "birth_date": updated.get("birth_date"),
            "age": age,
            "gender": updated.get("gender"),
            "contact_info": updated.get("contact_info", {}),
            "username": updated.get("username"),
            "message": "Client updated successfully",
        }

    def delete_client(self, client_id: int) -> dict:
        client = self.store.get("clients", "client_id", client_id)
        if not client:
            raise ValueError("Client not found")
        self.store.delete("clients", "client_id", client_id)
        return {"message": f"Client {client['full_name']} deleted successfully", "client_id": client_id}

    # ---------------- Trainers ----------------
    def create_trainer(self, payload) -> dict:
        if not payload.full_name or not payload.full_name.strip():
            raise ValueError("Trainer full name is required and cannot be empty")
        if not payload.specialization or not payload.specialization.strip():
            raise ValueError("Trainer specialization is required and cannot be empty")
        if payload.birth_date >= date.today():
            raise ValueError("Birth date cannot be today or in the future")

        for t in self.store.list_all("trainers"):
            if t.get("full_name", "").lower().strip() == payload.full_name.lower().strip():
                raise ValueError(f"Trainer with name '{payload.full_name}' already exists")

        contact = self._extract_contact_info(payload.contact_info)
        trainer_obj = {
            "full_name": payload.full_name,
            "specialization": payload.specialization,
            "birth_date": payload.birth_date.isoformat(),
            "contact_info": {
                "phone": contact.phone if contact else None,
                "email": contact.email if contact else None,
            },
        }
        saved = self.store.add("trainers", trainer_obj, "trainer_id")
        return {
            "trainer_id": saved["trainer_id"],
            "full_name": saved["full_name"],
            "specialization": saved["specialization"],
        }

    def list_trainers(self) -> List[dict]:
        return [
            {
                "trainer_id": t["trainer_id"],
                "full_name": t.get("full_name"),
                "specialization": t.get("specialization"),
                "contact_info": t.get("contact_info", {}),
            }
            for t in self.store.list_all("trainers")
        ]

    def update_trainer(self, trainer_id: int, payload) -> dict:
        if not payload.full_name or not payload.full_name.strip():
            raise ValueError("Trainer full name is required and cannot be empty")
        if not payload.specialization or not payload.specialization.strip():
            raise ValueError("Trainer specialization is required and cannot be empty")
        if payload.birth_date >= date.today():
            raise ValueError("Birth date cannot be today or in the future")

        contact = self._extract_contact_info(payload.contact_info)
        updated = self.store.update(
            "trainers",
            "trainer_id",
            trainer_id,
            {
                "full_name": payload.full_name,
                "specialization": payload.specialization,
                "birth_date": payload.birth_date.isoformat(),
                "contact_info": {
                    "phone": contact.phone if contact else None,
                    "email": contact.email if contact else None,
                },
            },
        )
        return {
            "trainer_id": updated["trainer_id"],
            "full_name": updated["full_name"],
            "specialization": updated["specialization"],
            "message": "Trainer updated successfully",
        }

    def delete_trainer(self, trainer_id: int) -> dict:
        trainer = self.store.get("trainers", "trainer_id", trainer_id)
        if not trainer:
            raise ValueError("Trainer not found")
        self.store.delete("trainers", "trainer_id", trainer_id)
        return {"message": f"Trainer {trainer['full_name']} deleted successfully", "trainer_id": trainer_id}

    # ---------------- Services ----------------
    def create_service(self, payload) -> dict:
        if payload.price < 0:
            raise ValueError("Service price must be non-negative")
        if not payload.service_name or not payload.service_name.strip():
            raise ValueError("Service name is required")

        for s in self.store.list_all("services"):
            if s.get("service_name", "").lower().strip() == payload.service_name.lower().strip():
                raise ValueError(f"Service '{payload.service_name}' already exists")

        service_obj = {
            "service_name": payload.service_name,
            "price": payload.price,
            "requires_medical_certificate": payload.requires_medical_certificate,
            "is_active": True,
        }
        saved = self.store.add("services", service_obj, "service_id")
        return saved

    def list_services(self) -> List[dict]:
        return [
            {
                "service_id": s["service_id"],
                "service_name": s["service_name"],
                "name": s["service_name"],
                "price": s.get("price"),
                "requires_medical_certificate": s.get("requires_medical_certificate", False),
            }
            for s in self.store.list_all("services") if s.get("is_active", True)
        ]

    def update_service(self, service_id: int, payload) -> dict:
        if payload.price < 0:
            raise ValueError("Service price must be non-negative")
        if not payload.service_name or not payload.service_name.strip():
            raise ValueError("Service name is required")

        updated = self.store.update(
            "services",
            "service_id",
            service_id,
            {
                "service_name": payload.service_name,
                "price": payload.price,
                "requires_medical_certificate": payload.requires_medical_certificate,
            },
        )
        return {
            "service_id": updated["service_id"],
            "service_name": updated["service_name"],
            "price": updated["price"],
            "requires_medical_certificate": updated.get("requires_medical_certificate", False),
            "message": "Service updated successfully",
        }

    def delete_service(self, service_id: int) -> dict:
        service = self.store.get("services", "service_id", service_id)
        if not service:
            raise ValueError("Service not found")
        # Soft delete: mark as inactive instead of removing
        self.store.update("services", "service_id", service_id, {"is_active": False})
        return {"message": f"Service {service['service_name']} deleted successfully", "service_id": service_id}

    # ---------------- Medical & Visits ----------------
    def attach_medical(self, payload) -> dict:
        client = self.store.get("clients", "client_id", payload.client_id)
        if not client:
            raise ValueError(f"Client {payload.client_id} not found")
        if payload.expiry_date <= payload.examination_date:
            raise ValueError("Certificate expiry date must be after examination date")
        client["has_valid_cert"] = True
        client["medical_certificate_valid_until"] = payload.expiry_date.isoformat()
        client["medical_notes"] = payload.examination_result
        self.store._save()
        return {
            "certificate_id": f"cert_{client['client_id']}",
            "client_id": client["client_id"],
            "expiry_date": payload.expiry_date.isoformat(),
        }

    def register_visit(self, payload) -> dict:
        client = self.store.get("clients", "client_id", payload.client_id)
        if not client:
            raise ValueError(f"Client {payload.client_id} not found")
        service = self.store.get("services", "service_id", payload.service_id)
        if not service:
            raise ValueError(f"Service {payload.service_id} not found")

        if service.get("requires_medical_certificate"):
            if not client.get("has_valid_cert") or not client.get("medical_certificate_valid_until"):
                raise ValueError("Medical certificate is required and not valid")
            if datetime.fromisoformat(client["medical_certificate_valid_until"]) < datetime.now():
                raise ValueError("Medical certificate has expired")

        visit_obj = {
            "client_id": client["client_id"],
            "service_id": service["service_id"],
            "entry_time": (payload.entry_time or datetime.now()).isoformat(),
        }
        saved = self.store.add("visits", visit_obj, "visit_id")
        return {
            "visit_id": saved["visit_id"],
            "client_id": saved["client_id"],
            "service": service["service_name"],
            "entry_time": saved["entry_time"],
        }

    def _get_visit_dict(self, visit) -> dict:
        client = self.store.get("clients", "client_id", visit["client_id"])
        service = self.store.get("services", "service_id", visit["service_id"])
        return {
            "visit_id": visit["visit_id"],
            "client_id": visit["client_id"],
            "client_name": client.get("full_name") if client else "Unknown",
            "service_id": visit["service_id"],
            "service_name": service.get("service_name") if service else "Unknown",
            "entry_time": visit.get("entry_time"),
            "exit_time": visit.get("exit_time"),
        }

    def list_visits(self) -> List[dict]:
        return [self._get_visit_dict(v) for v in self.store.list_all("visits")]

    # ---------------- Memberships ----------------
    def create_membership(self, payload: dict) -> dict:
        # Allow lightweight memberships even if client was pre-seeded elsewhere
        membership_obj = {
            "client_id": payload.get("client_id"),
            "start_date": payload.get("start_date"),
            "end_date": payload.get("end_date"),
            "status": payload.get("status", "active"),
        }
        saved = self.store.add("memberships", membership_obj, "membership_id")
        return saved

    def _get_membership_dict(self, membership) -> dict:
        client = self.store.get("clients", "client_id", membership["client_id"])
        return {
            "membership_id": membership["membership_id"],
            "client_id": membership["client_id"],
            "client_name": client.get("full_name") if client else "Unknown",
            "start_date": membership.get("start_date"),
            "end_date": membership.get("end_date"),
            "status": membership.get("status"),
            "subscription_type": membership.get("subscription_type"),
            "price": membership.get("price"),
        }

    def list_memberships(self) -> List[dict]:
        return [self._get_membership_dict(m) for m in self.store.list_all("memberships")]

    def update_membership(self, membership_id: int, payload: dict) -> dict:
        membership = self.store.get("memberships", "membership_id", membership_id)
        if not membership:
            raise ValueError("Membership not found")
        
        # Update with provided fields
        updated_data = {}
        if "client_id" in payload:
            updated_data["client_id"] = payload["client_id"]
        if "start_date" in payload:
            updated_data["start_date"] = payload["start_date"]
        if "end_date" in payload:
            updated_data["end_date"] = payload["end_date"]
        if "status" in payload:
            updated_data["status"] = payload["status"]
        if "subscription_type" in payload:
            updated_data["subscription_type"] = payload["subscription_type"]
        if "price" in payload:
            updated_data["price"] = payload["price"]
        
        updated = self.store.update("memberships", "membership_id", membership_id, updated_data)
        return self._get_membership_dict(updated)

    def delete_membership(self, membership_id: int) -> dict:
        membership = self.store.get("memberships", "membership_id", membership_id)
        if not membership:
            raise ValueError("Membership not found")
        
        client = self.store.get("clients", "client_id", membership["client_id"])
        client_name = client.get("full_name") if client else "Unknown"
        
        self.store.delete("memberships", "membership_id", membership_id)
        return {"message": f"Membership for {client_name} deleted successfully", "membership_id": membership_id}

    # ---------------- Reports ----------------
    def report(self) -> dict:
        visits = self.store.list_all("visits")
        services = {s["service_id"]: s for s in self.store.list_all("services")}
        visits_per_service: Dict[str, int] = {}
        total_revenue = 0.0
        for v in visits:
            svc = services.get(v["service_id"])
            if not svc:
                continue
            name = svc["service_name"]
            visits_per_service[name] = visits_per_service.get(name, 0) + 1
            total_revenue += svc.get("price") or 0.0
        return {
            "total_clients": len(self.store.list_all("clients")),
            "total_revenue": total_revenue,
            "visits_per_service": visits_per_service,
            "notes": "Auto-generated from JSON store",
        }

    def analytics(self) -> dict:
        visits = self.store.list_all("visits")
        clients = self.store.list_all("clients")
        if not visits or not clients:
            return {"avg_revenue_per_client": 0.0, "avg_visits_per_client": 0.0}
        services = {s["service_id"]: s for s in self.store.list_all("services")}
        revenue = 0.0
        for visit in visits:
            svc = services.get(visit["service_id"])
            if svc:
                revenue += svc.get("price") or 0.0
        total_clients = len(clients)
        return {
            "avg_revenue_per_client": revenue / total_clients,
            "avg_visits_per_client": len(visits) / total_clients,
        }
