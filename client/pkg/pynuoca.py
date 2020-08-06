# (C) Copyright NuoDB, Inc. 2020  All Rights Reserved.
#
# Add the nuodb collection agent

from client.package import Package
from client.stage import Stage
from client.utils import rmdir, mkdir, run

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

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)

        run(['python', '-m', 'pip', 'install', self.__PKGNAME, '-t', self.pkgroot])

    def install(self):
        self.stage.stage('python', ['./'])

# Create and register this package
PyNuoCA()
