import pytest
import json
from src.gateway_server import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

# ------------------------
# User endpoints
# ------------------------
def test_add_and_get_user(client):
    # Create user
    
    response = client.post(
        "/users",
        data=json.dumps({"name": "Alice", "email": "alice@example.com", "password": "Testing123", "user_type": 1}),
        content_type="application/json"
    )
 
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["name"] == "Alice"
    user_id = user_data["id"]

    # Fetch same user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    fetched = response.get_json()
  
    assert fetched["id"] == user_id
    assert fetched["name"] == "Alice"

def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    users = response.get_json()["users"]
    print(users)
    
    assert isinstance(users, list)

# ------------------------
# Book endpoints
# ------------------------
def test_add_and_list_books(client):
    # Add book
    response = client.post(
        "/books",
        data=json.dumps({
            "title": "1984",
            "author": "George Orwell",
            "isbn": "12345"
        }),
        content_type="application/json"
    )
    assert response.status_code == 200
    book_data = response.get_json()
    assert book_data["title"] == "1984"
    book_id = book_data["id"]

    # Fetch same book
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    fetched = response.get_json()
    assert fetched["id"] == book_id
    assert fetched["title"] == "1984"

    # List books
    response = client.get("/books")
    assert response.status_code == 200
    books = response.get_json()["books"]
    assert any(b["title"] == "1984" for b in books)

# # ------------------------
# # Borrowing endpoints
# # ------------------------
def test_borrow_and_return(client):
    # First, add a user and a book
    user = client.post(
        "/users",
        data=json.dumps({"name": "Bob", "email": "bob@example.com", "password": "RoyalParis", "user_type": 2}),
        content_type="application/json"
    ).get_json()
    book = client.post(
        "/books",
        data=json.dumps({
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "isbn": "67890"
        }),
        content_type="application/json"
    ).get_json()

    # Borrow the book
    response = client.post(
        "/borrowings",
        data=json.dumps({"user_id": user["id"], "book_id": book["id"]}),
        content_type="application/json"
    )
    assert response.status_code == 200
    borrow_data = response.get_json()
    borrow_id = borrow_data["borrow_id"]
    assert borrow_data["status"] == "success"

    # Get user borrowings
    response = client.get(f"/users/{user['id']}/borrowings")
    assert response.status_code == 200
    borrowings = response.get_json()["borrowed_books"]
    assert any(b["book_id"] == book["id"] for b in borrowings) 

    # Return book
    response = client.post(f"/borrowings/{borrow_id}/return")
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


