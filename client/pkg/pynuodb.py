# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the nuodb-python client

import os

from client.package import Package
from client.stage import Stage
from client.artifact import PyPIMetadata, Artifact
from client.utils import *

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

    def download(self):
        # Find the latest release
        pypi = PyPIMetadata(self.__PKGNAME)

        self.setversion(pypi.version)

        self._file = Artifact(self.name, 'pynuodb.tar.gz',
                              pypi.pkgurl, chksum=pypi.pkgchksum)
        self._file.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._file.path, self.pkgroot)
        self.stage.basedir = os.path.join(self.pkgroot, 'pynuodb-{}'.format(self.stage.version))

    def install(self):
        self.stage.stage('python', ['pynuodb'])
        self.stage.stage('doc', ['README.rst', 'LICENSE'])


# Create and register this package
PyNuodbPackage()
