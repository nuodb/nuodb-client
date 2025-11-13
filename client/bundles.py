# (C) Copyright NuoDB, Inc. 2023  All Rights Reserved.
#
# Enumerate the software bundles in the client package.
#
# Each stage must be associated with one bundle.

from enum import Enum


class Bundles(dict, Enum):
    SQL_TOOLS = {"name": "sql-tools", "title": "SQL tools"}
    DRIVER_C = {"name": "c-driver", "title": "C driver"}
    DRIVER_CPP = {"name": "cpp-driver", "title": "C++ driver"}
    ODBC = {"name": "odbc-driver", "title": "ODBC Driver"}

    def __str__(self):
        return self['name']
