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
        self._ac_file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoAdmin Driver',
                             requirements='Python 2')]

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

        # Grab the latest version of argcomplete
        acpypi = PyPIMetadata('argcomplete')
        self._ac_version = acpypi.version
        self._ac_file = Artifact('argcomplete',
                                 'argcomplete-{}.tar.gz'.format(self._ac_version),
                                 acpypi.pkgurl,
                                 chksum=acpypi.pkgchksum)
        self._ac_file.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._file.path, self.pkgroot)
        self.stage.basedir = os.path.join(self.pkgroot, 'pynuoadmin-{}'.format(self.stage.version))

        unpack_file(self._ac_file.path, self.pkgroot)
        self.ac_basedir = os.path.join(self.pkgroot, 'argcomplete-{}'.format(self._ac_version))

    def install(self):
        pdir = os.path.join('python', 'pynuoadmin')
        self.stage.stage(pdir, ['nuodb_cli.py', 'nuodb_mgmt.py'])
        self.stage.stage('doc', ['README.rst'])

        acdir = os.path.join('python', 'argcomplete')
        self.stage.stage(acdir, [os.path.join(self.ac_basedir, 'argcomplete/')])
        self.stage.stage(acdir, [os.path.join(self.ac_basedir, 'LICENSE.rst')])

        if Globals.target == 'lin64':
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd')])
            self.stage.stagefiles('etc', Globals.etcdir, ['run-java-app.sh', 'nuokeymgr'])
        else:
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd.bat')])
            self.stage.stagefiles('etc', Globals.etcdir, ['nuokeymgr.bat'])

        nuodb = self.get_package('nuodb')
        self.stage.stage('jar', [os.path.join(nuodb.staged[0].basedir, 'jar', 'nuokeymanager.jar')])
        self.stage.stage(pdir, [os.path.join(nuodb.staged[0].basedir, 'drivers', 'pynuoadmin', 'nuocmd-complete')])


# Create and register this package
PyNuoadminPackage()
