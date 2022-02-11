# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Extract client content from the NuoDB database package

import os

from client.exceptions import DownloadError
from client.package import Package
from client.stage import Stage
from client.artifact import Artifact
from client.utils import Globals, mkdir, rmdir, loadfile, unpack_file, verbose


class NuoDBPackage(Package):
    """Extract NuoDB clients from the database package."""

    __PKGNAME = 'nuodb'

    __NUODB_URL = 'https://ce-downloads.nuohub.org'
    __VERSIONS = 'supportedversions.txt'
    __TARFORMAT = 'nuodb-{}.linux.x86_64'
    __TAREXT = '.tar.gz'
    __ZIPFORMAT = 'nuodb-{}.win64'
    __ZIPEXT = '.zip'

    def __init__(self):
        super(NuoDBPackage, self).__init__(self.__PKGNAME)
        self._pkg = None
        self._dirname = None

        self.stgs = {
            'nuosql': Stage('nuosql',
                            title='nuosql',
                            requirements='GNU/Linux or Windows'),

            'nuoloader': Stage('nuoloader',
                               title='nuoloader',
                               requirements='GNU/Linux or Windows'),

            'nuodbmgr': Stage('nuodbmgr',
                              title='nuodbmgr',
                              requirements='Java 8 or 11'),

            'nuoremote': Stage('nuoremote',
                               title='C++ Driver',
                               requirements='GNU/Linux or Windows'),

            'nuoclient': Stage('nuoclient',
                               title='C Driver',
                               requirements='GNU/Linux or Windows')
        }

        self.staged = self.stgs.values()

    def download(self):
        versions = Artifact(self.name, self.__VERSIONS,
                            '{}/{}'.format(self.__NUODB_URL, self.__VERSIONS))
        versions.get()

        version = loadfile(versions.path).split()[-1]
        self.setversion(version)

        if Globals.target == 'lin64':
            fmt = self.__TARFORMAT
            ext = self.__TAREXT
        else:
            fmt = self.__ZIPFORMAT
            ext = self.__ZIPEXT

        try:
            self._dirname = fmt.format(version)
            pkgname = self._dirname + ext
            self._pkg = Artifact(self.name, pkgname,
                                 '{}/{}'.format(self.__NUODB_URL, pkgname))
            self._pkg.update()
        except DownloadError as ex:
            # Older releases publish packages named with a "ce" label; try that
            try:
                self._dirname = fmt.format('ce-'+version)
                pkgname = self._dirname + ext
                self._pkg = Artifact(self.name, pkgname,
                                     '{}/{}'.format(self.__NUODB_URL, pkgname))
                self._pkg.update()
            except DownloadError:
                raise ex

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        unpack_file(self._pkg.path, self.pkgroot)
        udir = os.path.join(self.pkgroot, self._dirname)

        # Newer versions of NuoDB don't ship nuodbmanager any longer
        if not os.path.exists(os.path.join(udir, 'jar', 'nuodbmanager.jar')):
            verbose('Obsolete nuodbmanager is not present.')
            stg = self.stgs.pop('nuodbmgr')
            self.staged.remove(stg)

        for stg in self.staged:
            stg.basedir = udir

    def _install_linux(self):
        self.stgs['nuosql'].stagefiles('bin', 'bin', ['nuosql'])
        self.stgs['nuoloader'].stagefiles('bin', 'bin', ['nuoloader'])

        self.stgs['nuoremote'].stagefiles('lib64', 'lib64', ['libNuoRemote.so'])
        self.stgs['nuoclient'].stagefiles('lib64', 'lib64', ['libnuoclient.so'])

        # Add in shared libraries for packages that need it
        soglobs = ['libicu*.so.*', 'libmpir.so.*']
        for stg in ['nuosql', 'nuoloader', 'nuoremote', 'nuoclient']:
            self.stgs[stg].stagefiles('lib64', 'lib64', soglobs)

        if 'nuodbmgr' in self.stgs:
            self.stgs['nuodbmgr'].stagefiles('jar', 'jar', ['nuodbmanager.jar'])
            # Get the client-specific version of these scripts
            self.stgs['nuodbmgr'].stage('bin', [os.path.join(Globals.bindir, 'nuodbmgr')])
            self.stgs['nuodbmgr'].stage('etc', [os.path.join(Globals.etcdir, 'run-java-app.sh')])

    def _install_windows(self):
        self.stgs['nuosql'].stagefiles('bin', 'bin', ['nuosql.exe'])
        self.stgs['nuoloader'].stagefiles('bin', 'bin', ['nuoloader.exe'])

        self.stgs['nuoremote'].stagefiles('bin', 'bin', ['NuoRemote.dll', 'NuoRemote.pdb'])
        self.stgs['nuoremote'].stagefiles('lib', 'lib', ['NuoRemote.lib'])
        self.stgs['nuoclient'].stagefiles('bin', 'bin', ['nuoclient.dll', 'nuoclient.pdb'])
        self.stgs['nuoclient'].stagefiles('lib', 'lib', ['nuoclient.lib'])

        # Add in shared libraries for packages that need it
        soglobs = ['icu*.dll', 'mpir*.dll', 'msvcp140.dll', 'vcruntime140.dll']
        for stg in ['nuosql', 'nuoloader', 'nuoremote', 'nuoclient']:
            self.stgs[stg].stagefiles('bin', 'bin', soglobs)

        if 'nuodbmgr' in self.stgs:
            self.stgs['nuodbmgr'].stagefiles('jar', 'jar', ['nuodbmanager.jar'])
            # Get the client-specific versions
            self.stgs['nuodbmgr'].stage('bin', [os.path.join(Globals.bindir, 'nuodbmgr.bat')])

    def install(self):
        if Globals.target == 'lin64':
            self._install_linux()
        else:
            self._install_windows()

        # Install header and sample files for C/C++ drivers
        self.stgs['nuoremote'].stagefiles('include', 'include',
                                          ['NuoDB.h', 'SQLException.h',
                                           'SQLExceptionConstants.h', 'NuoRemote'])
        self.stgs['nuoremote'].stage('samples', [os.path.join('samples', 'doc', 'cpp')])
        self.stgs['nuoclient'].stagefiles('include', 'include', ['nuodb'])
        self.stgs['nuoclient'].stage('samples', [os.path.join('samples', 'doc', 'c')])

        for stg in self.staged:
            stg.stage('doc', ['README.txt', 'license.txt', 'ce_license.txt'])


# Create and register this package
NuoDBPackage()
