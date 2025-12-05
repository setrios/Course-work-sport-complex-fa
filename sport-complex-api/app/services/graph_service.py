from typing import Dict, Any, List, Optional
from app.db.neo4j_driver import get_neo4j_session

class GraphService:
    """Service for Neo4j graph operations"""
    
    @staticmethod
    def create_client_node(client_id: int, name: str, registration_date: str):
        """Create a Client node in Neo4j"""
        with get_neo4j_session() as session:
            query = """
            CREATE (c:Client {
                id: $client_id,
                name: $name,
                registration_date: date($registration_date)
            })
            RETURN c
            """
            session.run(query, client_id=client_id, name=name, registration_date=registration_date)
    
    @staticmethod
    def create_trainer_node(trainer_id: int, name: str, specialization: str):
        """Create a Trainer node in Neo4j"""
        with get_neo4j_session() as session:
            query = """
            CREATE (t:Trainer {
                id: $trainer_id,
                name: $name,
                specialization: $specialization
            })
            RETURN t
            """
            session.run(query, trainer_id=trainer_id, name=name, specialization=specialization)
    
    @staticmethod
    def create_product_node(product_id: int, name: str, category: str):
        """Create a Product node in Neo4j"""
        with get_neo4j_session() as session:
            query = """
            MERGE (p:Product {id: $product_id})
            SET p.name = $name, p.category = $category
            RETURN p
            """
            session.run(query, product_id=product_id, name=name, category=category)
    
    @staticmethod
    def record_purchase(client_id: int, product_id: int, quantity: int, price: float):
        """Record a client purchasing a product"""
        with get_neo4j_session() as session:
            query = """
            MATCH (c:Client {id: $client_id})
            MATCH (p:Product {id: $product_id})
            CREATE (c)-[r:PURCHASED {
                quantity: $quantity,
                total_price: $price,
                date: datetime()
            }]->(p)
            RETURN r
            """
            session.run(query, client_id=client_id, product_id=product_id, 
                       quantity=quantity, price=price)
    
    @staticmethod
    def record_training_session(client_id: int, trainer_id: int, rating: Optional[int] = None):
        """Record a client training with a trainer"""
        with get_neo4j_session() as session:
            query = """
            MATCH (c:Client {id: $client_id})
            MATCH (t:Trainer {id: $trainer_id})
            CREATE (c)-[r:TRAINED_WITH {
                date: datetime(),
                rating: $rating
            }]->(t)
            RETURN r
            """
            session.run(query, client_id=client_id, trainer_id=trainer_id, rating=rating)
    
    @staticmethod
    def get_product_recommendations(client_id: int, limit: int = 5) -> List[Dict]:
        """Get product recommendations based on similar clients' purchases"""
        with get_neo4j_session() as session:
            query = """
            MATCH (c:Client {id: $client_id})-[:PURCHASED]->(p:Product)
            MATCH (p)<-[:PURCHASED]-(other:Client)
            MATCH (other)-[:PURCHASED]->(rec:Product)
            WHERE NOT (c)-[:PURCHASED]->(rec)
            RETURN rec.id AS product_id, rec.name AS product_name, 
                   COUNT(*) AS recommendation_score
            ORDER BY recommendation_score DESC
            LIMIT $limit
            """
            result = session.run(query, client_id=client_id, limit=limit)
            return [dict(record) for record in result]
    
    @staticmethod
    def get_trainer_recommendations(client_id: int, limit: int = 5) -> List[Dict]:
        """Get trainer recommendations based on similar clients"""
        with get_neo4j_session() as session:
            query = """
            MATCH (c:Client {id: $client_id})-[:TRAINED_WITH]->(t:Trainer)
            MATCH (t)<-[r:TRAINED_WITH]-(other:Client)
            MATCH (other)-[r2:TRAINED_WITH]->(rec:Trainer)
            WHERE NOT (c)-[:TRAINED_WITH]->(rec) AND r2.rating >= 4
            RETURN rec.id AS trainer_id, rec.name AS trainer_name,
                   rec.specialization AS specialization,
                   COUNT(*) AS recommendation_score
            ORDER BY recommendation_score DESC
            LIMIT $limit
            """
            result = session.run(query, client_id=client_id, limit=limit)
            return [dict(record) for record in result]
