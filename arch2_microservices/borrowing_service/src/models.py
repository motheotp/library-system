from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer
from sqlalchemy.sql import func
from datetime import datetime, timezone
from .db import Base, engine

class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    borrow_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    book_id = Column(String, index=True, nullable=False)
    borrowed_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)

    # Added fields for compatibility with arch1
    returned_date = Column(DateTime(timezone=True), nullable=True)
    returned = Column(Boolean, default=False, index=True)
    fine_amount = Column(Float, default=0.0)

    def is_overdue(self):
        """Check if borrowing is overdue"""
        if self.returned:
            return False
        now = datetime.now(timezone.utc)
        return now > self.due_date if self.due_date else False

    def days_overdue(self):
        """Calculate days overdue"""
        if not self.is_overdue():
            return 0
        now = datetime.now(timezone.utc)
        return (now - self.due_date).days if self.due_date else 0


class Reservation(Base):
    """Reservation model - represents book reservations when not available"""
    __tablename__ = 'reservations'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    book_id = Column(String, index=True, nullable=False)
    reserved_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='active')  # active, fulfilled, cancelled
    priority = Column(Integer, default=1)  # for queue ordering
    notified = Column(Boolean, default=False)


def create_db_and_tables():
    """Creates all tables defined on Base if they do not exist."""
    print("Attempting to create borrowing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Borrowing database tables created successfully.")