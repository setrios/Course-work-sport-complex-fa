from __future__ import annotations

import os
import couchdb
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from neo4j import GraphDatabase

from sport_complex import SportComplexSystem

# Database configuration with environment variable fallbacks
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "sport-complex-cw")
DB_PASSWORD = os.getenv("DB_PASSWORD", "sport-complex-cw")
DB_NAME = os.getenv("DB_NAME", "sport-complex-cw")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
REDIS_TTL_SUPPLIERS = 120
REDIS_TTL_PRODUCTS = 60

# CouchDB
COUCHDB_URL = os.getenv("COUCHDB_URL", "http://couchdb:couchdb@localhost:5984/")
try:
    couch_server = couchdb.Server(COUCHDB_URL)
    db_couch = couch_server.create("product_images") if "product_images" not in couch_server else couch_server["product_images"]
except Exception as e:
    print(f"CouchDB Warning: {e}")
    db_couch = None

# Neo4j
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jneo4j")
neo4j_driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Sport complex in-memory system
sport_system = SportComplexSystem()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
