"""Abstract class to be inherited by concrete data store implementations."""

import abc


class AbstractDataStore(object):
    """Abstract class to be inherited by concrete data store implementations."""

    @abc.abstractmethod
    def get_name(self):
        """Return printable name of this storage."""

    @abc.abstractmethod
    def list_files(self, prefix=None, max_count=None):
        """List all the files in the source directory."""

    @abc.abstractmethod
    def read_json_file(self, filename):
        """Read JSON file from the data source."""

    @abc.abstractmethod
    def read_all_json_files(self):
        """Read all the files from the data source."""

    @abc.abstractmethod
    def write_json_file(self, filename, contents):
        """Write JSON file into data source."""

    @abc.abstractmethod
    def upload_file(self, src, target):
        """Upload file into data store."""

    @abc.abstractmethod
    def download_file(self, src, target):
        """Download file from data store."""
