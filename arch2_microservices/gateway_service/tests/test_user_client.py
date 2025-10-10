import pytest
from src.user_client import UserClient
from src import user_pb2

def test_create_and_list_user():
    client = UserClient()
    user = client.create_user("Bob", "bob@example.com", "pass", user_pb2.STAFF)         #Did I update this??????????????????????????????????????
    assert user.user.name == "Bob"

    users = client.list_users()
   
    assert any(u.name == "Bob" for u in users.users)


# test_create_and_list_user()