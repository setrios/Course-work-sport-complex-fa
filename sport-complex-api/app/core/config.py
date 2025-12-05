from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "SportComplex API"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000"]

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "sportcomplex"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "sportcomplex_db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # CouchDB
    COUCHDB_HOST: str = "localhost"
    COUCHDB_PORT: int = 5984
    COUCHDB_USER: str = "admin"
    COUCHDB_PASSWORD: str = "password"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_VERY_SECRET_KEY_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
