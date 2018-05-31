"""Mocks object for AWS S3 interface provided by Boto client."""


class MockedS3Data:
    """Mock for the S3 data."""

    def __init__(self):
        """Initialize the object."""
        pass

    def read(self):
        """Fake the behaviour of read method."""
        return b'{"json":"data"}'


class MockedS3Object:
    """Mock for the S3.Object class."""

    def __init__(self, key=None):
        """Initialize the object."""
        self.key = key
        pass

    def get(self):
        """Fake the behaviour of get method."""
        return {"Body": MockedS3Data()}

    def put(self, Body=None):
        """Fake the behaviour of put method."""
        return


class MockedS3Resource:
    """Mock for the S3.ServiceResource class."""

    def __init__(self):
        """Initialize the object."""
        pass

    def Object(self, bucket_name, filename):
        """Fake the behaviour of Object constructor."""
        return MockedS3Object()


class MockedS3Objects:
    """Mock for the S3.Objects class."""

    def __init__(self):
        """Initialize the object."""
        pass

    def all(self):
        """Fake the behaviour of all method."""
        return [MockedS3Object("file1"),
                MockedS3Object("file2"),
                MockedS3Object("file3")]

    def filter(self, Prefix=None):
        """Fake the behaviour of filter method."""
        # TODO: implement proper filter?
        return [MockedS3Object("file1"),
                MockedS3Object("file3")]


class MockedS3Bucket:
    """Mock for the S3.Bucket class."""

    def __init__(self, src=None, target=None):
        """Initialize the object."""
        self.objects = MockedS3Objects()
        self.src = src
        self.target = target

    def upload_file(self, src, target):
        """Fake the behaviour of upload_file method."""
        assert src is not None
        assert target is not None
        assert src == self.src
        assert target == self.target

    def download_file(self, src, target):
        """Fake the behaviour of download_file method."""
        assert src is not None
        assert target is not None
        assert src == self.src
        assert target == self.target
