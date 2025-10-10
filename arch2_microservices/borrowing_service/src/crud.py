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
    db.delete(borrow)
    db.commit()
    return borrow

def get_borrowed_books_by_user(db: Session, user_id: str):
    return db.query(models.BorrowedBook).filter(models.BorrowedBook.user_id == user_id).all()
