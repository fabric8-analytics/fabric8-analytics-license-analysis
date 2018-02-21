"""Tests for the class S3DataStore."""

import pytest
import os

from src.util.data_store.s3_data_store import S3DataStore


def test_initial_state():
    """Check the initial state of S3DataStore object."""
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")


def test_get_name():
    """Check the method get_name()."""
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    assert s3DataStore.get_name() == "S3:bucket"


def test_read_json_file():
    """Check the method read_json_file()."""

    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    with pytest.raises(Exception):
        s3DataStore.read_json_file("file")


def test_write_json_file():
    """Check the method write_json_file()."""

    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    with pytest.raises(Exception):
        s3DataStore.write_json_file("file", {})


def test_list_files():
    """Check the method list_files()."""

    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    with pytest.raises(Exception):
        s3DataStore.list_files()


def test_read_all_json_files():
    """Check the method read_all_json_files()."""

    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    with pytest.raises(Exception):
        s3DataStore.read_all_json_files("file")
