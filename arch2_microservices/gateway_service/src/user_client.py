import grpc
from . import user_pb2, user_pb2_grpc  


class UserClient:
    def __init__(self, host="user_service", port=50051):
        """
        Initialize a gRPC channel and stub for UserService.
        """
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    def create_user(self, name, email, password, user_type):
        """
        Calls the CreateUser RPC on the server.
        """
        request = user_pb2.CreateUserRequest(
            name=name,
            email=email,
            password=password,
            user_type=user_type
        )
        return self.stub.CreateUser(request)

    def get_user(self, user_id):
        """
        Calls the GetUser RPC on the server.
        """
        request = user_pb2.GetUserRequest(id=user_id)
        return self.stub.GetUser(request)

    def authenticate_user(self, student_id):
        """
        Calls the AuthenticateUser RPC on the server using student_id.
        """
        request = user_pb2.AuthenticateUserRequest(student_id=student_id)
        return self.stub.AuthenticateUser(request)

    def list_users(self):
        """
        Calls the ListUsers RPC on the server.
        """
        request = user_pb2.ListUsersRequest()
        return self.stub.ListUsers(request)

    def close(self):
        """
        Close the gRPC channel.
        """
        self.channel.close()


