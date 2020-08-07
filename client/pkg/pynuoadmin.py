# (C) Copyright NuoDB, Inc. 2019-2020  All Rights Reserved.
#
# Add the pynuoadmin client

import os

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import Globals, rmdir, mkdir, pipinstall


class PyNuoadminPackage(Package):
    """Add the NuoDB pynuoadmin client.
This pulls the latest version available from PyPI.
"""

    __PKGNAME = 'pynuoadmin'

    def __init__(self):
        super(PyNuoadminPackage, self).__init__(self.__PKGNAME)

        self._file = None
        self._ac_file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoAdmin Driver',
                             requirements='Python 2')]

        self.stage = self.staged[0]

    def prereqs(self):
        # We need nuodb to get nuokeymanager.jar and pynuoadmin uses pynuodb
        return ['nuodb', 'pynuodb']

    def unpack(self):
        pypi = PyPIMetadata(self.__PKGNAME)
        self.setversion(pypi.version)

        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        pipinstall('%s[completion]==%s' % (self.__PKGNAME, pypi.version), self.pkgroot)

    def install(self):
        # Omit the files that were installed due to pynuodb
        self.stage.omitcontents = Package.get_package('pynuodb').staged[0].getcontents()

        self.stage.stage(os.path.join('python', 'site-packages'), ['./'])

        nuodb = self.get_package('nuodb')

        # This needs to go two levels below the root, as it contains a ../..
        # to find the root.
        self.stage.stage(os.path.join('etc', self.__PKGNAME),
                         [os.path.join(nuodb.staged[0].basedir, 'drivers', 'pynuoadmin', 'nuocmd-complete')])

        self.stage.stage('jar', [os.path.join(nuodb.staged[0].basedir, 'jar', 'nuokeymanager.jar')])

        # Always install sh scripts: Windows may  have a POSIX shell available
        self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd')])
        self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['run-java-app.sh', 'nuokeymgr'])

        if Globals.target == 'win64':
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd.bat')])
            self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['nuokeymgr.bat'])



# Create and register this package
PyNuoadminPackage()
