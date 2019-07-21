# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the pynuoadmin client

import os

from client.package import Package
from client.stage import Stage
from client.artifact import PyPIMetadata, Artifact
from client.utils import *

class PyNuoadminPackage(Package):
    """Add the NuoDB pynuoadmin client."""

    __PKGNAME = 'pynuoadmin'

    def __init__(self):
        super(PyNuoadminPackage, self).__init__(self.__PKGNAME)
        self._file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoAdmin Driver',
                             requirements='Python 2')]
        # There's only one, make it simple
        self.stage = self.staged[0]

    def prereqs(self):
        # We need nuodb to get nuokeymanager.jar
        return ['nuodb']

    def download(self):
        # Find the latest release
        pypi = PyPIMetadata('pynuoadmin')

        self.setversion(pypi.version)

        self._file = Artifact(self.name, 'pynuoadmin.tar.gz',
                              pypi.pkgurl, chksum=pypi.pkgchksum)
        self._file.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._file.path, self.pkgroot)
        self.stage.basedir = os.path.join(self.pkgroot, 'pynuoadmin-{}'.format(self.stage.version))

    def install(self):
        pdir = os.path.join('python', 'pynuoadmin')
        self.stage.stage(pdir, ['nuodb_cli.py', 'nuodb_mgmt.py'])
        self.stage.stage('doc', ['README.rst'])

        if Globals.target == 'lin64':
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd')])
            self.stage.stagefiles('etc', Globals.etcdir, ['run-java-app.sh', 'nuokeymgr'])
        else:
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd.bat')])
            self.stage.stagefiles('etc', Globals.etcdir, ['nuokeymgr.bat'])

        nuodb = self.get_package('nuodb')
        self.stage.stage('jar', [os.path.join(nuodb.staged[0].basedir, 'jar', 'nuokeymanager.jar')])


# Create and register this package
PyNuoadminPackage()
