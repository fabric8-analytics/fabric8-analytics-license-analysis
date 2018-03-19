"""Tests for the class S3DataStore."""

from unittest.mock import *
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


class _MockedS3Data:
    def __init__(self):
        pass

    def read(self):
        return b'{"json":"data"}'


class _MockedS3Object:

    def __init__(self):
        pass

    def get(self):
        return {"Body": _MockedS3Data()}


class _MockedS3Resource:
    def __init__(self):
        pass

    def Object(self, bucket_name, filename):
        return _MockedS3Object()


def test_read_json_file_positive():
    """Check the method read_json_file()."""
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    s3DataStore.s3_resource = _MockedS3Resource()
    s3DataStore.read_json_file("file")


def test_read_json_file_negative():
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


@patch('src.util.data_store.s3_data_store.S3DataStore.list_files', return_value=['file1', 'file2'])
def test_read_all_json_files_positive(mocked_object):
    """Check the method read_all_json_files()."""
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    s3DataStore.s3_resource = _MockedS3Resource()
    s3DataStore.read_all_json_files()


def test_read_all_json_files_negative():
    """Check the method read_all_json_files()."""
    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "sercet_key")
    with pytest.raises(Exception):
        s3DataStore.read_all_json_files("file")
