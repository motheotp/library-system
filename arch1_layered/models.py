from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    borrowings = db.relationship('Borrowing', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<User {self.student_id}: {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_active_borrowings_count(self):
        """Get count of user's active borrowings"""
        return self.borrowings.filter_by(returned=False).count()
    
    def can_borrow_book(self, max_limit=3):
        """Check if user can borrow another book"""
        return self.get_active_borrowings_count() < max_limit

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, index=True)
    category = db.Column(db.String(50), index=True)
    description = db.Column(db.Text)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    borrowings = db.relationship('Borrowing', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='book', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

    def to_dict(self):
        """Convert book object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'description': self.description,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'is_available': self.available_copies > 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0
    
    def borrow_copy(self):
        """Decrease available copies when book is borrowed"""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
    
    def return_copy(self):
        """Increase available copies when book is returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False

class Borrowing(db.Model):
    """Borrowing model - represents book borrowing transactions"""
    __tablename__ = 'borrowings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    borrowed_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    returned_date = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, default=False, index=True)
    fine_amount = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Borrowing User:{self.user_id} Book:{self.book_id} Returned:{self.returned}>'
    
    def to_dict(self):
        """Convert borrowing object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrowed_date': self.borrowed_date.isoformat() if self.borrowed_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'returned_date': self.returned_date.isoformat() if self.returned_date else None,
            'returned': self.returned,
            'fine_amount': self.fine_amount,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue()
        }
    
    def is_overdue(self):
        """Check if borrowing is overdue"""
        if self.returned:
            return False

        # Handle both naive and aware datetimes (for SQLite compatibility)
        now = datetime.now(timezone.utc)
        due = self.due_date

        # If due_date is naive (from SQLite), make comparison naive
        if due.tzinfo is None:
            now = datetime.utcnow()

        return now > due

    def days_overdue(self):
        """Calculate days overdue"""
        if not self.is_overdue():
            return 0

        # Handle both naive and aware datetimes (for SQLite compatibility)
        now = datetime.now(timezone.utc)
        due = self.due_date

        # If due_date is naive (from SQLite), make comparison naive
        if due.tzinfo is None:
            now = datetime.utcnow()

        return (now - due).days

class Reservation(db.Model):
    """Reservation model - represents book reservations when not available"""
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    reserved_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, fulfilled, cancelled
    priority = db.Column(db.Integer, default=1)  # for queue ordering
    notified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Reservation User:{self.user_id} Book:{self.book_id} Status:{self.status}>'
    
    def to_dict(self):
        """Convert reservation object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'reserved_date': self.reserved_date.isoformat() if self.reserved_date else None,
            'status': self.status,
            'priority': self.priority,
            'notified': self.notified
        }