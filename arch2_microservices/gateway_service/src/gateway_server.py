from flask import Flask, request, jsonify
from flask_cors import CORS
from src.user_client import UserClient
from src.book_client import BookClient
from src.borrowing_client import BorrowingClient
import grpc
import logging
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# Configure CORS to allow all methods and headers from frontend
CORS(app,
     origins=['http://localhost:3000'],
     methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True,
     max_age=3600)

logging.basicConfig(level=logging.INFO)

# Secret key for JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'microservices-secret-key')

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


# JWT token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = data['user_id']
            request.user_role = data.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated

# Health check endpoint
@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }), 200

# Initialize clients before first request
@app.before_request
def before_first_request():
    global user_client, book_client, borrowing_client
    if user_client is None or book_client is None or borrowing_client is None:
        initialize_clients()

# ------------------------
# Authentication routes
# ------------------------
@app.route("/api/users/register", methods=["POST"])
def register():
    if not user_client:
        return jsonify({"error": "User service not available"}), 503

    try:
        data = request.json

        # Map frontend user_type/role to proto enum
        user_type_map = {
            "user": 1,       # STUDENT
            "student": 1,    # STUDENT
            "admin": 2,      # STAFF
            "staff": 2,      # STAFF
            "librarian": 2   # STAFF
        }
        role = data.get("role", data.get("user_type", "student")).lower()
        user_type = user_type_map.get(role, 1)

        # Frontend might send student_id instead of password
        password = data.get("password", data.get("student_id", "default123"))

        response = user_client.create_user(
            data["name"],
            data["email"],
            password,
            user_type
        )

        # Generate JWT token
        token = jwt.encode({
            'user_id': response.user.id,
            'role': response.user.user_type,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            "token": token,
            "user": {
                "id": response.user.id,
                "student_id": response.user.student_id,
                "name": response.user.name,
                "email": response.user.email,
                "role": response.user.role
            }
        }), 201
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 400

@app.route("/api/users/login", methods=["POST"])
def login():
    if not user_client:
        return jsonify({"error": "User service not available"}), 503

    try:
        data = request.json
        if not data or 'student_id' not in data:
            return jsonify({"error": "Student ID is required"}), 400

        # Call user service to authenticate by student_id
        response = user_client.authenticate_user(data['student_id'])

        return jsonify({
            "message": response.message,
            "user": {
                "id": response.user.id,
                "student_id": response.user.student_id,
                "name": response.user.name,
                "email": response.user.email,
                "role": response.user.role
            }
        }), 200
    except grpc.RpcError as e:
        logging.error(f"Login error: {e.details()}")
        return jsonify({"error": "User not found"}), 401
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({"error": "Invalid credentials"}), 401

# ------------------------
# User routes
# ------------------------
@app.route("/api/users", methods=["POST"])
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

@app.route("/api/users/<user_id>", methods=["GET"])
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

@app.route("/api/users", methods=["GET"])
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
@app.route("/api/books", methods=["POST"])
def add_book():
    if not book_client:
        return jsonify({"error": "Book service not available"}), 503

    try:
        data = request.json
        response = book_client.add_book(
            data["title"],
            data["author"],
            data["isbn"],
            data.get("category", ""),
            data.get("description", ""),
            data.get("total_copies", 1)
        )
        return jsonify({
            "id": response.book.id,
            "title": response.book.title,
            "author": response.book.author,
            "isbn": response.book.isbn,
            "status": response.book.status,
            "category": response.book.category,
            "description": response.book.description,
            "total_copies": response.book.total_copies,
            "available_copies": response.book.available_copies
        })
    except grpc.RpcError as e:
        logging.error(f"Error adding book: {e}")
        return jsonify({"error": e.details()}), 500

@app.route("/api/books/<book_id>", methods=["GET"])
def get_book(book_id):
    try:
        response = book_client.get_book(book_id)
        return jsonify({
            "id": response.book.id,
            "title": response.book.title,
            "author": response.book.author,
            "isbn": response.book.isbn,
            "status": response.book.status,
            "category": response.book.category,
            "description": response.book.description,
            "total_copies": response.book.total_copies,
            "available_copies": response.book.available_copies
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

@app.route("/api/books", methods=["GET"])
def list_books():
    if not book_client:
        return jsonify({"error": "Book service not available"}), 503

    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 12))

        response = book_client.list_books()
        all_books = [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "isbn": b.isbn,
                "status": b.status,
                "available": b.status == "available",
                "category": b.category,
                "description": b.description,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies
            }
            for b in response.books
        ]

        # Paginate books
        total_books = len(all_books)
        total_pages = (total_books + limit - 1) // limit  # Ceiling division
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_books = all_books[start_idx:end_idx]

        return jsonify({
            "books": paginated_books,
            "pagination": {
                "page": page,
                "pages": total_pages,
                "total": total_books,
                "has_prev": page > 1,
                "has_next": page < total_pages
            }
        })
    except grpc.RpcError as e:
        logging.error(f"Error fetching books: {e}")
        return jsonify({"error": e.details()}), 500

