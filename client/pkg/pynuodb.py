# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the nuodb-python client

import os
import shutil

from client.artifact import PyPIMetadata
from client.package import Package
from client.stage import Stage
from client.utils import rmdir, mkdir, pipinstall, getcontents


class PyNuodbPackage(Package):
    """Add the NuoDB nuodb-python client."""

    __PKGNAME = 'pynuodb'

    def __init__(self):
        super(PyNuodbPackage, self).__init__(self.__PKGNAME)
        self._file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='Python Driver',
                             requirements='Python 2 or 3')]
        # There's only one, make it simple
        self.stage = self.staged[0]

    def unpack(self):
        pypi = PyPIMetadata(self.__PKGNAME)
        self.setversion(pypi.version)

        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        pipinstall('%s[crypto]==%s' % (self.__PKGNAME, pypi.version), self.pkgroot)

    def install(self):
        files = os.listdir(self.pkgroot)

        site = os.path.join('etc', 'python', 'site-packages')

        self.stage.stage(site, files, ignore=shutil.ignore_patterns('*.pyc', '*.pyo'))

        # We don't want to list all the pip-installed site-lisp package content
        for pth in files:
            if 'pynuodb' not in pth:
                self.stage.omitcontents.append(os.path.join(site, pth))
                for f in getcontents(os.path.join(self.pkgroot, pth)):
                    self.stage.omitcontents.append(os.path.join(site, pth, f))

        # But, add the site-package root elements to the contents output
        for pth in files:
            if ('pynuodb' not in pth and 'dist-info' not in pth
                    and 'egg-info' not in pth and not pth.endswith('.pyc')):
                self.stage.extracontents.append(os.path.join(site, pth))


# Create and register this package
PyNuodbPackage()
