#SQLAlchemy MODELS (User)
# Defines the User Alchemy class

from sqlalchemy import Column, String, Integer
from .db import Base, engine # Import engine from db.py for table creation
from . import user_pb2 # Import the generated protobuf file for enums
import enum

# Define a Python Enum that mirrors the Protobuf Enum
# This ensures type safety and clarity in the code.
class UserType(enum.Enum):
    UNKNOWN = user_pb2.UNKNOWN
    STUDENT = user_pb2.STUDENT
    STAFF = user_pb2.STAFF

# Define the User SQLAlchemy Model (Table Schema)
class User(Base):
    __tablename__ = "users"

    # id should be String to hold UUIDs generated in the server
    id = Column(String, primary_key=True, index=True) 
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # --- FIX 1: Renamed 'password' to 'password_hash' ---
    password_hash = Column(String, nullable=False) 
    
    # --- FIX 2: Using String column to store the enum name (e.g., "STUDENT") ---
    user_type = Column(String, default=UserType.STUDENT.name, nullable=False) 

# Database Initialization
def create_db_and_tables():
    """Creates all defined tables in the database if they do not exist."""
    print("Attempting to create database tables...")
    # Base.metadata contains all the table definitions inherited from Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
