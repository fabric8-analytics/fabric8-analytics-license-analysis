"""Mocks object for Pandas DF."""

import json


class MockedData:
    """Mocked pandas DF data."""

    def __init__(self, payload):
        """Initialize the object, use the provided payload."""
        self.payload = payload

    def to_json(self):
        """Convert payload into JSON."""
        return json.dumps(self.payload)
