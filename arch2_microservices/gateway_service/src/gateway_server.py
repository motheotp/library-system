from flask import Flask, request, jsonify
from flask_cors import CORS
from src.user_client import UserClient
from src.book_client import BookClient
from src.borrowing_client import BorrowingClient
import grpc
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Initialize gRPC clients to None
user_client = None
book_client = None
borrowing_client = None

# # Initialize gRPC clients
# user_client = UserClient()
# book_client = BookClient()
# borrowing_client = BorrowingClient()


def initialize_clients():
    """Initialize gRPC clients with error handling"""
    global user_client, book_client, borrowing_client
    try:
        logging.info("Initializing gRPC clients...")
        user_client = UserClient()
        logging.info("✓ UserClient initialized")
    except Exception as e:
        logging.error(f"Failed to initialize UserClient: {e}")
    
    try:
        book_client = BookClient()
        logging.info("✓ BookClient initialized")
    except Exception as e:
        logging.error(f"Failed to initialize BookClient: {e}")
    
    try:
        borrowing_client = BorrowingClient()
        logging.info("✓ BorrowingClient initialized")
    except Exception as e:
        logging.error(f"Failed to initialize BorrowingClient: {e}")


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

# Initialize clients before first request
@app.before_request
def before_first_request():
    global user_client, book_client, borrowing_client
    if user_client is None or book_client is None or borrowing_client is None:
        initialize_clients()

# ------------------------
# User routes
# ------------------------
@app.route("/users", methods=["POST"])
def create_user():
    if not user_client:
        return jsonify({"error": "User service not available"}), 503
    
    data = request.json
    response = user_client.create_user(data["name"], data["email"], data["password"],data["user_type"])
    return jsonify({
        "id": response.user.id,
        "name": response.user.name,
        "email": response.user.email,
        "password": response.user.email,
        "user_type": response.user.user_type
    })

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    if not user_client:
        return jsonify({"error": "User service not available"}), 503
    try:
        response = user_client.get_user(user_id)
        return jsonify({
            "id": response.user.id,
            "name": response.user.name,
            "email": response.user.email,
            # "user_type": response.user_type
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

@app.route("/users", methods=["GET"])
def list_users():
    response = user_client.list_users()
    return jsonify({
        "users": [
            {"id": u.id, "name": u.name, "email": u.email}
            for u in response.users
        ]
    })

# ------------------------
# Book routes
# ------------------------
@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    response = book_client.add_book(data["title"], data["author"], data["isbn"])
    return jsonify({
        "id": response.book.id,
        "title": response.book.title,
        "author": response.book.author,
        "isbn": response.book.isbn,
        "status": response.book.status
    })

@app.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    try:
        response = book_client.get_book(book_id)
        return jsonify({
            "id": response.book.id,
            "title": response.book.title,
            "author": response.book.author,
            "isbn": response.book.isbn,
            "status": response.book.status
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

@app.route("/books", methods=["GET"])
def list_books():
    response = book_client.list_books()
    return jsonify({
        "books": [
            {"id": b.id, "title": b.title, "author": b.author,
             "isbn": b.isbn, "status": b.status}
            for b in response.books
        ]
    })

@app.route("/books/<book_id>/status", methods=["PATCH"])
def update_book_status(book_id):
    data = request.json
    try:
        response = book_client.update_book_status(book_id, data["status"])
        return jsonify({
            "id": response.book.id,
            "title": response.book.title,
            "author": response.book.author,
            "isbn": response.book.isbn,
            "status": response.book.status
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

# ------------------------
# Borrowing routes
# ------------------------
@app.route("/borrowings", methods=["POST"])
def borrow_book():
    data = request.json
    response = borrowing_client.borrow_book(data["user_id"], data["book_id"])
    return jsonify({
        "borrow_id": response.borrow_id,
        "status": response.status
    })

@app.route("/borrowings/<borrow_id>/return", methods=["POST"])
def return_book(borrow_id):
    try:
        response = borrowing_client.return_book(borrow_id)
        return jsonify({"status": response.status})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

@app.route("/users/<user_id>/borrowings", methods=["GET"])
def get_user_borrowings(user_id):
    response = borrowing_client.get_borrowed_books(user_id)
    return jsonify({
        "borrowed_books": [
            {
                "borrow_id": b.borrow_id,
                "user_id": b.user_id,
                "book_id": b.book_id,
                "borrowed_date": b.borrowed_date,
                "due_date": b.due_date
            }
            for b in response.borrowed_books
        ]
    })

# Error handler
@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Error: {error}")
    return jsonify({"error": str(error)}), 500


# ------------------------
# Run Flask Gateway
# ------------------------
if __name__ == "__main__":
    logging.info("Starting Flask Gateway...")
    app.run(host="0.0.0.0", port=8000, debug=True)