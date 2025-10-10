import grpc
import pytest
from concurrent import futures
from datetime import datetime

from src import borrowing_pb2, borrowing_pb2_grpc
from src.borrowing_server import BorrowingService
from src.db import SessionLocal, Base, engine
from src import crud, models

# -------------------------------
# Database Setup / Teardown
# -------------------------------
@pytest.fixture(scope="session", autouse=True)
def database_setup():
    """
    Create tables for the borrowing database once per session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def db_session_cleanup():
    """
    Cleanup BorrowedBook table after each test.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.query(models.BorrowedBook).delete()
        db.commit()
        db.close()


# -------------------------------
# gRPC Server Fixture
# -------------------------------
@pytest.fixture(scope="module")
def grpc_stub(database_setup):
    """
    Start BorrowingService gRPC server and yield a stub.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    borrowing_pb2_grpc.add_BorrowingServiceServicer_to_server(BorrowingService(), server)
    
    # Let OS pick a free port
    port = server.add_insecure_port("localhost:0")
    server.start()

    channel = grpc.insecure_channel(f"localhost:{port}")
    # Wait until channel is ready
    grpc.channel_ready_future(channel).result(timeout=5)
    stub = borrowing_pb2_grpc.BorrowingServiceStub(channel)

    yield stub

    server.stop(None)


# -------------------------------
# Tests
# -------------------------------
def test_borrow_book_and_check_db(grpc_stub):
    """
    Test that a borrow request is inserted into the database and can be retrieved.
    """
    user_id = "user-123"
    book_id = "book-abc"

    # Borrow a book
    resp = grpc_stub.BorrowBook(
        borrowing_pb2.BorrowRequest(user_id=user_id, book_id=book_id)
    )
    assert resp.status == "success"
    borrow_id = resp.borrow_id

    # Verify it exists in the DB
    db = SessionLocal()
    borrow = db.query(models.BorrowedBook).filter_by(borrow_id=borrow_id).first()
    db.close()
    assert borrow is not None
    assert borrow.user_id == user_id
    assert borrow.book_id == book_id

    # Retrieve borrowed books via gRPC
    list_resp = grpc_stub.GetBorrowedBooks(
        borrowing_pb2.UserRequest(user_id=user_id)
    )
    assert any(b.borrow_id == borrow_id for b in list_resp.borrowed_books)


def test_return_book(grpc_stub):
    """
    Test returning a book via gRPC updates the database correctly.
    """
    # First, insert a borrow directly via CRUD
    db = SessionLocal()
    borrow = crud.create_borrow(db, user_id="user-999", book_id="book-xyz")
    db.close()

    # Return via gRPC
    ret_resp = grpc_stub.ReturnBook(
        borrowing_pb2.ReturnRequest(borrow_id=borrow.borrow_id)
    )
    assert ret_resp.status == "success"

    # Verify DB no longer has this borrow
    db = SessionLocal()
    deleted_borrow = db.query(models.BorrowedBook).filter_by(borrow_id=borrow.borrow_id).first()
    db.close()
    assert deleted_borrow is None
