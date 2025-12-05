import json
import time
from datetime import datetime

# Import our custom modules
# Note: In a real environment, you would need to have the database drivers installed
# and the services (Redis, MySQL, CouchDB, Neo4j) running.
try:
    from redis_models import RedisManager
    from couchdb_models import create_sample_supply_request
except ImportError:
    print("Warning: Dependencies not found. This is expected if you haven't installed requirements.")
    print("This script is a demonstration of the logic flow.")

def main():
    print("=== SportComplex System Integration Demo ===\n")

    # 1. Initialize Managers
    # redis_db = RedisManager(host='localhost', port=6379, db=0)
    print("[INIT] Connecting to databases...")
    print("   - MySQL: Connected (Simulated)")
    print("   - Redis: Connected (Simulated)")
    print("   - CouchDB: Connected (Simulated)")
    print("   - Neo4j: Connected (Simulated)")

    # 2. User Login Flow
    print("\n[FLOW 1] User Login 'ivan_petrenko'")
    user_id = 123
    session_token = "abc-123-xyz"
    user_data = {"user_id": user_id, "role": "client", "email": "ivan@example.com"}
    
    # Redis: Cache session
    # redis_db.set_session(session_token, user_data)
    print(f"   -> Redis: Saved session token '{session_token}' with TTL 24h")
    print(f"   -> Redis: Added user_{user_id} to 'online:clients' set")

    # 3. Product Search & Recommendation
    print("\n[FLOW 2] Client searches for 'Protein'")
    # MySQL: Search products
    print("   -> MySQL: SELECT * FROM products WHERE name LIKE '%Protein%'")
    
    # Neo4j: Get smart recommendations
    print("   -> Neo4j: Executing Recommendation Query...")
    print("      MATCH (c:Client {id: 123})-[:SIMILAR_TO]-(similar)-[:PURCHASED]->(p:Product)")
    print("      RETURN p.name ORDER BY frequency DESC")
    print("      [Result]: Recommended 'Creatine Monohydrate' (bought by 5 similar clients)")

    # 4. View Product Details
    product_id = 45
    print(f"\n[FLOW 3] Client views Product #{product_id}")
    # Redis: Check cache first
    # cached_product = redis_db.get_cached_product(product_id)
    print("   -> Redis: Cache MISS. Fetching from DB...")
    print("   -> MySQL: SELECT * FROM products WHERE id = 45")
    print("   -> Redis: Cache SET 'product:45' (TTL 1h)")

    # 5. Purchase Logic
    print("\n[FLOW 4] Client purchases Product #45 (Quantity: 5)")
    current_stock = 4  # Too low!
    requested_qty = 5
    print(f"   -> Check Stock: Requested {requested_qty}, Available {current_stock}")
    
    if current_stock < requested_qty:
        print("   [!] Insufficient Stock!")
        # Trigger Low Stock Event
        print("   -> System triggers 'Low Stock' workflow")
        
        # CouchDB: Create Supply Request Letter
        letter = create_sample_supply_request()
        # letter.save()
        print(f"   -> CouchDB: Created SupplyRequestLetter doc (ID: {letter._id})")
        print(f"      To: {letter.supplier['name']}")
        print(f"      Requesting: {letter.products_requested[0]['name']}")

        # Redis: Notify Admin/Supplier logic
        # redis_db.push_email_task({...})
        print("   -> Redis: Pushed task to 'email_queue' (Notify Supplier)")

    else:
        print("   -> MySQL: INSERT INTO orders...")
        print("   -> Redis: Decrement stock, Update Bestsellers ranking")

    print("\n=== Demo Completed Successfully ===")

if __name__ == "__main__":
    main()