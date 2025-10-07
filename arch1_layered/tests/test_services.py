import pytest
from datetime import datetime, timedelta
from services import (
    CacheService, UserService, BookService,
    BorrowingService, ReservationService, StatisticsService
)
from models import User, Book, Borrowing, Reservation, db
from config import Config

class TestCacheService:
    """Test suite for CacheService"""

    def test_cache_service_initialization(self, app_context):
        """Test cache service initializes correctly"""
        cache = CacheService(app_context.config)
        assert cache is not None

    def test_cache_set_get(self, app_context):
        """Test setting and getting cache values"""
        cache = CacheService(app_context.config)

        if cache.cache_enabled:
            result = cache.set('test_key', 'test_value')
            assert result == True

            value = cache.get('test_key')
            assert value == 'test_value'

    def test_cache_delete(self, app_context):
        """Test deleting cache values"""
        cache = CacheService(app_context.config)

        if cache.cache_enabled:
            cache.set('test_key', 'test_value')
            result = cache.delete('test_key')

            value = cache.get('test_key')
            assert value is None

    def test_cache_expiry(self, app_context):
        """Test cache expiry works"""
        cache = CacheService(app_context.config)

        if cache.cache_enabled:
            # Set with 1 second expiry
            cache.set('expire_key', 'expire_value', expiry=1)

            import time
            time.sleep(2)

            value = cache.get('expire_key')
            assert value is None

    def test_cache_clear_pattern(self, app_context):
        """Test clearing cache by pattern"""
        cache = CacheService(app_context.config)

        if cache.cache_enabled:
            cache.set('books:1', 'value1')
            cache.set('books:2', 'value2')
            cache.set('users:1', 'value3')

            count = cache.clear_pattern('books:*')
            assert count >= 2

            # books should be cleared
            assert cache.get('books:1') is None
            # users should remain
            assert cache.get('users:1') == 'value3'


class TestUserService:
    """Test suite for UserService"""

    def test_create_user_success(self, app_context):
        """Test successful user creation"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)

        success, message, user = user_service.create_user(
            student_id='TEST001',
            name='Test User',
            email='test@example.com',
            role='student'
        )

        assert success == True
        assert user is not None
        assert user.student_id == 'TEST001'

    def test_create_user_duplicate_student_id(self, app_context, sample_users):
        """Test creating user with duplicate student ID"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)

        success, message, user = user_service.create_user(
            student_id='STU001',  # Already exists
            name='Different Name',
            email='different@example.com'
        )

        assert success == False
        assert 'already exists' in message

    def test_create_user_missing_fields(self, app_context):
        """Test creating user with missing fields"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)

        success, message, user = user_service.create_user(
            student_id='',
            name='Test User',
            email='test@example.com'
        )

        assert success == False
        assert 'required' in message

    def test_get_user_by_id(self, app_context, sample_users):
        """Test getting user by ID"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)

        user = user_service.get_user_by_id(sample_users[0].id)

        assert user is not None
        assert user.student_id == 'STU001'

    def test_authenticate_user_success(self, app_context, sample_users):
        """Test successful user authentication"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)

        success, message, user = user_service.authenticate_user('STU001')

        assert success == True
        assert user is not None

    def test_authenticate_user_not_found(self, app_context):
        """Test authentication with non-existent user"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)

        success, message, user = user_service.authenticate_user('NONEXISTENT')

        assert success == False
        assert user is None


class TestBookService:
    """Test suite for BookService"""

    def test_get_books_pagination(self, app_context, sample_books):
        """Test getting books with pagination"""
        cache = CacheService(app_context.config)
        book_service = BookService(cache)

        result = book_service.get_books(page=1, per_page=2)

        assert 'books' in result
        assert 'pagination' in result
        assert len(result['books']) <= 2

    def test_get_books_by_category(self, app_context, sample_books):
        """Test filtering books by category"""
        cache = CacheService(app_context.config)
        book_service = BookService(cache)

        result = book_service.get_books(category='Programming')

        assert all(book['category'] == 'Programming' for book in result['books'])

    def test_search_books(self, app_context, sample_books):
        """Test searching books"""
        cache = CacheService(app_context.config)
        book_service = BookService(cache)

        result = book_service.search_books('Python')

        assert result['count'] > 0
        assert any('Python' in book['title'] for book in result['books'])

    def test_search_books_empty_query(self, app_context, sample_books):
        """Test search with empty query"""
        cache = CacheService(app_context.config)
        book_service = BookService(cache)

        result = book_service.search_books('   ')

        assert 'error' in result

    def test_get_book_by_id(self, app_context, sample_books):
        """Test getting book by ID"""
        cache = CacheService(app_context.config)
        book_service = BookService(cache)

        book = book_service.get_book_by_id(sample_books[0].id)

        assert book is not None
        assert book.title == 'Python Programming'

    def test_get_popular_books(self, app_context, sample_books, sample_users):
        """Test getting popular books"""
        # Create some borrowings
        borrowing = Borrowing(
            user_id=sample_users[0].id,
            book_id=sample_books[0].id,
            borrowed_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            returned=True
        )
        db.session.add(borrowing)
        db.session.commit()

        cache = CacheService(app_context.config)
        book_service = BookService(cache)

        popular = book_service.get_popular_books(limit=5)

        assert len(popular) > 0
        assert 'borrow_count' in popular[0]


