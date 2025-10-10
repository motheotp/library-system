
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# from .models import Base

# Adjust according to your actual Postgres setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://book_service_user:strong_password@book_db:5432/book_service_db")

# Create the engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency helper for getting a session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize book table
def create_db_and_tables():
    print("Creating database tables for book service...")
    Base.metadata.create_all(bind=engine)
    print("Book service database setup complete.")
