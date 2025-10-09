from collections import UserList
import redis
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from models import db, User, Book, Borrowing, Reservation
from config import Config

class CacheService:

    def __init__(self, config: Config):
        try:
            self.redis_client = redis.Redis(
                host=config.get('REDIS_HOST', 'localhost'),
                port=config.get('REDIS_PORT', 6379),
                db=config.get('REDIS_DB', 0),
                decode_responses=True
            )
            self.redis_client.ping()
            self.cache_enabled = True
            print("Redis cache connected successfully")
        
        except Exception as e:
            self.redis_client=None
            self.cache_enabled=False
            print(f"Redis cache not available: {e}")

    def get(self, key: str) -> Optional[str]:
        if not self.cache_enabled:
            return None
        try:
            return self.redis_client.get(key)
        except Exception:
            return None
    
    def set(self, key: str, value: str, expiry: int = 300) -> bool:
        if not self.cache_enabled:
            return False
        try:
            return self.redis_client.setex(key, expiry, value)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        if not self.cache_enabled:
            return False
        try:
            return self.redis_client.delete(key) > 0
        except Exception:
            return False

    def clear_pattern(self, pattern: str) -> int:
        if not self.cache_enabled:
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0


class UserService:
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service

    def create_user(self, student_id: str, name: str, email: str, role: str = 'student') -> Tuple[bool, str, Optional[User]]:
        try:
            if not all([student_id, name, email]):
                return False, "All fields (student_id, name, email) are required", None
            
            existing_user = User.query.filter(
                (User.student_id == student_id) | (User.email == email)
            ).first()

            if existing_user:
                return False, "User with this student ID or email already exists", None
            
            user = User(student_id=student_id,
                        name=name,
                        email=email,
                        role=role)
            
            db.session.add(user)
            db.session.commit()

            return True, "User created successfully", user

        except Exception as e:
            db.session.rollback()
            return False, f"Error creating user: {str(e)}", None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return User.query.get(user_id)

    def get_user_by_student_id(self, student_id:str) -> Optional[User]:
        return User.query.filter_by(student_id=student_id).first()

    def authenticate_user(self, student_id: str) -> Tuple[bool, str, Optional[User]]:
        user = self.get_user_by_student_id(student_id)
        if user:
            return True, "Authentication successful", user
        return False, "User not found", None

class BookService:

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service

    def get_books(self, page: int=1, per_page: int=10, category: str=None) -> Dict:
        try:
            cache_key = f"books:page:{page}:per_page:{per_page}:category:{category or 'all'}"
            cached_result = self.cache.get(cache_key)

            if cached_result:
                return {**json.loads(cached_result), 'source': 'cache'}
            
            query = Book.query.filter(Book.available_copies > 0)

            if category:
                query = query.filter(Book.category == category)
            
            paginated_books = query.paginate(
                page=page, per_page=per_page, error_out=False
            )

            result = {
                'books': [book.to_dict() for book in paginated_books.items],
                'pagination': {
                    'page': page,
                    'pages': paginated_books.pages,
                    'total': paginated_books.total,
                    'has_next': paginated_books.has_next,
                    'has_prev': paginated_books.has_prev
                },
                'source': 'database'
            }

            self.cache.set(cache_key, json.dumps({
                'books': result['books'],
                'pagination': result['pagination']
            }), 300)

            return result

        except Exception as e:
            return {'error': str(e), 'books': [], 'pagination': {}}

    def search_books(self, query: str) -> Dict:
        try:
            if not query.strip():
                return {'error': 'Search query cannot be empty', 'books': []}

            cache_key = f"search:{query.lower().strip()}"
            cached_result = self.cache.get(cache_key)

            if cached_result:
                return {**json.loads(cached_result), 'source': 'cache'}

            search_term = f"%{query}%"
            books = Book.query.filter(
                (Book.title.ilike(search_term)) | (Book.author.ilike(search_term))
            ).filter(Book.available_copies > 0).all()

            result = {
                'books': [book.to_dict() for book in books],
                'query': query,
                'count': len(books),
                'source': 'database'
            }

            self.cache.set(cache_key, json.dumps({
                'books': result['books'],
                'query': result['query'],
                'count': result['count']
            }), 600)

            return result
        
        except Exception as e:
            return {'error': str(e), 'books': [], 'query': query, 'count': 0}

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        return db.session.get(Book, book_id)

    def get_popular_books(self, limit: int=10) -> List[Dict]:
        try:
            popular_books = db.session.query(Book, db.func.count(Borrowing.id).label('borrow_count')).join(
                Borrowing, Book.id == Borrowing.book_id
            ).group_by(Book.id).order_by(db.desc('borrow_count')).limit(limit).all()

            return [{
                **book.to_dict(),
                'borrow_count': count
            } for book, count in popular_books]

        
        except Exception as e:
            return []


