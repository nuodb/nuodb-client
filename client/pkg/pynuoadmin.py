# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the pynuoadmin client

import os

from client.package import Package
from client.stage import Stage
from client.utils import rmdir, mkdir, runpip, Globals


class PyNuoadminPackage(Package):
    """Add the NuoDB pynuoadmin client."""

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
        # We need nuodb to get nuokeymanager.jar
        return ['nuodb']

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        runpip(self.__PKGNAME, self.pkgroot)

    def install(self):
        self.stage.stage('python', ['./'])

        nuodb = self.get_package('nuodb')
        self.stage.stage('jar', [os.path.join(nuodb.staged[0].basedir, 'jar', 'nuokeymanager.jar')])
        self.stage.stage('python', [os.path.join(nuodb.staged[0].basedir, 'drivers', 'pynuoadmin', 'nuocmd-complete')])

        if Globals.target == 'lin64':
            self.stage.stage('bin', [os.path.join(nuodb.staged[0].basedir, 'bin', 'nuocmd')])
            self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['run-java-app.sh', 'nuokeymgr'])
        else:
            self.stage.stage('bin', [os.path.join(nuodb.staged[0].basedir, 'bin', 'nuocmd.bat')])
            self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['nuokeymgr.bat'])



# Create and register this package
PyNuoadminPackage()
