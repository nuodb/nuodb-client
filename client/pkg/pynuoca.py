# (C) Copyright NuoDB, Inc. 2020  All Rights Reserved.
#
# Add the nuodb collection agent

import os

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import rmdir, mkdir, pipinstall

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

    def prereqs(self):
        return ['pynuodb', 'pynuoadmin']

    def unpack(self):
        pypi = PyPIMetadata(self.__PKGNAME)
        self.setversion(pypi.version)

        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        pipinstall('%s==%s' % (self.__PKGNAME, pypi.version), self.pkgroot)

    def install(self):
        # Omit the files that were installed due to pynuodb and pynuoadmin
        self.stage.omitcontents = Package.get_package('pynuodb').staged[0].getcontents() + Package.get_package('pynuoadmin').staged[0].getcontents()
        self.stage.stage(os.path.join('python', 'site-packages'), ['./'])

# Create and register this package
PyNuoCA()
