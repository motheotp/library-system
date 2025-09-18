import grpc
from . import borrowing_pb2, borrowing_pb2_grpc

class BorrowingClient:
    def __init__(self, host="localhost", port=50052):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = borrowing_pb2_grpc.BorrowingServiceStub(self.channel)

    def borrow_book(self, user_id, book_id):
        """Borrow a book for a user."""
        request = borrowing_pb2.BorrowRequest(user_id=user_id, book_id=book_id)
        return self.stub.BorrowBook(request)

    def return_book(self, borrow_id):
        """Return a borrowed book."""
        request = borrowing_pb2.ReturnRequest(borrow_id=borrow_id)
        return self.stub.ReturnBook(request)

    def get_borrowed_books(self, user_id):
        """Get all borrowed books for a given user."""
        request = borrowing_pb2.UserRequest(user_id=user_id)
        return self.stub.GetBorrowedBooks(request)
