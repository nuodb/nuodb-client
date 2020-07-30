# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the pynuoca module

import os

from client.package import Package
from client.stage import Stage
from client.artifact import GitHubMetadata, Artifact
from client.utils import *

class NuoCAPackage(Package):
    """Add the NuoDB Collection Agent."""

    __PKGNAME = 'pynuoca'

    __USER = 'nuodb'
    __REPO = 'nuoca'
    __ZIP = 'pynuoca.zip'

    def __init__(self):
        super(NuoCAPackage, self).__init__(self.__PKGNAME)
        self._zip = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoDB Collection Agent',
                             requirements='Python 2')]
        self.stage = self.staged[0]

    def download(self):
        repo = GitHubMetadata(self.__USER, self.__REPO)
        self.stage.version = repo.version

        self._zip = Artifact(self.name, self.__ZIP, repo.pkgurl)
        self._zip.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._zip.path, self.pkgroot)

        for file_name in os.listdir(self.pkgroot):
            self.stage.basedir = os.path.join(self.pkgroot, file_name)

    def install(self):
        if Globals.target != 'lin64':
            info('{}: Skipping on {} platform'.format(self.name, Globals.target))
            return

        self.stage.stage(self.__PKGNAME, ['src/'])

        self.stage.stage('etc', ['etc/'])
        self.stage.stage('lib', ['lib/'])
        self.stage.stage('plugins', ['plugins/'])

        self.stage.stage('bin', ['bin/'])

# Create and register this package
NuoCAPackage()
