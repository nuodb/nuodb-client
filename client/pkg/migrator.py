# (C) Copyright NuoDB, Inc. 2019-2023  All Rights Reserved.
#
# Add the nuodb-migrator client

from client.package import Package
from client.stage import Stage
from client.artifact import GitHubMetadata, Artifact
from client.utils import Globals, rmdir, mkdir, unpack_file
from client.bundles import Bundles


class MigratorPackage(Package):
    """Add the NuoDB migrator client."""

    __PKGNAME = 'migrator'

    __USER = 'nuodb'
    __REPO = 'migration-tools'
    __TAR = 'nuodb-migrator.tar'

    def __init__(self):
        super(MigratorPackage, self).__init__(self.__PKGNAME)
        self._tar = None

        self.staged = [Stage(self.__PKGNAME,
                             title='NuoDB Migrator (nuodb-migrator)',
                             requirements='Java 8 or 11',
                             bundle=Bundles.CLI_TOOLS,
                             package=self.__PKGNAME)]
        self.stage = self.staged[0]

    def download(self):
        repo = GitHubMetadata(self.__USER, self.__REPO)
        self.set_repo(repo.friendlytitle, repo.friendlyurl)
        self.stage.version = repo.version

        self._tar = Artifact(self.name, self.__TAR, repo.pkgurl)
        self._tar.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._tar.path, self.pkgroot)

    def install(self):
        self.stage.stage('jar', ['jar/'])
        self.stage.stage('conf', ['conf/'])
        ext = '.bat' if Globals.target.startswith('win') else ''
        self.stage.stagefiles('bin', 'bin', ['nuodb-migrator'+ext])


# Create and register this package
MigratorPackage()
