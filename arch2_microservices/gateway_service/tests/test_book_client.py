import pytest
from src.book_client import BookClient
from src import book_pb2

@pytest.fixture(scope="module")
def client():
    # Initialize the client for the whole module
    c = BookClient()
    yield c
    c.close()

def test_add_and_get_book(client):
    # Add a book
    add_resp = client.add_book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565")
    book_id = add_resp.book.id
    assert add_resp.book.title == "The Great Gatsby"
    assert add_resp.book.author == "F. Scott Fitzgerald"

    # Get the book
    get_resp = client.get_book(book_id)
    assert get_resp.book.id == book_id
    assert get_resp.book.title == "The Great Gatsby"

def test_list_books(client):
    # List books and ensure at least one book exists
    list_resp = client.list_books()
    assert len(list_resp.books) >= 1

def test_update_book_status(client):
    # Add a new book
    add_resp = client.add_book("1984", "George Orwell", "1234567890")
    book_id = add_resp.book.id

    # Update the status
    update_resp = client.update_book_status(book_id, "borrowed")
    assert update_resp.book.status == "borrowed"

    # Confirm via get_book
    get_resp = client.get_book(book_id)
    assert get_resp.book.status == "borrowed"
