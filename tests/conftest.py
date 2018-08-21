"""Definition of fixtures for static data, sessions etc. used by unit tests."""

import pytest

from src.rest_api import app


@pytest.fixture
def client():
    """Provide the client session used by tests."""
    with app.test_client() as client:
        yield client
