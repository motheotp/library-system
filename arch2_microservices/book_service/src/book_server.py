import grpc
from concurrent import futures
import time

from . import book_pb2, book_pb2_grpc

# In-memory "database"
books_db = {}
next_id = 1


class BookService(book_pb2_grpc.BookServiceServicer):
    def AddBook(self, request, context):
        global next_id
        book_id = str(next_id)
        next_id += 1

        books_db[book_id] = {
            "id": book_id,
            "title": request.title,
            "author": request.author,
            "isbn": request.isbn,
            "status": "available"
        }

        return book_pb2.AddBookResponse(
            book=book_pb2.Book(**books_db[book_id])
        )

    def GetBook(self, request, context):
        book = books_db.get(request.id)
        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")
        return book_pb2.GetBookResponse(book=book_pb2.Book(**book))

    def ListBooks(self, request, context):
        return book_pb2.ListBooksResponse(
            books=[book_pb2.Book(**b) for b in books_db.values()]
        )

    def UpdateBookStatus(self, request, context):
        book = books_db.get(request.id)
        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")

        book["status"] = request.status
        return book_pb2.UpdateBookStatusResponse(
            book=book_pb2.Book(**book)
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port('[::]:50053')
    print("BookService gRPC server running on port 50053...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
