# (C) Copyright NuoDB, Inc. 2020  All Rights Reserved.
#
# Add the nuodb collection agent

import os
import shutil

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import rmdir, mkdir, pipinstall, getcontents


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
        # We want all the packages, but not bin / etc / et.al.
        files = os.listdir(self.pkgroot)
        files.remove('bin')
        files.remove('etc')

        site = os.path.join('etc', 'python', 'site-packages')

        self.stage.stage(site, files, ignore=shutil.ignore_patterns('*.pyc', '*.pyo'))

        # We don't want to list all the pip-installed site-lisp package content
        for pth in files:
            if 'pynuoca' not in pth:
                self.stage.omitcontents.append(os.path.join(site, pth))
                for f in getcontents(os.path.join(self.pkgroot, pth)):
                    self.stage.omitcontents.append(os.path.join(site, pth, f))

        # But, add the site-package root elements to the contents output
        for pth in files:
            if ('pynuoca' not in pth and 'dist-info' not in pth
                    and 'egg-info' not in pth and not pth.endswith('.pyc')):
                self.stage.extracontents.append(os.path.join(site, pth))

        etc = [os.path.join('etc', f) for f in os.listdir(os.path.join(self.pkgroot, 'etc')) if f.startswith('nuoca')]

        self.stage.stage('etc', etc)
        self.stage.stage('bin', [os.path.join('bin', 'nuoca')])


# Create and register this package
PyNuoCA()
