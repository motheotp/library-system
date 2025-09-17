import grpc
import pytest
from concurrent import futures

from src import user_pb2, user_pb2_grpc, user_server 


@pytest.fixture(scope="module")
def grpc_server():
    # Start the gRPC server in background
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(user_server.UserService(), server)
    port = server.add_insecure_port("localhost:0")  # 0 = random free port
    server.start()

    channel = grpc.insecure_channel(f"localhost:{port}")
    stub = user_pb2_grpc.UserServiceStub(channel)

    yield stub  # test functions will use this stub

    server.stop(None)


def test_create_and_get_user(grpc_server):
    # Create user
    resp = grpc_server.CreateUser(user_pb2.CreateUserRequest(
        name="Alice",
        email="alice@example.com",
        password="secret123",
        user_type=user_pb2.STUDENT
    ))
    assert resp.user.name == "Alice"
    user_id = resp.user.id
    

    # Fetch user
    fetched = grpc_server.GetUser(user_pb2.GetUserRequest(id=user_id))
   
    assert fetched.user.email == "alice@example.com"


def test_authenticate_user(grpc_server):
    grpc_server.CreateUser(user_pb2.CreateUserRequest(
        name="Bob",
        email="bob@example.com",
        password="pass456",
        user_type=user_pb2.STAFF
    ))

    auth = grpc_server.AuthenticateUser(user_pb2.AuthenticateUserRequest(
        email="bob@example.com",
        password="pass456"
    ))

    assert auth.user_id is not None
    # print("Authenticated user ID:", end=" ")
    # print(auth.user_id)
    assert auth.token == "fake-jwt-token"
    