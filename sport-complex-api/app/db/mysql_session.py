from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Hardcoded for now since Config is skipped
# In production, these should come from app.core.config
MYSQL_URL = "mysql+pymysql://sportcomplex:password@localhost:3306/sportcomplex_db"

engine = create_engine(
    MYSQL_URL,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
