import grpc
from concurrent import futures
import time
import uuid # <--- For generating unique user IDs
from . import user_pb2, user_pb2_grpc

# --- Database and CRUD logic ---
from .db import get_db #for the session context
from .models import create_db_and_tables, User # <--- Import table creation function and User model
from . import crud 
# --------------------------------------------


"""
1.  **Docker Compose** sets the database URL via `DATABASE_URL`.
2.  **`db.py`** reads that URL and provides sessions via `get_db()`.
3.  **`models.py`** defines the schema using `String` for `id` and `user_type` and includes the `password_hash` column.
4.  **`crud.py`** handles the logic, hashing the password before creation and correctly mapping the Protobuf enum to the database string type.
"""

# # In-memory "database" for demo
# users_db = {}
# next_id = 1

class UserService(user_pb2_grpc.UserServiceServicer):
    
    def CreateUser(self, request, context):
        # 1. Generate a universally unique ID (UUID)
        user_id = str(uuid.uuid4()) #UUID
        
        try:
            with get_db() as db: # <--- CHANGE: Open database session
                # 2. Use CRUD function to insert user into PostgreSQL
                db_user = crud.create_user(db, request, user_id)
                
                # 3. Convert the resulting SQLAlchemy model object to a Protobuf message
                user_proto = crud.user_model_to_proto(db_user)
                # logging.info(f" CreateUser RPC completed for {user.email}")
                return user_pb2.CreateUserResponse(user=user_proto)
        except Exception as e:
            # Handle database errors (e.g., email unique constraint violation)
            print(f"Error creating user: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Could not create user due to database error.")

    def GetUser(self, request, context):
        try:
            with get_db() as db: # <--- CHANGE: Open database session
                # 1. Use CRUD to fetch user by ID
                db_user = crud.get_user_by_id(db, request.id)
                
                if not db_user:
                    # 2. Handle not found error
                    context.abort(grpc.StatusCode.NOT_FOUND, f"User with ID {request.id} not found")
                
                # 3. Convert model to proto
                user_proto = crud.user_model_to_proto(db_user)
                return user_pb2.GetUserResponse(user=user_proto)
        except Exception as e:
            print(f"Error retrieving user: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Could not retrieve user due to database error.")

    def AuthenticateUser(self, request, context):
        try:
            with get_db() as db:
                # Fetch user by student_id
                db_user = crud.get_user_by_student_id(db, request.student_id)

                if not db_user:
                    # User not found
                    context.abort(grpc.StatusCode.UNAUTHENTICATED, "User not found")

                # Simple authentication - just check if user exists
                # In production, you'd verify password here
                user_proto = crud.user_model_to_proto(db_user)

                return user_pb2.AuthenticateUserResponse(
                    user=user_proto,
                    message="Authentication successful"
                )

        except Exception as e:
            print(f"Error during authentication: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Authentication failed due to server error")

    def ListUsers(self, request, context):
        # NOTE: Listing all users is not a standard CRUD function but is necessary here.
        try:
            with get_db() as db: # <--- CHANGE: Open database session
                # 1. Query all users from the database
                all_db_users = db.query(User).all() # <--- CHANGE: Direct DB query
                
                # 2. Convert all model objects to Protobuf messages
                user_protos = [crud.user_model_to_proto(u) for u in all_db_users]
                
                return user_pb2.ListUsersResponse(users=user_protos)
        except Exception as e:
            print(f"Error listing users: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Could not list users due to database error.")


def serve():
    # --- NEW: Initialize the database tables on startup ---
    create_db_and_tables() 
    # -----------------------------------------------------

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("UserService gRPC server running on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)




if __name__ == "__main__":
    serve()
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

