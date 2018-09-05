"""Tests for the class S3DataStore."""

from unittest.mock import patch
import pytest

from src.util.data_store.s3_data_store import S3DataStore
from tests.s3_mocks import MockedS3Resource, MockedS3Bucket
from tests.pandas_mocks import MockedData


def test_initial_state():
    """Check the initial state of S3DataStore object."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    assert s3DataStore


def test_get_name():
    """Check the method get_name()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    assert s3DataStore.get_name() == "S3:bucket"


def test_read_json_file_positive():
    """Check the method read_json_file()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.s3_resource = MockedS3Resource()
    s3DataStore.read_json_file("file")


def test_read_json_file_negative():
    """Check the method read_json_file()."""
    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    with pytest.raises(Exception):
        s3DataStore.read_json_file("file")


def test_write_json_file():
    """Check the method write_json_file()."""
    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    with pytest.raises(Exception):
        s3DataStore.write_json_file("file", {})


def test_write_json_file_mocked_s3():
    """Check the method write_json_file() with mocked S3 object."""
    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.s3_resource = MockedS3Resource()
    s3DataStore.write_json_file("file", {})


def test_list_files():
    """Check the method list_files()."""
    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    with pytest.raises(Exception):
        s3DataStore.list_files()


def test_list_files_mocked_s3():
    """Check the method list_files()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.bucket = MockedS3Bucket()

    files = s3DataStore.list_files()
    assert files is not None
    assert len(files) == 3

    # check the 'max_count' filter behaviour
    files = s3DataStore.list_files(max_count=2)
    assert files is not None
    assert len(files) == 2

    files = s3DataStore.list_files(max_count=1)
    assert files is not None
    assert len(files) == 1

    # check the 'prefix' filter behaviour
    files = s3DataStore.list_files(prefix="file")
    assert files is not None
    assert len(files) == 2

    # check the 'max_count' and 'prefix' filters behaviour
    files = s3DataStore.list_files(prefix="file", max_count=1)
    assert files is not None
    assert len(files) == 1


@patch('src.util.data_store.s3_data_store.S3DataStore.list_files', return_value=['file1', 'file2'])
def test_read_all_json_files_positive(_mocked_object):
    """Check the method read_all_json_files()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.s3_resource = MockedS3Resource()
    s3DataStore.read_all_json_files()


def test_read_all_json_files_negative():
    """Check the method read_all_json_files()."""
    # try for improper access_key and secret_key
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    with pytest.raises(Exception):
        s3DataStore.read_all_json_files("file")


def test_download_file():
    """Check the method download_file()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.bucket = MockedS3Bucket("src", "target")
    s3DataStore.download_file("src", "target")


def test_upload_file():
    """Check the method download_file()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.bucket = MockedS3Bucket("src", "target")
    s3DataStore.upload_file("src", "target")


def test_write_pandas_df_into_json_file():
    """Check the method write_pandas_df_into_json_file()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.s3_resource = MockedS3Resource()

    payload = {
        "test": "this"
    }

    data = MockedData(payload)

    s3DataStore.write_pandas_df_into_json_file(data, "payload.json")


@patch('src.util.data_store.s3_data_store.pd', return_value="json data")
def test_read_json_file_into_pandas_df(_mocked_df):
    """Check the method read_json_file_into_pandas_df()."""
    s3DataStore = S3DataStore("bucket", "access_key", "secret_key")
    s3DataStore.s3_resource = MockedS3Resource()
    s3DataStore.read_json_file_into_pandas_df("payload.json")
