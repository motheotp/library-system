# functions for create, get, update users
# has grpc functions so grpc server stays clean

from sqlalchemy.orm import Session
from .models import User, UserType
from . import user_pb2 # Used for type mapping, gRPC request/response messages

# Helper function (Placeholder for robust hashing)
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ----------------------------------------------------
# CREATE Operations
# ----------------------------------------------------
def create_user(db: Session, request: user_pb2.CreateUserRequest, new_user_id: str) -> User:
    """Inserts a new user record into the database."""
    
    password_hash = hash_password(request.password)
    user_type_name = UserType(request.user_type).name

    db_user = User(
        id=new_user_id,
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        user_type=user_type_name
    )
    
    db.add(db_user)
    # Note: We rely on the get_db context manager (database.py) to commit the transaction
    return db_user

# ----------------------------------------------------
# READ Operations
# ----------------------------------------------------
def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Fetches a user record by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetches a user record by email for authentication."""
    return db.query(User).filter(User.email == email).first()

# ----------------------------------------------------
# PROTO MAPPING Helper
# ----------------------------------------------------
def user_model_to_proto(user_model: User) -> user_pb2.User:
    """Converts a SQLAlchemy User object to a Protobuf User message."""
    
    # Safely map the string name back to the protobuf integer enum value
    user_type_value = UserType[user_model.user_type].value
    
    return user_pb2.User(
        id=user_model.id,
        name=user_model.name,
        email=user_model.email,
        

        # This is stored for internal use; generally omitted for client-facing responses
        password_hash=user_model.password_hash, 
        user_type=user_type_value
    )
