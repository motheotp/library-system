# crud.py
import uuid
from sqlalchemy.orm import Session
from . import models

def create_book(db: Session, title: str, author: str, isbn: str, category: str = None, description: str = None, total_copies: int = 1):
    """Add a new book to the database."""
    book = models.Book(
        id=str(uuid.uuid4()),
        title=title,
        author=author,
        isbn=isbn,
        category=category,
        description=description,
        total_copies=total_copies,
        available_copies=total_copies,
        status="available"
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: str):
    """Fetch a single book by ID."""
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def list_books(db: Session):
    """Retrieve all books."""
    return db.query(models.Book).all()


def update_book_status(db: Session, book_id: str, new_status: str):
    """Update the status of a book (e.g., borrowed, available)."""
    book = get_book(db, book_id)
    if not book:
        return None

    book.status = new_status
    db.commit()
    db.refresh(book)
    return book


def update_available_copies(db: Session, book_id: str, increment: int):
    """Update the available copies of a book (increment can be positive or negative)."""
    book = get_book(db, book_id)
    if not book:
        return None

    # Update available_copies
    new_available = book.available_copies + increment

    # Ensure available_copies doesn't go below 0 or above total_copies
    if new_available < 0:
        new_available = 0
    elif new_available > book.total_copies:
        new_available = book.total_copies

    book.available_copies = new_available

    # Update status based on availability
    if book.available_copies == 0:
        book.status = "borrowed"
    else:
        book.status = "available"

    db.commit()
    db.refresh(book)
    return book
