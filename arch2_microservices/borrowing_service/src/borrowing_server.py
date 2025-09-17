import grpc
from concurrent import futures
import time
from . import borrowing_pb2, borrowing_pb2_grpc

# In-memory "database" for demo
borrowings_db = {}
next_borrow_id = 1

class BorrowingService(borrowing_pb2_grpc.BorrowingServiceServicer):
    def BorrowBook(self, request, context):
        global next_borrow_id
        borrow_id = str(next_borrow_id)
        next_borrow_id += 1

        borrowings_db[borrow_id] = {
            "borrow_id": borrow_id,
            "user_id": request.user_id,
            "book_id": request.book_id,
            "borrowed_date": "2025-09-17",  # placeholder
            "due_date": "2025-09-24"        # placeholder
        }

        return borrowing_pb2.BorrowResponse(
            borrow_id=borrow_id,
            status="success"
        )

    def ReturnBook(self, request, context):
        if request.borrow_id in borrowings_db:
            del borrowings_db[request.borrow_id]
            return borrowing_pb2.ReturnResponse(status="success")
        else:
            context.abort(grpc.StatusCode.NOT_FOUND, "Borrow record not found")

    def GetBorrowedBooks(self, request, context):
        user_borrowed = [
            borrowing_pb2.BorrowedBook(**b)
            for b in borrowings_db.values()
            if b["user_id"] == request.user_id
        ]
        return borrowing_pb2.BorrowedBooksResponse(borrowed_books=user_borrowed)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    borrowing_pb2_grpc.add_BorrowingServiceServicer_to_server(BorrowingService(), server)
    server.add_insecure_port('[::]:50052')  # different port than UserService
    print("BorrowingService gRPC server running on port 50052...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
