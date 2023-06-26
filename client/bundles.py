# (C) Copyright NuoDB, Inc. 2023  All Rights Reserved.
#
# Enumerate the software bundles in the client package.
#
# Each stage must be associated with one bundle.

from enum import Enum


class Bundles(dict, Enum):
    CLI_TOOLS = {'name': 'cli-tools', 'title': 'CLI tools'}
    DRIVERS = {'name': 'drivers', 'title': 'Drivers'}

    def __str__(self):
        return self['name']
