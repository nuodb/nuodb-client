# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the nuodb-migrator client

from client.package import Package
from client.stage import Stage
from client.artifact import GitHubMetadata, Artifact
from client.utils import Globals, rmdir, mkdir, unpack_file


class MigratorPackage(Package):
    """Add the NuoDB migrator client."""

    __PKGNAME = 'migrator'

    __USER = 'nuodb'
    __REPO = 'migration-tools'
    __ZIP = 'nuodb-migrator.zip'

    def __init__(self):
        super(MigratorPackage, self).__init__(self.__PKGNAME)
        self._zip = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoDB Migrator',
                             requirements='Java 8 or 11')]
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
        ext = '.bat' if Globals.target.startswith('win') else ''
        self.stage.stagefiles('bin', 'bin', ['nuodb-migrator'+ext])


# Create and register this package
MigratorPackage()
