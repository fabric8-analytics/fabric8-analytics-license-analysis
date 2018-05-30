"""Unit tests for token handling functions."""

import unittest
import pytest
from unittest.mock import *

from src.auth import *
from src.utils import *


def mocked_fetch_public_key_1(app):
    """Mock for the function fetch_public_key()."""
    return None


def mocked_fetch_public_key_2(app):
    """Mock for the function fetch_public_key()."""
    return "nothing"


def mocked_get_audiences():
    """Mock for the function get_audiences()."""
    return []


def mocked_get_audiences_2():
    """Mock for the function get_audiences()."""
    return ["audience1", "audience2"]


@patch("auth.get_audiences", side_effect=mocked_get_audiences)
@patch("auth.fetch_public_key", side_effect=mocked_fetch_public_key_1)
def test_decode_token_invalid_input_1(mocked_fetch_public_key, x):
    """Test the invalid input handling during token decoding."""
    assert decode_token(None) == {}


@patch("auth.get_audiences", side_effect=mocked_get_audiences)
@patch("auth.fetch_public_key", side_effect=mocked_fetch_public_key_1)
def test_decode_token_invalid_input_2(mocked_fetch_public_key, x):
    """Test the invalid input handling during token decoding."""
    with pytest.raises(Exception):
        assert decode_token("Foobar") is None


@patch("auth.get_audiences", side_effect=mocked_get_audiences)
@patch("auth.fetch_public_key", side_effect=mocked_fetch_public_key_1)
def test_decode_token_invalid_input_3(mocked_fetch_public_key, x):
    """Test the invalid input handling during token decoding."""
    with pytest.raises(Exception):
        assert decode_token("Bearer ") is None


@patch("auth.get_audiences", side_effect=mocked_get_audiences)
@patch("auth.fetch_public_key", side_effect=mocked_fetch_public_key_2)
def test_decode_token_invalid_input_4(mocked_fetch_public_key, x):
    """Test the invalid input handling during token decoding."""
    with pytest.raises(Exception):
        assert decode_token("Bearer ") is None


@patch("auth.get_audiences", side_effect=mocked_get_audiences_2())
@patch("auth.fetch_public_key", side_effect=mocked_fetch_public_key_2)
def test_decode_token_invalid_input_5(mocked_fetch_public_key, mocked_get_audiences):
    """Test the handling wrong JWT tokens."""
    with pytest.raises(Exception):
        assert decode_token("Bearer something") is None


if __name__ == '__main__':
    test_decode_token_invalid_input_1()
    test_decode_token_invalid_input_2()
    test_decode_token_invalid_input_3()
    test_decode_token_invalid_input_4()
    test_decode_token_invalid_input_5()
