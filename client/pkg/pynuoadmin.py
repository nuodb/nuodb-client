# (C) Copyright NuoDB, Inc. 2019-2023  All Rights Reserved.
#
# Add the pynuoadmin client

import os
import shutil

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import Globals, getcontents, rmdir, mkdir, pipinstall
from client.bundles import Bundles


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
                             title='NuoAdmin Driver (pynuoadmin)',
                             requirements='Python 3',
                             package=self.__PKGNAME)]

        self.stage = self.staged[0]

    def prereqs(self):
        # We need nuodb to get nuokeymanager.jar and pynuoadmin uses pynuodb
        return ['nuodb', 'pynuodb']

    def unpack(self):
        pypi = PyPIMetadata(self.__PKGNAME)
        self.set_repo(pypi.friendlytitle, pypi.friendlyurl)
        self.setversion(pypi.version)

        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        if Globals.pythonversion < 3:
            # Unfortunately the latest pathlib2 requires typing, which breaks
            # p2<->p3 compatibility.  Force an older version.
            # Double unfortunately, this doesn't work.  We pre-install the
            # version we want, which SHOULD prevent pip from installing the
            # newer version since this version is sufficient and the default
            # upgrade strategy is "only-if-needed".  However, pip still
            # decides to ALSO install pathlib2-2.3.7 so now there are TWO
            # pathlib2 versions installed, and the "bad" one breaks things.
            pipinstall('pathlib2 < 2.3.7', self.pkgroot)
        pipinstall('%s[completion]==%s' % (self.__PKGNAME, pypi.version), self.pkgroot)

    def install(self):
        nopyc = shutil.ignore_patterns('*.pyc', '*.pyo')

        # We want all the packages, but not bin / etc / et.al.
        files = os.listdir(self.pkgroot)
        if 'bin' in files:
            files.remove('bin')
        if 'etc' in files:
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

        if Globals.target.startswith('win'):
            self.stage.stage('bin', [os.path.join(Globals.bindir, 'nuocmd.bat')])
            self.stage.stagefiles('etc', os.path.join(nuodb.staged[0].basedir, 'etc'), ['nuokeymgr.bat'])


# Create and register this package
PyNuoadminPackage()
