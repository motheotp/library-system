# borrowing_service/tests/test_borrowing_service.py
import pytest
import grpc
from concurrent import futures

from src import borrowing_pb2, borrowing_pb2_grpc, borrowing_server

@pytest.fixture(scope="module")
def grpc_stub():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    borrowing_pb2_grpc.add_BorrowingServiceServicer_to_server(borrowing_server.BorrowingService(), server)
    port = server.add_insecure_port("localhost:0")  # let OS pick a free port
    server.start()

    channel = grpc.insecure_channel(f"localhost:{port}")
    stub = borrowing_pb2_grpc.BorrowingServiceStub(channel)

    yield stub

    server.stop(None)


def test_borrow_and_return(grpc_stub):
    # Borrow
    resp = grpc_stub.BorrowBook(borrowing_pb2.BorrowRequest(user_id="1", book_id="10"))
    assert resp.status == "success"
    borrow_id = resp.borrow_id

    # Get borrowed books for user 1
    list_resp = grpc_stub.GetBorrowedBooks(borrowing_pb2.UserRequest(user_id="1"))
    assert len(list_resp.borrowed_books) >= 1

    # Return
    ret = grpc_stub.ReturnBook(borrowing_pb2.ReturnRequest(borrow_id=borrow_id))
    assert ret.status == "success"
