# DB Connection + Base
# engine, SessionLocal and Base

import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager 

# 1. Define the Database URL from environment variables
# The environment variable DATABASE_URL will be set in docker-compose.yml

# DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db") 

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://user_service_user:strong_password@user_db:5432/user_service_db"
)

# 2. Create the SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True # Helps maintain connection health in a service environment
)

# 3. Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Define a declarative base class for models
Base = declarative_base()

# Helper function to get a database session and ensure it's closed
@contextmanager
def get_db():
    """Providing transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit() # Commit if successful
    except Exception:
        db.rollback() # Rollback if error
        raise
    finally:
        db.close() # Always close the session
