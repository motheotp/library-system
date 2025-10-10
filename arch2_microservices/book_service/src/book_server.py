

import grpc
from concurrent import futures
import time

from src import book_pb2, book_pb2_grpc
from src.db import SessionLocal, create_db_and_tables
from src import crud


# Initialize DB tables
create_db_and_tables()

class BookService(book_pb2_grpc.BookServiceServicer):
    def AddBook(self, request, context):
        with SessionLocal() as db:
            book = crud.create_book(db, request.title, request.author, request.isbn)
            return book_pb2.AddBookResponse(
                book=book_pb2.Book(
                    id=str(book.id),
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    status=book.status,
                )
            )

    def GetBook(self, request, context):
        with SessionLocal() as db:
            book = crud.get_book(db, request.id)
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")

            return book_pb2.GetBookResponse(
                book=book_pb2.Book(
                    id=str(book.id),
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    status=book.status,
                )
            )

    def ListBooks(self, request, context):
        with SessionLocal() as db:
            books = crud.list_books(db)
            return book_pb2.ListBooksResponse(
                books=[
                    book_pb2.Book(
                        id=str(b.id),
                        title=b.title,
                        author=b.author,
                        isbn=b.isbn,
                        status=b.status,
                    )
                    for b in books
                ]
            )

    def UpdateBookStatus(self, request, context):
        with SessionLocal() as db:
            book = crud.update_book_status(db, request.id, request.status)
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")

            return book_pb2.UpdateBookStatusResponse(
                book=book_pb2.Book(
                    id=str(book.id),
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    status=book.status,
                )
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port("[::]:50053")
    print("✅ BookService gRPC server running on port 50053...")
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down BookService...")
        server.stop(0)


if __name__ == "__main__":
    serve()
