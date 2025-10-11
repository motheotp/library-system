from sqlalchemy.orm import Session
from . import models
import uuid
from datetime import datetime, timedelta

# ------------------------------
# CRUD Operations
# ------------------------------

def create_borrow(db: Session, user_id: str, book_id: str, due_days: int = 14):
    borrow = models.BorrowedBook(
        borrow_id=str(uuid.uuid4()),
        user_id=user_id,
        book_id=book_id,
        due_date=datetime.utcnow() + timedelta(days=due_days)
    )
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

def return_borrow(db: Session, borrow_id: str):
    borrow = db.query(models.BorrowedBook).filter(models.BorrowedBook.borrow_id == borrow_id).first()
    if not borrow:
        return None

    # Mark as returned instead of deleting
    borrow.returned = True
    borrow.returned_date = datetime.utcnow()

    # Calculate fine if overdue (e.g., $1 per day)
    if borrow.is_overdue():
        days_over = borrow.days_overdue()
        borrow.fine_amount = days_over * 1.0  # $1 per day fine

    db.commit()
    db.refresh(borrow)
    return borrow

def get_borrowed_books_by_user(db: Session, user_id: str):
    return db.query(models.BorrowedBook).filter(
        models.BorrowedBook.user_id == user_id,
        models.BorrowedBook.returned == False
    ).all()

def get_overdue_books(db: Session):
    """Get all overdue borrowings"""
    now = datetime.utcnow()
    return db.query(models.BorrowedBook).filter(
        models.BorrowedBook.returned == False,
        models.BorrowedBook.due_date < now
    ).all()

def get_all_borrowings(db: Session):
    """Get all borrowing records"""
    return db.query(models.BorrowedBook).all()