class BorrowingService:
    def __init__(self, cache_service: CacheService, user_service: UserService, book_service: BookService):
        self.cache = cache_service
        self.user_service = user_service
        self.book_service = book_service

    def borrow_book(self, user_id: int, book_id: int, loan_days: int = 14) -> Tuple[bool, str, Optional[Borrowing]]:
        """Process book borrowing"""
        try:
            # Get user and book
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return False, "User not found", None
            
            book = self.book_service.get_book_by_id(book_id)
            if not book:
                return False, "Book not found", None
            
            # Check if book is available
            if not book.is_available():
                return False, "Book is not available", None
            
            # Check user's borrowing limit
            if not user.can_borrow_book():
                return False, f"Borrowing limit reached (maximum {Config.MAX_BORROWING_LIMIT} books)", None
            
            # Check if user already has this book
            existing_borrowing = Borrowing.query.filter_by(
                user_id=user_id, book_id=book_id, returned=False
            ).first()
            
            if existing_borrowing:
                return False, "You already have this book borrowed", None
            
            # Create borrowing record
            due_date = datetime.now(timezone.utc) + timedelta(days=loan_days)
            borrowing = Borrowing(
                user_id=user_id,
                book_id=book_id,
                due_date=due_date
            )
            
            # Update book availability
            book.borrow_copy()
            
            # Save to database
            db.session.add(borrowing)
            db.session.commit()
            
            # Clear relevant cache
            self.cache.clear_pattern('books:*')
            self.cache.clear_pattern(f'user:{user_id}:*')
            
            return True, "Book borrowed successfully", borrowing
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error borrowing book: {str(e)}", None
    
    def return_book(self, borrowing_id: int) -> Tuple[bool, str, Optional[Borrowing]]:
        """Process book return"""
        try:
            borrowing = Borrowing.query.get(borrowing_id)
            if not borrowing:
                return False, "Borrowing record not found", None
            
            if borrowing.returned:
                return False, "Book already returned", None

            # Calculate fine if overdue (BEFORE marking as returned)
            if borrowing.is_overdue():
                days_overdue = borrowing.days_overdue()
                borrowing.fine_amount = days_overdue * 1.0  # $1 per day

            # Mark as returned
            borrowing.returned = True
            borrowing.returned_date = datetime.now(timezone.utc)
            
            # Update book availability
            book = db.session.get(Book, borrowing.book_id)
            book.return_copy()
            
            db.session.commit()
            
            # Clear relevant cache
            self.cache.clear_pattern('books:*')
            self.cache.clear_pattern(f'user:{borrowing.user_id}:*')
            
            return True, "Book returned successfully", borrowing
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error returning book: {str(e)}", None
    
    def get_user_borrowed_books(self, user_id: int) -> Dict:
        """Get user's currently borrowed books"""
        try:
            # Check cache
            cache_key = f'user:{user_id}:borrowed'
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                return {**json.loads(cached_result), 'source': 'cache'}
            
            # Query database
            borrowings = db.session.query(Borrowing, Book).join(
                Book, Borrowing.book_id == Book.id
            ).filter(
                Borrowing.user_id == user_id,
                Borrowing.returned == False
            ).all()
            
            borrowed_books = []
            for borrowing, book in borrowings:
                # Handle both naive and aware datetimes for days_remaining
                due = borrowing.due_date
                now = datetime.now(timezone.utc)
                if due.tzinfo is None:
                    now = datetime.utcnow()

                borrowed_book_data = {
                    'borrowing': borrowing.to_dict(),
                    'book': book.to_dict(),
                    'days_remaining': (due - now).days
                }
                borrowed_books.append(borrowed_book_data)
            
            result = {
                'borrowed_books': borrowed_books,
                'count': len(borrowed_books),
                'user_id': user_id,
                'source': 'database'
            }
            
            # Cache result
            self.cache.set(cache_key, json.dumps({
                'borrowed_books': result['borrowed_books'],
                'count': result['count'],
                'user_id': result['user_id']
            }), 300)
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'borrowed_books': [], 'count': 0, 'user_id': user_id}
    
    def get_overdue_books(self) -> List[Dict]:
        """Get all overdue books"""
        try:
            overdue_borrowings = db.session.query(Borrowing, Book, User).join(
                Book, Borrowing.book_id == Book.id
            ).join(
                User, Borrowing.user_id == User.id
            ).filter(
                Borrowing.returned == False,
                Borrowing.due_date < datetime.now(timezone.utc)
            ).all()
            
            overdue_books = []
            for borrowing, book, user in overdue_borrowings:
                overdue_books.append({
                    'borrowing': borrowing.to_dict(),
                    'book': book.to_dict(),
                    'user': user.to_dict()
                })
            
            return overdue_books
            
        except Exception as e:
            return []

