
# from . import borrowing_pb2, borrowing_pb2_grpc

import grpc
from concurrent import futures
import time
import logging

from src import borrowing_pb2, borrowing_pb2_grpc, models
from src.db import SessionLocal  
from src import crud

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
    def BorrowBook(self, request, context):
        db = SessionLocal()
        try:
            logging.info(f"📚 BorrowBook request: user_id={request.user_id}, book_id={request.book_id}")
            borrow = crud.create_borrow(db, request.user_id, request.book_id)

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

            logging.info(f"✅ Book returned successfully (borrow_id={request.borrow_id})")
            return borrowing_pb2.ReturnResponse(status="success")
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
                    due_date=b.due_date.strftime("%Y-%m-%d"),
                    user_id=b.user_id
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