class TestBorrowingService:
    """Test suite for BorrowingService"""

    def test_borrow_book_success(self, app_context, sample_users, sample_books):
        """Test successful book borrowing"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        success, message, borrowing = borrowing_service.borrow_book(
            user_id=sample_users[0].id,
            book_id=sample_books[0].id
        )

        assert success == True
        assert borrowing is not None
        assert borrowing.returned == False

    def test_borrow_unavailable_book(self, app_context, sample_users, sample_books):
        """Test borrowing unavailable book"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        # sample_books[3] has 0 available copies
        success, message, borrowing = borrowing_service.borrow_book(
            user_id=sample_users[0].id,
            book_id=sample_books[3].id
        )

        assert success == False
        assert 'not available' in message

    def test_borrow_limit_exceeded(self, app_context, sample_users, sample_books):
        """Test exceeding borrow limit"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        # Borrow 3 books
        for i in range(3):
            borrowing_service.borrow_book(
                user_id=sample_users[0].id,
                book_id=sample_books[i].id
            )

        # Try 4th book
        success, message, borrowing = borrowing_service.borrow_book(
            user_id=sample_users[0].id,
            book_id=sample_books[4].id
        )

        assert success == False
        assert 'limit' in message.lower()

    def test_return_book_success(self, app_context, sample_borrowing):
        """Test successful book return"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        success, message, borrowing = borrowing_service.return_book(sample_borrowing.id)

        assert success == True
        assert borrowing.returned == True
        assert borrowing.returned_date is not None

    def test_return_overdue_book(self, app_context, overdue_borrowing):
        """Test returning overdue book calculates fine"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        success, message, borrowing = borrowing_service.return_book(overdue_borrowing.id)

        assert success == True
        assert borrowing.fine_amount > 0

    def test_get_user_borrowed_books(self, app_context, sample_borrowing, sample_users):
        """Test getting user's borrowed books"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        result = borrowing_service.get_user_borrowed_books(sample_users[0].id)

        assert result['count'] > 0
        assert len(result['borrowed_books']) > 0

    def test_get_overdue_books(self, app_context, overdue_borrowing):
        """Test getting overdue books"""
        cache = CacheService(app_context.config)
        user_service = UserService(cache)
        book_service = BookService(cache)
        borrowing_service = BorrowingService(cache, user_service, book_service)

        overdue_books = borrowing_service.get_overdue_books()

        assert len(overdue_books) > 0


class TestReservationService:
    """Test suite for ReservationService"""

    def test_create_reservation_success(self, app_context, sample_users, sample_books):
        """Test successful reservation creation"""
        cache = CacheService(app_context.config)
        reservation_service = ReservationService(cache)

        success, message, reservation = reservation_service.create_reservation(
            user_id=sample_users[0].id,
            book_id=sample_books[3].id
        )

        assert success == True
        assert reservation is not None
        assert reservation.status == 'active'

    def test_create_duplicate_reservation(self, app_context, sample_users, sample_books):
        """Test creating duplicate reservation"""
        cache = CacheService(app_context.config)
        reservation_service = ReservationService(cache)

        # First reservation
        reservation_service.create_reservation(
            user_id=sample_users[0].id,
            book_id=sample_books[3].id
        )

        # Duplicate reservation
        success, message, reservation = reservation_service.create_reservation(
            user_id=sample_users[0].id,
            book_id=sample_books[3].id
        )

        assert success == False
        assert 'already have a reservation' in message

    def test_reservation_priority_queue(self, app_context, sample_users, sample_books):
        """Test reservation priority assignment"""
        cache = CacheService(app_context.config)
        reservation_service = ReservationService(cache)

        # Create 2 reservations
        success1, _, res1 = reservation_service.create_reservation(
            user_id=sample_users[0].id,
            book_id=sample_books[3].id
        )

        success2, _, res2 = reservation_service.create_reservation(
            user_id=sample_users[1].id,
            book_id=sample_books[3].id
        )

        assert res1.priority == 1
        assert res2.priority == 2


class TestStatisticsService:
    """Test suite for StatisticsService"""

    def test_get_system_statistics(self, app_context, sample_users, sample_books):
        """Test getting system statistics"""
        cache = CacheService(app_context.config)
        stats_service = StatisticsService(cache)

        stats = stats_service.get_system_statistics()

        assert 'books' in stats
        assert 'users' in stats
        assert 'borrowings' in stats
        assert 'reservations' in stats

    def test_statistics_books_count(self, app_context, sample_books):
        """Test statistics counts books correctly"""
        cache = CacheService(app_context.config)
        stats_service = StatisticsService(cache)

        stats = stats_service.get_system_statistics()

        assert stats['books']['total'] == 5

    def test_statistics_users_by_role(self, app_context, sample_users):
        """Test statistics counts users by role"""
        cache = CacheService(app_context.config)
        stats_service = StatisticsService(cache)

        stats = stats_service.get_system_statistics()

        assert stats['users']['students'] == 3
        assert stats['users']['librarians'] == 1

    def test_statistics_active_borrowings(self, app_context, sample_borrowing):
        """Test statistics counts active borrowings"""
        cache = CacheService(app_context.config)
        stats_service = StatisticsService(cache)

        stats = stats_service.get_system_statistics()

        assert stats['borrowings']['active'] >= 1

    def test_statistics_overdue_count(self, app_context, overdue_borrowing):
        """Test statistics counts overdue borrowings"""
        cache = CacheService(app_context.config)
        stats_service = StatisticsService(cache)

        stats = stats_service.get_system_statistics()

        assert stats['borrowings']['overdue'] >= 1
