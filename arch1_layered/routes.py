from flask import Blueprint, request, jsonify
from services import UserService, BookService, BorrowingService, ReservationService, StatisticsService

def create_routes(user_service: UserService, book_service: BookService, 
                 borrowing_service: BorrowingService, reservation_service: ReservationService,
                 statistics_service: StatisticsService):
    
    # Create Blueprint
    api = Blueprint('api', __name__, url_prefix='/api')
    
    # Health check endpoint
    @api.route('/health', methods=['GET'])
    def health_check():
        """System health check"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    # User Management Routes
    @api.route('/users/register', methods=['POST'])
    def register_user():
        """Register a new user"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            success, message, user = user_service.create_user(
                student_id=data.get('student_id'),
                name=data.get('name'),
                email=data.get('email'),
                role=data.get('role', 'student')
            )
            
            if success:
                return jsonify({
                    'message': message,
                    'user': user.to_dict()
                }), 201
            else:
                return jsonify({'error': message}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        """Get user by ID"""
        user = user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': user.to_dict()})
    
    @api.route('/users/login', methods=['POST'])
    def login_user():
        """Simple user authentication"""
        try:
            data = request.get_json()
            if not data or 'student_id' not in data:
                return jsonify({'error': 'Student ID is required'}), 400
            
            success, message, user = user_service.authenticate_user(data['student_id'])
            
            if success:
                return jsonify({
                    'message': message,
                    'user': user.to_dict()
                })
            else:
                return jsonify({'error': message}), 401
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Book Management Routes
    @api.route('/books', methods=['GET'])
    def get_books():
        """Get books with pagination and filtering"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        category = request.args.get('category')
        
        result = book_service.get_books(page=page, per_page=per_page, category=category)
        return jsonify(result)
    
    @api.route('/books/search', methods=['GET'])
    def search_books():
        """Search books by title or author"""
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query parameter "q" is required'}), 400
        
        result = book_service.search_books(query)
        return jsonify(result)
    
    @api.route('/books/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        """Get book details by ID"""
        book = book_service.get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify({'book': book.to_dict()})
    
    @api.route('/books/popular', methods=['GET'])
    def get_popular_books():
        """Get most popular books"""
        limit = request.args.get('limit', 10, type=int)
        popular_books = book_service.get_popular_books(limit=limit)
        return jsonify({'popular_books': popular_books})
    
    # Borrowing Routes
    @api.route('/borrow', methods=['POST'])
    def borrow_book():
        """Borrow a book"""
        try:
            data = request.get_json()
            if not data or 'user_id' not in data or 'book_id' not in data:
                return jsonify({'error': 'user_id and book_id are required'}), 400
            
            success, message, borrowing = borrowing_service.borrow_book(
                user_id=data['user_id'],
                book_id=data['book_id']
            )
            
            if success:
                return jsonify({
                    'message': message,
                    'borrowing': borrowing.to_dict()
                })
            else:
                return jsonify({'error': message}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/return/<int:borrowing_id>', methods=['POST'])
    def return_book(borrowing_id):
        """Return a borrowed book"""
        try:
            success, message, borrowing = borrowing_service.return_book(borrowing_id)
            
            if success:
                return jsonify({
                    'message': message,
                    'borrowing': borrowing.to_dict()
                })
            else:
                return jsonify({'error': message}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api.route('/users/<int:user_id>/borrowed', methods=['GET'])
    def get_user_borrowed_books(user_id):
        """Get user's currently borrowed books"""
        result = borrowing_service.get_user_borrowed_books(user_id)
        return jsonify(result)
    
    @api.route('/overdue', methods=['GET'])
    def get_overdue_books():
        """Get all overdue books (admin only)"""
        overdue_books = borrowing_service.get_overdue_books()
        return jsonify({
            'overdue_books': overdue_books,
            'count': len(overdue_books)
        })
    
    # Reservation Routes
    @api.route('/reserve', methods=['POST'])
    def create_reservation():
        """Create a book reservation"""
        try:
            data = request.get_json()
            if not data or 'user_id' not in data or 'book_id' not in data:
                return jsonify({'error': 'user_id and book_id are required'}), 400
            
            success, message, reservation = reservation_service.create_reservation(
                user_id=data['user_id'],
                book_id=data['book_id']
            )
            
            if success:
                return jsonify({
                    'message': message,
                    'reservation': reservation.to_dict()
                }), 201
            else:
                return jsonify({'error': message}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Statistics and Admin Routes
    @api.route('/admin/stats', methods=['GET'])
    def get_statistics():
        """Get system statistics"""
        stats = statistics_service.get_system_statistics()
        return jsonify(stats)
    
    return api