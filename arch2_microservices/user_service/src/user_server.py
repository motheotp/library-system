import grpc
from concurrent import futures
import time

from . import user_pb2, user_pb2_grpc

# In-memory "database" for demo
users_db = {}
next_id = 1


class UserService(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        global next_id
        user_id = str(next_id)
        next_id += 1

        # Store user
        users_db[user_id] = {
            "id": user_id,
            "name": request.name,
            "email": request.email,
            "password_hash": request.password,  # should we hash this?
            "user_type": request.user_type
        }

        user = user_pb2.User(
            id=user_id,
            name=request.name,
            email=request.email,
            user_type=request.user_type
        )
        return user_pb2.CreateUserResponse(user=user)

    def GetUser(self, request, context):
        u = users_db.get(request.id)
        if not u:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        user = user_pb2.User(**u)
        return user_pb2.GetUserResponse(user=user)

    def AuthenticateUser(self, request, context):
        # Simple linear search for demo
        for u in users_db.values():
            if u["email"] == request.email and u["password_hash"] == request.password:
                # Return dummy token
                return user_pb2.AuthenticateUserResponse(user_id=u["id"], token="fake-jwt-token")
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials")

    def ListUsers(self, request, context):
        return user_pb2.ListUsersResponse(
            users=[user_pb2.User(**u) for u in users_db.values()]
        )


def serve():
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
