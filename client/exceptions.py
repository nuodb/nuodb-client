# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Exceptions

__all__ = ['ClientError', 'ChecksumError',
           'DownloadError', 'CommandError', 'UnpackError']


class ClientError(Exception):
    pass


class ChecksumError(ClientError):
    def __init__(self, url, expected, actual):
        super(ChecksumError, self).__init__(
            "Checksum mismatch for {}:\nExpected: {}\nActual:   {}".
            format(url, expected, actual))


class DownloadError(ClientError):
    pass


class CommandError(ClientError):
    pass


class UnpackError(ClientError):
    pass