@app.route("/api/books/<book_id>/status", methods=["PATCH"])
def update_book_status(book_id):
    data = request.json
    try:
        response = book_client.update_book_status(book_id, data["status"])
        return jsonify({
            "id": response.book.id,
            "title": response.book.title,
            "author": response.book.author,
            "isbn": response.book.isbn,
            "status": response.book.status,
            "category": response.book.category,
            "description": response.book.description,
            "total_copies": response.book.total_copies,
            "available_copies": response.book.available_copies
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

@app.route("/api/books/search", methods=["GET"])
def search_books():
    query = request.args.get('q', '')
    try:
        # Get all books and filter by query
        response = book_client.list_books()
        filtered_books = [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "isbn": b.isbn,
                "status": b.status,
                "available": b.status == "available",
                "category": b.category,
                "description": b.description,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies
            }
            for b in response.books
            if query.lower() in b.title.lower() or query.lower() in b.author.lower()
        ]
        return jsonify({"books": filtered_books})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 500

@app.route("/api/books/popular", methods=["GET"])
def get_popular_books():
    """Get popular books (most borrowed)"""
    if not book_client:
        return jsonify({"error": "Book service not available"}), 503

    try:
        limit = int(request.args.get('limit', 10))
        # For now, just return first N books
        # TODO: Implement actual popularity tracking
        response = book_client.list_books()
        popular_books = [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "isbn": b.isbn,
                "status": b.status,
                "available": b.status == "available",
                "category": b.category,
                "description": b.description,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies
            }
            for b in response.books[:limit]
        ]
        return jsonify({"books": popular_books})
    except grpc.RpcError as e:
        logging.error(f"Error fetching popular books: {e}")
        return jsonify({"error": e.details()}), 500

# ------------------------
# Borrowing routes
# ------------------------
@app.route("/api/borrowings", methods=["POST"])
def borrow_book():
    data = request.json
    response = borrowing_client.borrow_book(data["user_id"], data["book_id"])
    return jsonify({
        "borrow_id": response.borrow_id,
        "status": response.status
    })

@app.route("/api/borrowings/<borrow_id>/return", methods=["POST"])
def return_book(borrow_id):
    try:
        response = borrowing_client.return_book(borrow_id)
        return jsonify({"status": response.status})
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 404

@app.route("/api/users/<user_id>/borrowings", methods=["GET"])
def get_user_borrowings(user_id):
    if not borrowing_client:
        return jsonify({"error": "Borrowing service not available"}), 503

    try:
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
    except grpc.RpcError as e:
        logging.error(f"Error fetching borrowings: {e}")
        return jsonify({"error": e.details()}), 500

