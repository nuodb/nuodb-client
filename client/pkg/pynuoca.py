# (C) Copyright NuoDB, Inc. 2020  All Rights Reserved.
#
# Add the nuodb collection agent

import os

from client.package import Package
from client.stage import Stage
from client.artifact import PyPIMetadata, Artifact
from client.utils import *

class PyNuoCA(Package):
    """Add the NuoDB Collection Agent"""

    __PKGNAME = 'pynuoca'

    class PyDep:
        _file = ""
        _version = ""
        _basedir = ""

    dependencies = {'aenum': PyDep(),
                    'click': PyDep(),
                    'elasticsearch': PyDep(),
                    'python-dateutil': PyDep(),
                    'PyYaml': PyDep(),
                    'requests': PyDep(),
                    'wrapt': PyDep(),
                    'Yapsy': PyDep(),
                    'kafka-python': PyDep(),
                    'urllib3': PyDep(),
                    'six': PyDep(),
                    'certifi': PyDep(),
                    'chardet': PyDep(),
                    'idna': PyDep(),
                    'pytz': PyDep(),
                    }

    def __init__(self):
        super(PyNuoCA, self).__init__(self.__PKGNAME)
        self._file = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoDB Collection Agent',
                             requirements='Python 2')]
        # There's only one, make it simple
        self.stage = self.staged[0]

    def download(self):
        pass

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)

        run(['pip', 'install', self.__PKGNAME, '-t', self.pkgroot])

    def install(self):
        self.stage.stage('python', ['./'])

# Create and register this package
PyNuoCA()
