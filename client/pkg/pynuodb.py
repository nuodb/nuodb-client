# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the nuodb-python client

import os

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import rmdir, mkdir, pipinstall


class PyNuodbPackage(Package):
    """Add the NuoDB nuodb-python client."""

    __PKGNAME = 'pynuodb'

    def __init__(self):
        super(PyNuodbPackage, self).__init__(self.__PKGNAME)
        self._file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='Python Driver',
                             requirements='Python 2 or 3')]
        # There's only one, make it simple
        self.stage = self.staged[0]

    def unpack(self):
        pypi = PyPIMetadata(self.__PKGNAME)
        self.setversion(pypi.version)

        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        pipinstall('%s==%s' % (self.__PKGNAME, pypi.version), self.pkgroot)

    def install(self):
        self.stage.stage(os.path.join('python', 'site-packages'), ['./'])


# Create and register this package
PyNuodbPackage()
