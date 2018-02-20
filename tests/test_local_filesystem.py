"""Tests for the class LocalFileSystem."""

import pytest
import os

from src.config import DATA_DIR
from src.util.data_store.local_filesystem import LocalFileSystem


def test_initial_state():
    """Check the initial state of LocalFileSystem object."""
    localFileSystem = LocalFileSystem("")
    assert localFileSystem.src_dir == "/"

    localFileSystem = LocalFileSystem("/")
    assert localFileSystem.src_dir == "/"

    localFileSystem = LocalFileSystem("test")
    assert localFileSystem.src_dir == "test/"

    localFileSystem = LocalFileSystem("test/")
    assert localFileSystem.src_dir == "test/"


def test_get_name():
    """Check the method get_name()."""
    localFileSystem = LocalFileSystem("")
    assert localFileSystem.get_name() == "Local filesystem dir: /"

    localFileSystem = LocalFileSystem("/")
    assert localFileSystem.get_name() == "Local filesystem dir: /"

    localFileSystem = LocalFileSystem("test")
    assert localFileSystem.get_name() == "Local filesystem dir: test/"

    localFileSystem = LocalFileSystem("test/")
    assert localFileSystem.get_name() == "Local filesystem dir: test/"


def test_list_files():
    """Check the method list_files()."""
    # the testdir1 directory is empty
    data_dir = os.path.join(DATA_DIR, "testdir1")
    localFileSystem = LocalFileSystem(data_dir)
    # list of files must be empty
    assert not localFileSystem.list_files()

    # the testdir2 is not empty, but it does not contain any JSON file
    data_dir = os.path.join(DATA_DIR, "testdir2")
    localFileSystem = LocalFileSystem(data_dir)
    # list of files must be empty
    assert not localFileSystem.list_files()

    # the testdir3 directory contains four JSON files
    data_dir = os.path.join(DATA_DIR, "testdir3")
    localFileSystem = LocalFileSystem(data_dir)
    listFiles = localFileSystem.list_files()
    assert "1.json" in listFiles
    assert "2.json" in listFiles
    assert "prefix1.json" in listFiles
    assert "prefix2.json" in listFiles

    # test list of files with prefix
    data_dir = os.path.join(DATA_DIR, "testdir3")
    localFileSystem = LocalFileSystem(data_dir)
    listFiles = localFileSystem.list_files("prefix")
    assert "prefix1.json" in listFiles
    assert "prefix2.json" in listFiles

    # test list of files with prefix
    data_dir = os.path.join(DATA_DIR, "testdir3")
    localFileSystem = LocalFileSystem(data_dir)
    listFiles = localFileSystem.list_files("nonexistent-prefix")
    # list of files must be empty
    assert not listFiles


def test_read_json_file():
    """Check the method read_json_file()."""
    data_dir = os.path.join(DATA_DIR, "testdir3")
    localFileSystem = LocalFileSystem(data_dir)

    data = localFileSystem.read_json_file("1.json")
    assert data is not None
    assert "test" in data
    assert data["test"] == 42


def test_read_all_json_files():
    """Check the method read_all_json_files()."""
    data_dir = os.path.join(DATA_DIR, "testdir3")
    localFileSystem = LocalFileSystem(data_dir)

    datas = localFileSystem.read_all_json_files()
    assert datas is not None
    assert len(datas) == 4
    for file, data in datas:
        assert data is not None
        assert "test" in data
        assert data["test"] == 42


def test_write_json_file():
    """Check the method write_json_file()."""
    data_dir = os.path.join(DATA_DIR, "testdir4")
    localFileSystem = LocalFileSystem(data_dir)

    localFileSystem.write_json_file("test.json", {"t1": 1, "t2": 2})

    data = localFileSystem.read_json_file("test.json")
    assert data is not None
    assert "t1" in data
    assert data["t1"] == 1
    assert "t2" in data
    assert data["t2"] == 2


def test_upload_file():
    """Check the method upload_file()."""
    localFileSystem = LocalFileSystem("")
    assert localFileSystem.upload_file("src", "target") is None


def test_download_file():
    """Check the method download_file()."""
    localFileSystem = LocalFileSystem("")
    assert localFileSystem.download_file("src", "target") is None


def test_convert_list_of_tuples_to_string():
    """Check the method convert_list_of_tuples_to_string()."""
    assert LocalFileSystem.convert_list_of_tuples_to_string([(1,), (4,)]) == "[(1,), (4,)]"
    assert LocalFileSystem.convert_list_of_tuples_to_string([(1, 2), (3, 4)]) == "[(1, 2), (3, 4)]"
