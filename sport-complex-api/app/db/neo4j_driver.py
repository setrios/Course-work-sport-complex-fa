from neo4j import GraphDatabase
from typing import Optional

# Hardcoded for now since Config is skipped
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

class Neo4jDriver:
    _driver: Optional[GraphDatabase.driver] = None
    
    @classmethod
    def get_driver(cls):
        """
        Returns a Neo4j driver instance (singleton pattern).
        """
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
        return cls._driver
    
    @classmethod
    def close(cls):
        """
        Closes the driver connection.
        """
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None

def get_neo4j_driver():
    """
    Dependency that provides a Neo4j driver instance.
    """
    return Neo4jDriver.get_driver()

def get_neo4j_session():
    """
    Returns a Neo4j session for executing queries.
    """
    driver = Neo4jDriver.get_driver()
    return driver.session()
