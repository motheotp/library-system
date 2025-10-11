
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .db import Base, engine

class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, index=True)  # Added for compatibility with arch1
    description = Column(Text)  # Added for compatibility with arch1
    total_copies = Column(Integer, default=1)  # Added for copy tracking
    available_copies = Column(Integer, default=1)  # Added for copy tracking
    status = Column(String, default="available")  # available / borrowed (kept for backward compat)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0

    def borrow_copy(self):
        """Decrease available copies when book is borrowed"""
        if self.available_copies > 0:
            self.available_copies -= 1
            if self.available_copies == 0:
                self.status = "borrowed"
            return True
        return False

    def return_copy(self):
        """Increase available copies when book is returned"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            if self.available_copies > 0:
                self.status = "available"
            return True
        return False


def create_db_and_tables():
    """Creates all defined tables in the database if they do not exist."""
    print("Attempting to create book database tables...")
    Base.metadata.create_all(bind=engine)
    print("Book database tables created successfully.")
