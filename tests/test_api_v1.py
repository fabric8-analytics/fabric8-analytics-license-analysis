"""Unit tests for the REST API module."""

import json
import os
import urllib.parse as urlparse

from flask import current_app, url_for
import pytest
import requests


def api_route_for(route):
    """Construct an URL to the endpoint for given route."""
    return '/api/v1/' + route


def get_json_from_response(response):
    """Decode JSON from response."""
    return json.loads(response.data.decode('utf8'))


def test_heart_beat_endpoint(client):
    """Test the heart beat endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = get_json_from_response(response)
    assert "status" in json_data
    assert json_data["status"] == "ok"


def test_stack_license_endpoint(client):
    """Test the endpont /api/v1/stack_license."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['MIT', 'PD']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    response = client.post(api_route_for("stack_license"), data=json.dumps(payload))
    assert response.status_code == 200
    json_data = get_json_from_response(response)
    assert "status" in json_data
    assert json_data["status"] == "Successful"
    assert json_data['stack_license'] == 'gplv2'


def test_license_recommender_endpoint_empty_payload(client):
    """Test the endpont /api/v1/license_recommender."""
    payload = {}
    with pytest.raises(Exception):
        response = client.post(api_route_for("license-recommender"), data=json.dumps(payload))


def test_license_recommender_endpoint_payload(client):
    """Test the endpont /api/v1/license_recommender."""
    payload = {"_resolved": [],
               "ecosystem": "pypi"}
    response = client.post(api_route_for("license-recommender"), data=json.dumps(payload))
    assert response.status_code == 200
    json_data = get_json_from_response(response)
    assert "status" in json_data
    assert json_data["status"] == "Failure"
