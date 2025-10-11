import grpc
from . import book_pb2, book_pb2_grpc


class BookClient:
    def __init__(self, host="book_service", port=50053):
        """
        Initialize a gRPC channel and stub for BookService.
        """
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = book_pb2_grpc.BookServiceStub(self.channel)

    def update_available_copies(self, book_id: str, increment: int):
        """
        Calls the UpdateAvailableCopies RPC on the server.
        increment: positive to add copies, negative to remove copies
        """
        request = book_pb2.UpdateAvailableCopiesRequest(id=book_id, increment=increment)
        return self.stub.UpdateAvailableCopies(request)

    def get_book(self, book_id: str):
        """
        Calls the GetBook RPC on the server.
        """
        request = book_pb2.GetBookRequest(id=book_id)
        return self.stub.GetBook(request)

    def close(self):
        """
        Close the gRPC channel.
        """
        self.channel.close()
