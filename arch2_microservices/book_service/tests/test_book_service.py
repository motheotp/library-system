import pytest
import grpc
from concurrent import futures
from src import book_pb2, book_pb2_grpc, book_server


@pytest.fixture(scope="module")
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_pb2_grpc.add_BookServiceServicer_to_server(book_server.BookService(), server)
    port = server.add_insecure_port('[::]:0')  # dynamic port
    server.start()
    yield server, port
    server.stop(0)


@pytest.fixture(scope="module")
def grpc_stub(grpc_server):
    server, port = grpc_server
    channel = grpc.insecure_channel(f'localhost:{port}')
    return book_pb2_grpc.BookServiceStub(channel)


def test_add_and_get_book(grpc_stub):
    # Add book
    add_resp = grpc_stub.AddBook(book_pb2.AddBookRequest(
        title="1984", author="George Orwell", isbn="1234567890"
    ))
    assert add_resp.book.id == "1"
    assert add_resp.book.status == "available"

    # Get book
    get_resp = grpc_stub.GetBook(book_pb2.GetBookRequest(id="1"))
    assert get_resp.book.title == "1984"

    # Update status
    upd_resp = grpc_stub.UpdateBookStatus(book_pb2.UpdateBookStatusRequest(
        id="1", status="borrowed"
    ))
    assert upd_resp.book.status == "borrowed"

    # List books
    list_resp = grpc_stub.ListBooks(book_pb2.ListBooksRequest())
    assert len(list_resp.books) == 1
    assert list_resp.books[0].title == "1984"
