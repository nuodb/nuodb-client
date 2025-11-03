# (C) Copyright NuoDB, Inc. 2022-2023  All Rights Reserved.
#
# Add the NuoDB ODBC client

import os

from client.exceptions import DownloadError
from client.package import Package
from client.stage import Stage
from client.artifact import GitHubMetadata, Artifact
from client.utils import Globals, rmdir, mkdir, unpack_file
from client.bundles import Bundles


class ODBCPackage(Package):
    """Add the NuoDB ODBC client."""

    __PKGNAME = 'odbc'

    __USER = 'nuodb'
    __REPO = 'nuodb-odbc'
    __LX64 = 'linux.x86_64'
    __LARM64 = 'linux.arm64'
    __WIN = 'win64'

    def __init__(self):
        super(ODBCPackage, self).__init__(self.__PKGNAME)
        self._file = None

        self.staged = [Stage('nuodbodbc',
                             title='NuoDB ODBC Driver',
                             requirements='NuoDB C++ Driver; either UnixODBC 2.3 or Windows',
                             bundle=Bundles.ODBC,
                             package=self.__PKGNAME)]
        self.stage = self.staged[0]

    def _getext(self):
        if Globals.target == 'lin-x64':
            return self.__LX64
        if Globals.target == 'lin-arm64':
            return self.__LARM64
        else:
            return self.__WIN

    def prereqs(self):
        # We need nuodb to get the C++ driver
        return ['nuodb']

    def download(self):
        repo = GitHubMetadata(self.__USER, self.__REPO)
        self.set_repo(repo.friendlytitle, repo.friendlyurl)
        self.setversion(repo.version)

        ext = self._getext()
        name = None
        url = None
        for asset in repo.metadata['assets']:
            if ext in asset['name']:
                if name:
                    raise DownloadError("Multiple %s assets: %s, %s"
                                        % (ext, name, asset['name']))
                name = asset['name']
                url = asset['browser_download_url']
        if name is None:
            raise DownloadError("Cannot locate %s asset" % (ext))

        self._file = Artifact(self.name, name, url)
        self._file.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._file.path, self.pkgroot)

    def install(self):
        dirname = 'nuodbodbc-%s.%s' % (self.stage.version, self._getext())
        nuodb = self.get_package('nuodb')
        root = os.path.join(self.pkgroot, dirname)
        if Globals.target.startswith('lin'):
            self.stage.stagefiles('lib64', os.path.join(root, 'lib64'),
                                  ['libNuoODBC.so'])
            self.stage.stage('lib64', nuodb.stgs['nuoremote'].getstaged('lib64'))
        else:
            self.stage.stagefiles('lib', os.path.join(root, 'lib'),
                                  ['NuoODBC.lib'])
            bindir = os.path.join(root, 'bin')
            self.stage.stagefiles('bin', bindir, ['NuoODBC.dll', 'NuoODBC.pdb'])
            self.stage.stage('bin', nuodb.stgs['nuoremote'].getstaged('bin'),
                             ignore=lambda dst, lst: [f for f in lst if f.endswith('.pdb')])

        self.stage.stage('etc', [os.path.join(root, 'etc/')])


# Create and register this package
ODBCPackage()
