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

    # Map user_type to role
    role_map = {
        "STUDENT": "student",
        "STAFF": "admin",
        "UNKNOWN": "student"
    }
    role = role_map.get(user_type_name, "student")

    db_user = User(
        id=new_user_id,
        student_id=request.email.split('@')[0],  # Generate student_id from email prefix
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        user_type=user_type_name,
        role=role
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

def get_user_by_student_id(db: Session, student_id: str) -> User | None:
    """Fetches a user record by student_id for authentication."""
    return db.query(User).filter(User.student_id == student_id).first()

# ----------------------------------------------------
# PROTO MAPPING Helper
# ----------------------------------------------------
def user_model_to_proto(user_model: User) -> user_pb2.User:
    """Converts a SQLAlchemy User object to a Protobuf User message."""

    # Safely map the string name back to the protobuf integer enum value
    user_type_value = UserType[user_model.user_type].value

    return user_pb2.User(
        id=user_model.id,
        student_id=user_model.student_id if user_model.student_id else "",
        name=user_model.name,
        email=user_model.email,
        password_hash=user_model.password_hash,  # This is stored for internal use
        user_type=user_type_value,
        role=user_model.role if user_model.role else "student"
    )
