from flask import Flask
from flask_cors import CORS
from config import config
from models import db
from services import (CacheService, UserService, BookService, 
                     BorrowingService, ReservationService, StatisticsService)
from routes import create_routes
import os

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize services
    cache_service = CacheService(app.config)
    user_service = UserService(cache_service)
    book_service = BookService(cache_service)
    borrowing_service = BorrowingService(cache_service, user_service, book_service)
    reservation_service = ReservationService(cache_service)
    statistics_service = StatisticsService(cache_service)
    
    # Create and register routes
    api_blueprint = create_routes(
        user_service=user_service,
        book_service=book_service,
        borrowing_service=borrowing_service,
        reservation_service=reservation_service,
        statistics_service=statistics_service
    )
    
    app.register_blueprint(api_blueprint)
    
    # Create database tables and sample data
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    return app

def create_sample_data():
    """Create sample data for testing"""
    from models import User, Book
    
    # Check if data already exists
    if User.query.count() > 0:
        print("📚 Sample data already exists")
        return
    
    try:
        # Sample users
        users = [
            User(student_id="STU001", name="John Student", email="john@university.edu", role="student"),
            User(student_id="STU002", name="Jane Learner", email="jane@university.edu", role="student"),
            User(student_id="STU003", name="Bob Reader", email="bob@university.edu", role="student"),
            User(student_id="LIB001", name="Library Admin", email="admin@library.edu", role="librarian")
        ]
        
        # Sample books
        books = [
            Book(title="Python Programming", author="John Doe", isbn="978-0123456789", 
                 category="Programming", description="Complete guide to Python programming",
                 total_copies=3, available_copies=3),
            Book(title="Data Structures and Algorithms", author="Jane Smith", isbn="978-0987654321", 
                 category="Computer Science", description="Fundamental concepts in data structures",
                 total_copies=2, available_copies=2),
            Book(title="Web Development with Flask", author="Bob Johnson", isbn="978-0456789123", 
                 category="Web Development", description="Building web applications with Flask",
                 total_copies=4, available_copies=4),
            Book(title="Database Systems", author="Alice Brown", isbn="978-0789123456", 
                 category="Database", description="Introduction to database management systems",
                 total_copies=2, available_copies=2),
            Book(title="Machine Learning Basics", author="Charlie Davis", isbn="978-0321654987", 
                 category="AI", description="Getting started with machine learning",
                 total_copies=3, available_copies=3),
            Book(title="React.js Development", author="Sarah Wilson", isbn="978-0654987321", 
                 category="Web Development", description="Modern frontend development with React",
                 total_copies=2, available_copies=2),
            Book(title="System Design Interview", author="Alex Xu", isbn="978-0147258369", 
                 category="Interview Prep", description="Prepare for system design interviews",
                 total_copies=1, available_copies=1),
            Book(title="Clean Code", author="Robert Martin", isbn="978-0132350884", 
                 category="Software Engineering", description="Writing clean, maintainable code",
                 total_copies=2, available_copies=2)
        ]
        
        # Add to database
        for user in users:
            db.session.add(user)
        
        for book in books:
            db.session.add(book)
        
        db.session.commit()
        print("✅ Sample data created successfully")
        print(f"   - {len(users)} users added")
        print(f"   - {len(books)} books added")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")

if __name__ == '__main__':
    # Create the application
    app = create_app()
    
    print("🚀 Starting Flask Library Management System")
    print("📚 Layered Architecture Implementation")
    print("🌐 API Base URL: http://localhost:5000/api")
    print("🔍 Health Check: http://localhost:5000/api/health")
    print("📖 Available Endpoints:")
    print("   POST /api/users/register - Register new user")
    print("   GET  /api/books - List books")
    print("   GET  /api/books/search?q=python - Search books")
    print("   POST /api/borrow - Borrow a book")
    print("   POST /api/return/1 - Return a book")
    print("   GET  /api/admin/stats - System statistics")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )