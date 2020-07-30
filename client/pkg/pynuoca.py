# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the pynuoca module

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

    def install(self):
        self.stage.stage('jar', ['jar/'])
        self.stage.stage('conf', ['conf/'])
        ext = '' if Globals.target == 'lin64' else '.bat'
        self.stage.stagefiles('bin', 'bin', ['nuodb-migrator'+ext])


# Create and register this package
NuoCAPackage()