class ReservationService:
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def create_reservation(self, user_id: int, book_id: int) -> Tuple[bool, str, Optional[Reservation]]:
        try:
            # Check if user already has this book reserved
            existing_reservation = Reservation.query.filter_by(
                user_id=user_id, book_id=book_id, status='active'
            ).first()
            
            if existing_reservation:
                return False, "You already have a reservation for this book", None
            
            # Get next priority number
            max_priority = db.session.query(db.func.max(Reservation.priority)).filter_by(
                book_id=book_id, status='active'
            ).scalar() or 0
            
            reservation = Reservation(
                user_id=user_id,
                book_id=book_id,
                priority=max_priority + 1
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            return True, "Reservation created successfully", reservation
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating reservation: {str(e)}", None

class StatisticsService:
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def get_system_statistics(self) -> Dict:
        try:
            # Check cache
            cache_key = "system:statistics"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                return {**json.loads(cached_result), 'source': 'cache'}
            
            stats = {
                'books': {
                    'total': Book.query.count(),
                    'available': Book.query.filter(Book.available_copies > 0).count(),
                    'borrowed': Book.query.filter(Book.available_copies < Book.total_copies).count()
                },
                'users': {
                    'total': User.query.count(),
                    'students': User.query.filter_by(role='student').count(),
                    'librarians': User.query.filter_by(role='librarian').count()
                },
                'borrowings': {
                    'total': Borrowing.query.count(),
                    'active': Borrowing.query.filter_by(returned=False).count(),
                    'overdue': Borrowing.query.filter(
                        Borrowing.returned == False,
                        Borrowing.due_date < datetime.now(timezone.utc)
                    ).count()
                },
                'reservations': {
                    'active': Reservation.query.filter_by(status='active').count()
                },
                'generated_at': datetime.now(timezone.utc).isoformat()
            }

            self.cache.set(cache_key, json.dumps(stats), 180)  # 3 minutes
            
            return {**stats, 'source': 'database'}
            
        except Exception as e:
            return {'error': str(e)}