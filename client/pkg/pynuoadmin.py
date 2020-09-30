# (C) Copyright NuoDB, Inc. 2019-2020  All Rights Reserved.
#
# Add the pynuoadmin client

import os
import shutil

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import Globals, getcontents, rmdir, mkdir, pipinstall


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
        pipinstall('%s[completion,crypto]==%s' % (self.__PKGNAME, pypi.version), self.pkgroot)

    def install(self):
        nopyc = shutil.ignore_patterns('*.pyc', '*.pyo')

        # We want all the packages, but not bin / etc / et.al.
        files = os.listdir(self.pkgroot)
        files.remove('bin')
        files.remove('etc')

        site = os.path.join('etc', 'python', 'site-packages')

        self.stage.stage(site, files, ignore=nopyc)

        # We don't want to list all the pip-installed site-lisp package content
        for pth in files:
            if 'pynuoadmin' not in pth:
                self.stage.omitcontents.append(os.path.join(site, pth))
                for f in getcontents(os.path.join(self.pkgroot, pth)):
                    self.stage.omitcontents.append(os.path.join(site, pth, f))

        # But, add the site-package root elements to the contents output
        for pth in files:
            if ('pynuoadmin' not in pth and 'dist-info' not in pth
                    and 'egg-info' not in pth and not pth.endswith('.pyc')):
                self.stage.extracontents.append(os.path.join(site, pth))

        nuodb = self.get_package('nuodb')

        # This needs to go two levels below the root, as it contains a ../..
        # to find the root.
        self.stage.stage('etc',
                         [os.path.join(nuodb.staged[0].basedir, 'drivers', 'pynuoadmin', 'nuocmd-complete')],
                         ignore=nopyc)

        self.stage.stage('jar', [os.path.join(nuodb.staged[0].basedir, 'jar', 'nuokeymanager.jar')])

        # Always install sh scripts: Windows may  have a POSIX shell available
        self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd')])
        self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['run-java-app.sh', 'nuokeymgr'])

        if Globals.target == 'win64':
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd.bat')])
            self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['nuokeymgr.bat'])


# Create and register this package
PyNuoadminPackage()
