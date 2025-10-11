
# from . import borrowing_pb2, borrowing_pb2_grpc

import grpc
from concurrent import futures
import time
import logging

from src import borrowing_pb2, borrowing_pb2_grpc, models
from src.db import SessionLocal
from src import crud
from src.book_client import BookClient

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --------------------------------------------------
# gRPC Service Implementation
# --------------------------------------------------
class BorrowingService(borrowing_pb2_grpc.BorrowingServiceServicer):
    def __init__(self):
        """Initialize the BorrowingService with a BookClient"""
        self.book_client = BookClient()

    def BorrowBook(self, request, context):
        db = SessionLocal()
        try:
            logging.info(f"📚 BorrowBook request: user_id={request.user_id}, book_id={request.book_id}")

            # First, check if the book has available copies
            try:
                book_response = self.book_client.get_book(request.book_id)
                if book_response.book.available_copies <= 0:
                    logging.warning(f"⚠️ Book {request.book_id} has no available copies")
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                    context.set_details("No copies available for borrowing.")
                    return borrowing_pb2.BorrowResponse(status="failed")
            except grpc.RpcError as e:
                logging.error(f"❌ Error checking book availability: {str(e)}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Could not check book availability.")
                return borrowing_pb2.BorrowResponse(status="failed")

            # Create the borrow record
            borrow = crud.create_borrow(db, request.user_id, request.book_id)

            # Update available copies in book service (decrement by 1)
            try:
                self.book_client.update_available_copies(request.book_id, -1)
                logging.info(f"📉 Decremented available copies for book {request.book_id}")
            except grpc.RpcError as e:
                logging.error(f"❌ Error updating book copies: {str(e)}")
                # Rollback the borrow record if we can't update the book
                db.delete(borrow)
                db.commit()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Could not update book availability.")
                return borrowing_pb2.BorrowResponse(status="failed")

            logging.info(f"✅ Book borrowed successfully (borrow_id={borrow.borrow_id})")
            return borrowing_pb2.BorrowResponse(
                borrow_id=borrow.borrow_id,
                status="success"
            )
        except Exception as e:
            logging.error(f"❌ Error borrowing book: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Could not borrow book due to database error.")
            return borrowing_pb2.BorrowResponse(status="failed")
        finally:
            db.close()

    def ReturnBook(self, request, context):
        db = SessionLocal()
        try:
            logging.info(f"↩️ ReturnBook request: borrow_id={request.borrow_id}")
            borrow = crud.return_borrow(db, request.borrow_id)
            if not borrow:
                logging.warning(f"⚠️ Borrow record not found: {request.borrow_id}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Borrow record not found.")
                return borrowing_pb2.ReturnResponse(status="failed")

            # Update available copies in book service (increment by 1)
            try:
                self.book_client.update_available_copies(borrow.book_id, 1)
                logging.info(f"📈 Incremented available copies for book {borrow.book_id}")
            except grpc.RpcError as e:
                logging.error(f"❌ Error updating book copies: {str(e)}")
                # Note: We still mark the book as returned even if we can't update the book service
                # This ensures consistency - the user has returned the book

            # Build the full borrowing response with fine details
            borrowed_book = borrowing_pb2.BorrowedBook(
                borrow_id=borrow.borrow_id,
                book_id=borrow.book_id,
                borrowed_date=borrow.borrowed_date.strftime("%Y-%m-%d"),
                due_date=borrow.due_date.strftime("%Y-%m-%d") if borrow.due_date else "",
                user_id=borrow.user_id,
                returned=borrow.returned,
                returned_date=borrow.returned_date.strftime("%Y-%m-%d") if borrow.returned_date else "",
                fine_amount=borrow.fine_amount,
                is_overdue=borrow.is_overdue(),
                days_overdue=borrow.days_overdue()
            )

            logging.info(f"✅ Book returned successfully (borrow_id={request.borrow_id}), fine=${borrow.fine_amount}")
            return borrowing_pb2.ReturnResponse(
                status="success",
                borrowing=borrowed_book
            )
        except Exception as e:
            logging.error(f"❌ Error returning book: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Could not return book due to database error.")
            return borrowing_pb2.ReturnResponse(status="failed")
        finally:
            db.close()

    def GetBorrowedBooks(self, request, context):
        db = SessionLocal()
        try:
            logging.info(f"📋 GetBorrowedBooks request: user_id={request.user_id}")
            borrows = crud.get_borrowed_books_by_user(db, request.user_id)

            borrowed_books = [
                borrowing_pb2.BorrowedBook(
                    borrow_id=b.borrow_id,
                    book_id=b.book_id,
                    borrowed_date=b.borrowed_date.strftime("%Y-%m-%d"),
                    due_date=b.due_date.strftime("%Y-%m-%d") if b.due_date else "",
                    user_id=b.user_id,
                    returned=b.returned,
                    returned_date=b.returned_date.strftime("%Y-%m-%d") if b.returned_date else "",
                    fine_amount=b.fine_amount,
                    is_overdue=b.is_overdue(),
                    days_overdue=b.days_overdue()
                )
                for b in borrows
            ]
            logging.info(f"✅ Found {len(borrowed_books)} borrowed books for user {request.user_id}")
            return borrowing_pb2.BorrowedBooksResponse(borrowed_books=borrowed_books)
        except Exception as e:
            logging.error(f"❌ Error fetching borrowed books: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error retrieving borrowed books.")
            return borrowing_pb2.BorrowedBooksResponse()
        finally:
            db.close()

# --------------------------------------------------
# gRPC Server Setup
# --------------------------------------------------
def serve():
    # --- Ensure tables exist on startup ---
    models.create_db_and_tables()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    borrowing_pb2_grpc.add_BorrowingServiceServicer_to_server(BorrowingService(), server)

    server.add_insecure_port('[::]:50055')  # Match the port used in docker-compose
    logging.info("🚀 BorrowingService gRPC server running on port 50055...")
    server.start()

    try:
        while True:
            time.sleep(86400)  # Keep running
    except KeyboardInterrupt:
        logging.info("🛑 Shutting down BorrowingService...")
        server.stop(0)


if __name__ == "__main__":
    serve()
