import grpc
from . import book_pb2, book_pb2_grpc

class BookClient:
    def __init__(self, host="book_service", port=50053):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = book_pb2_grpc.BookServiceStub(self.channel)

    def add_book(self, title: str, author: str, isbn: str, category: str = "", description: str = "", total_copies: int = 1):
        request = book_pb2.AddBookRequest(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            description=description,
            total_copies=total_copies
        )
        return self.stub.AddBook(request)

    def get_book(self, book_id: str):
        request = book_pb2.GetBookRequest(id=book_id)
        return self.stub.GetBook(request)

    def list_books(self):
        request = book_pb2.ListBooksRequest()
        return self.stub.ListBooks(request)

    def update_book_status(self, book_id: str, status: str):
        request = book_pb2.UpdateBookStatusRequest(id=book_id, status=status)
        return self.stub.UpdateBookStatus(request)

    def close(self):
        self.channel.close()

