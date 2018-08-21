"""Unit tests for the APIUser class."""

from src.auth import APIUser


def test_api_user_class():
    """Test the basic behaviour of APIUser class."""
    email = "tester@foo.bar.baz"
    user = APIUser(email)
    # just dummy check ATM as the class is pretty simple
    assert email == user.email


if __name__ == '__main__':
    test_api_user_class()
