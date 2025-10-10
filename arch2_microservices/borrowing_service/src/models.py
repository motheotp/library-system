from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from .db import Base, engine

class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    borrow_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    book_id = Column(String, index=True, nullable=False)
    borrowed_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)


def create_db_and_tables():
    """Creates all tables defined on Base if they do not exist."""
    print("Attempting to create borrowing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Borrowing database tables created successfully.")