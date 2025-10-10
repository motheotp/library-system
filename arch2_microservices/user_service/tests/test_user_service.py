import grpc
import pytest
from concurrent import futures
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# --- NEW IMPORTS: Access database and model components ---
from src import user_pb2, user_pb2_grpc, user_server
from src.db import get_db, Base, engine, SessionLocal
from src.models import create_db_and_tables, User
# --------------------------------------------------------

# IMPORTANT: For testing in a containerized environment, ensure the 
# DATABASE_URL environment variable points to the test database.
# In a docker-compose test setup, this should be handled automatically.
# Example: export DATABASE_URL="postgresql+psycopg2://testuser:testpass@localhost:5433/test_db"
# If this is not set, SQLAlchemy will likely raise an error.

@pytest.fixture(scope="session", autouse=True) # Runs once per test session
def database_setup():
    """
    Initializes the database engine and creates all tables before the tests run.
    Yields to let tests run, then cleans up the tables afterwards.
    """
    # 1. Ensure tables are created once
    create_db_and_tables()
    
    yield # Run tests
    
    # 2. Teardown: Drop all tables after the entire test session finishes
    # This assumes you have full control over the test database.
    Base.metadata.drop_all(bind=engine)
    

@pytest.fixture(scope="function", autouse=True) # Runs before and after EVERY test function
def db_session_cleanup():
    """
    Clears all data from the User table after each test run
    to ensure perfect test isolation.
    """
    db: Session = SessionLocal()
    try:
        # Before test: nothing to do, just yield
        yield db 
    finally:
        # After test: Rollback any changes and delete all user data
        db.rollback() 
        db.query(User).delete() # <--- NEW: Crucial for test isolation
        db.commit()
        db.close()
        
@pytest.fixture(scope="module")
def grpc_server(database_setup): # <--- CHANGE: Dependency on database_setup fixture
    """
    Starts the gRPC server and provides a stub for interaction.
    """
    # The database_setup fixture ensures tables exist before the server starts.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # We pass the same UserService instance to the gRPC server
    user_pb2_grpc.add_UserServiceServicer_to_server(user_server.UserService(), server)
    port = server.add_insecure_port("localhost:0")
    server.start()

    channel = grpc.insecure_channel(f"localhost:{port}")
    stub = user_pb2_grpc.UserServiceStub(channel)

    yield stub # test functions will use this stub

    server.stop(None)


def test_create_and_get_user(grpc_server):
    """Tests user creation and retrieval against the PostgreSQL database."""
    # Create user
    resp = grpc_server.CreateUser(user_pb2.CreateUserRequest(
        name="Alice",
        email="alice@example.com",
        password="secret123",
        user_type=user_pb2.STUDENT
    ))
    # Assertions remain the same, but now they check database persistence
    assert resp.user.name == "Alice"
    user_id = resp.user.id
    
    # Fetch user
    fetched = grpc_server.GetUser(user_pb2.GetUserRequest(id=user_id))
    
    assert fetched.user.email == "alice@example.com"
    
    # <--- NEW: Test that a subsequent test will start clean --->
    # The db_session_cleanup fixture will run immediately after this function finishes.


def test_authenticate_user(grpc_server):
    """Tests user authentication logic, including password hashing/comparison."""
    # This test starts with a clean database thanks to the db_session_cleanup fixture.
    
    # Create user for authentication test
    grpc_server.CreateUser(user_pb2.CreateUserRequest(
        name="Bob",
        email="bob@example.com",
        password="pass456",
        user_type=user_pb2.STAFF
    ))

    # Test successful authentication
    auth = grpc_server.AuthenticateUser(user_pb2.AuthenticateUserRequest(
        email="bob@example.com",
        password="pass456"
    ))

    assert auth.user_id is not None
    # CHANGE: Token is no longer hardcoded "fake-jwt-token" but now uses the ID
    assert auth.token == f"TOKEN_{auth.user_id}" 
    
    # Test failed authentication (wrong password)
    with pytest.raises(grpc.RpcError) as e:
        grpc_server.AuthenticateUser(user_pb2.AuthenticateUserRequest(
            email="bob@example.com",
            password="wrong-password"
        ))
    assert e.value.code() == grpc.StatusCode.UNAUTHENTICATED
    
    # Test failed authentication (wrong email)
    with pytest.raises(grpc.RpcError) as e:
        grpc_server.AuthenticateUser(user_pb2.AuthenticateUserRequest(
            email="not-bob@example.com",
            password="pass456"
        ))
    assert e.value.code() == grpc.StatusCode.UNAUTHENTICATED
