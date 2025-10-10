# crud.py
import uuid
from sqlalchemy.orm import Session
from . import models

def create_book(db: Session, title: str, author: str, isbn: str):
    """Add a new book to the database."""
    book = models.Book(
        id=str(uuid.uuid4()),
        title=title,
        author=author,
        isbn=isbn,
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
