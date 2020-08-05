# (C) Copyright NuoDB, Inc. 2020  All Rights Reserved.
#
# Add the nuodb collection agent

import os

from client.package import Package
from client.stage import Stage
from client.artifact import PyPIMetadata, Artifact
from client.utils import *

class PyNuoCA(Package):
    """Add the NuoDB Collection Agent"""

    __PKGNAME = 'pynuoca'

    def __init__(self):
        super(PyNuoCA, self).__init__(self.__PKGNAME)
        self._file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoDB Collection Agent',
                             requirements='Python 2')]
        # There's only one, make it simple
        self.stage = self.staged[0]

    def download(self):
        # Find the latest release
        pypi = PyPIMetadata(self.__PKGNAME)

        self.setversion(pypi.version)

        self._file = Artifact(self.name, 'pynuoca.tar.gz',
                              pypi.pkgurl, chksum=pypi.pkgchksum)
        self._file.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._file.path, self.pkgroot)
        self.stage.basedir = os.path.join(self.pkgroot, 'pynuoca-{}'.format(self.stage.version))

    def install(self):
        self.stage.stage('python', ['pynuoca'])
        self.stage.stage('lib', ['lib/'])
        self.stage.stage('doc', ['README.rst', 'LICENSE'])
        self.stage.stage('bin', ['bin/'])
        self.stage.stage('etc', ['etc/'])


# Create and register this package
PyNuoCA()
