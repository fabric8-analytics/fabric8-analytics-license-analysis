"""Unit tests for the REST API module."""

import json
import os
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from flask import current_app, url_for
import pytest
import requests


def api_route_for(route):
    """Construct an URL to the endpoint for given route."""
    return '/api/v1' + route


def get_json_from_response(response):
    """Decode JSON from response."""
    return json.loads(response.data.decode('utf8'))


def test_heart_beat_endpoint(client):
    """Test the heart beat endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    json = get_json_from_response(response)
    assert "status" in json
    assert json["status"] == "ok"
