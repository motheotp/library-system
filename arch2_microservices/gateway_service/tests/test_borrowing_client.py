import pytest
from src.borrowing_client import BorrowingClient

@pytest.fixture(scope="module")
def grpc_client():
    """Setup BorrowingClient for tests"""
    client = BorrowingClient()
    yield client
    # Teardown if needed (close channel)
    client.channel.close()

def test_borrow_and_list(grpc_client):
    # Borrow a book for user 1
    borrow_resp = grpc_client.borrow_book(user_id="1", book_id="101")
    assert borrow_resp.status == "success"
    borrow_id = borrow_resp.borrow_id

    # Get borrowed books for user 1
    list_resp = grpc_client.get_borrowed_books(user_id="1")
    assert any(b.borrow_id == borrow_id for b in list_resp.borrowed_books)

    # Return the borrowed book
    return_resp = grpc_client.return_book(borrow_id)
    assert return_resp.status == "success"

    # Ensure the book is no longer listed
    list_resp_after = grpc_client.get_borrowed_books(user_id="1")
    assert all(b.borrow_id != borrow_id for b in list_resp_after.borrowed_books)
