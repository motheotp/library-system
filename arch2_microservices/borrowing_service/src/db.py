import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Database URL from environment variables (fallback to local SQLite for testing)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://borrowing_service_user:strong_password@borrowing_db:5432/borrowing_service_db"
)

# SQLAlchemy Engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

@contextmanager
def get_db():
    """Provide transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