@app.route("/api/users/<user_id>/borrowed", methods=["GET"])
def get_user_borrowed_books(user_id):
    """Get user's borrowed books (frontend expects this endpoint)"""
    if not borrowing_client:
        return jsonify({"borrowed_books": []}), 200

    try:
        response = borrowing_client.get_borrowed_books(user_id)
        borrowed_books = []

        # Get book details for each borrowed book
        for b in response.borrowed_books:
            try:
                book_response = book_client.get_book(b.book_id)

                # Calculate days remaining
                from datetime import datetime, timezone
                try:
                    due_date = datetime.strptime(b.due_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    days_remaining = (due_date - now).days
                except:
                    days_remaining = 0

                borrowed_books.append({
                    "borrowing": {
                        "id": b.borrow_id,
                        "user_id": b.user_id,
                        "book_id": b.book_id,
                        "borrowed_date": b.borrowed_date,
                        "due_date": b.due_date,
                        "returned": b.returned,
                        "returned_date": b.returned_date if b.returned_date else None,
                        "fine_amount": b.fine_amount,
                        "is_overdue": b.is_overdue,
                        "days_overdue": b.days_overdue
                    },
                    "book": {
                        "id": book_response.book.id,
                        "title": book_response.book.title,
                        "author": book_response.book.author,
                        "isbn": book_response.book.isbn,
                        "category": book_response.book.category,
                        "description": book_response.book.description,
                        "status": book_response.book.status,
                        "total_copies": book_response.book.total_copies,
                        "available_copies": book_response.book.available_copies
                    },
                    "days_remaining": days_remaining
                })
            except grpc.RpcError:
                # Book not found, skip
                continue

        return jsonify({
            "borrowed_books": borrowed_books,
            "count": len(borrowed_books),
            "user_id": user_id
        })
    except grpc.RpcError as e:
        logging.error(f"Error fetching borrowed books: {e}")
        return jsonify({"borrowed_books": [], "count": 0, "user_id": user_id}), 200

@app.route("/api/return/<borrow_id>", methods=["POST"])
def return_book_by_id(borrow_id):
    """Return a borrowed book (frontend expects this endpoint)"""
    if not borrowing_client:
        return jsonify({"error": "Borrowing service not available"}), 503

    try:
        response = borrowing_client.return_book(borrow_id)

        # Build the borrowing object response
        borrowing_data = {
            "id": response.borrowing.borrow_id,
            "user_id": response.borrowing.user_id,
            "book_id": response.borrowing.book_id,
            "borrowed_date": response.borrowing.borrowed_date,
            "due_date": response.borrowing.due_date,
            "returned": response.borrowing.returned,
            "returned_date": response.borrowing.returned_date,
            "fine_amount": response.borrowing.fine_amount,
            "is_overdue": response.borrowing.is_overdue,
            "days_overdue": response.borrowing.days_overdue
        }

        return jsonify({
            "message": "Book returned successfully",
            "borrowing": borrowing_data
        })
    except grpc.RpcError as e:
        logging.error(f"Error returning book: {e}")
        return jsonify({"error": e.details()}), 400

@app.route("/api/overdue", methods=["GET"])
def get_all_overdue_books():
    """Get all overdue borrowed books"""
    if not borrowing_client:
        return jsonify({"overdue_books": []}), 200

    try:
        # TODO: Implement in borrowing service
        # For now return empty list
        return jsonify({"overdue_books": []})
    except Exception as e:
        logging.error(f"Error fetching overdue books: {e}")
        return jsonify({"overdue_books": []}), 200

# ------------------------
# Admin routes
# ------------------------
@app.route("/api/admin/stats", methods=["GET"])
def get_stats():
    """Get library statistics"""
    try:
        # Get all books
        books_response = book_client.list_books()
        total_books = len(books_response.books)
        available_books = sum(1 for b in books_response.books if b.status == "available")
        borrowed_books = total_books - available_books

        # Get all users
        users_response = user_client.list_users()
        total_users = len(users_response.users)

        return jsonify({
            "total_books": total_books,
            "available_books": available_books,
            "borrowed_books": borrowed_books,
            "total_users": total_users,
            "overdue_books": 0  # Placeholder - would need to query borrowing service
        })
    except grpc.RpcError as e:
        logging.error(f"Stats error: {e}")
        return jsonify({"error": e.details()}), 500

@app.route("/api/admin/overdue", methods=["GET"])
def get_overdue_books():
    """Get overdue borrowed books"""
    try:
        # Placeholder - would need to implement in borrowing service
        # For now return empty list
        return jsonify({
            "overdue": []
        })
    except grpc.RpcError as e:
        logging.error(f"Overdue books error: {e}")
        return jsonify({"error": e.details()}), 500

@app.route("/api/borrow", methods=["POST"])
def borrow_book_simple():
    """Simplified borrow endpoint for compatibility"""
    data = request.json
    try:
        response = borrowing_client.borrow_book(data["user_id"], data["book_id"])
        return jsonify({
            "borrow_id": response.borrow_id,
            "status": response.status,
            "message": "Book borrowed successfully"
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 400

@app.route("/api/return", methods=["POST"])
def return_book_simple():
    """Simplified return endpoint for compatibility"""
    data = request.json
    try:
        response = borrowing_client.return_book(data["borrow_id"])
        return jsonify({
            "status": response.status,
            "message": "Book returned successfully"
        })
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), 400

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    """Get user dashboard data"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    try:
        # Get user's borrowed books
        borrowings_response = borrowing_client.get_borrowed_books(user_id)

        return jsonify({
            "borrowed_books": [
                {
                    "borrow_id": b.borrow_id,
                    "user_id": b.user_id,
                    "book_id": b.book_id,
                    "borrowed_date": b.borrowed_date,
                    "due_date": b.due_date
                }
                for b in borrowings_response.borrowed_books
            ]
        })
    except grpc.RpcError as e:
        logging.error(f"Dashboard error: {e}")
        return jsonify({"error": e.details()}), 500

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