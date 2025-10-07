import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import os
from app import create_app
from models import db, User, Book, Borrowing, Reservation
from datetime import datetime, timedelta

@pytest.fixture(scope='session')
def test_app():
    """Create and configure a test application instance"""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'

    app = create_app('development')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': 6379,
        'MAX_BORROWING_LIMIT': 3,
        'LOAN_PERIOD_DAYS': 14
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """Create a test client for the app"""
    return test_app.test_client()

@pytest.fixture(scope='function')
def app_context(test_app):
    """Provide application context for tests"""
    with test_app.app_context():
        yield test_app

@pytest.fixture(scope='function', autouse=True)
def setup_database(app_context):
    """Clean database before each test"""
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield
    db.session.remove()

@pytest.fixture
def sample_users(app_context):
    """Create sample users for testing"""
    users = [
        User(student_id="STU001", name="John Student", email="john@university.edu", role="student"),
        User(student_id="STU002", name="Jane Learner", email="jane@university.edu", role="student"),
        User(student_id="STU003", name="Bob Reader", email="bob@university.edu", role="student"),
        User(student_id="LIB001", name="Library Admin", email="admin@library.edu", role="librarian")
    ]

    for user in users:
        db.session.add(user)
    db.session.commit()

    return users

@pytest.fixture
def sample_books(app_context):
    """Create sample books for testing"""
    books = [
        Book(
            title="Python Programming",
            author="John Doe",
            isbn="978-0123456789",
            category="Programming",
            description="Complete guide to Python programming",
            total_copies=3,
            available_copies=3
        ),
        Book(
            title="Data Structures and Algorithms",
            author="Jane Smith",
            isbn="978-0987654321",
            category="Computer Science",
            description="Fundamental concepts in data structures",
            total_copies=2,
            available_copies=2
        ),
        Book(
            title="Web Development with Flask",
            author="Bob Johnson",
            isbn="978-0456789123",
            category="Web Development",
            description="Building web applications with Flask",
            total_copies=4,
            available_copies=4
        ),
        Book(
            title="Database Systems",
            author="Alice Brown",
            isbn="978-0789123456",
            category="Database",
            description="Introduction to database management systems",
            total_copies=1,
            available_copies=0  # Not available
        ),
        Book(
            title="Machine Learning Basics",
            author="Charlie Davis",
            isbn="978-0321654987",
            category="AI",
            description="Getting started with machine learning",
            total_copies=3,
            available_copies=3
        )
    ]

    for book in books:
        db.session.add(book)
    db.session.commit()

    return books

@pytest.fixture
def sample_borrowing(app_context, sample_users, sample_books):
    """Create a sample borrowing record"""
    borrowing = Borrowing(
        user_id=sample_users[0].id,
        book_id=sample_books[0].id,
        borrowed_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        returned=False
    )

    # Update book availability
    sample_books[0].available_copies -= 1

    db.session.add(borrowing)
    db.session.commit()

    return borrowing

@pytest.fixture
def overdue_borrowing(app_context, sample_users, sample_books):
    """Create an overdue borrowing record"""
    borrowing = Borrowing(
        user_id=sample_users[1].id,
        book_id=sample_books[1].id,
        borrowed_date=datetime.utcnow() - timedelta(days=20),
        due_date=datetime.utcnow() - timedelta(days=6),  # 6 days overdue
        returned=False
    )

    # Update book availability
    sample_books[1].available_copies -= 1

    db.session.add(borrowing)
    db.session.commit()

    return borrowing

@pytest.fixture
def sample_reservation(app_context, sample_users, sample_books):
    """Create a sample reservation record"""
    reservation = Reservation(
        user_id=sample_users[2].id,
        book_id=sample_books[3].id,  # Book that's not available
        reserved_date=datetime.utcnow(),
        status='active',
        priority=1
    )

    db.session.add(reservation)
    db.session.commit()

    return reservation
