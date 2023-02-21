# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Extract client content from the NuoDB database package

import os

from client.exceptions import DownloadError, UnpackError
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

            'nuoclient': Stage('nuoclient',
                               title='C Driver',
                               requirements='GNU/Linux or Windows'),

            'nuoremote': Stage('nuoremote',
                               title='C++ Driver',
                               requirements='GNU/Linux or Windows'),
            'nuodump': Stage('nuodump',
                             title='NuoDB Logical Backup Tool',
                             requirements='GNU/Linux or Windows')
        }

        self.staged = list(self.stgs.values())

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
        if not os.path.exists(udir):
            raise UnpackError("Unpack did not create %s" % (udir))

        # Newer versions of NuoDB don't ship nuodbmanager any longer
        if not os.path.exists(os.path.join(udir, 'jar', 'nuodbmanager.jar')):
            verbose('Obsolete nuodbmanager is not present.')
            stg = self.stgs.pop('nuodbmgr')
            self.staged.remove(stg)

        for stg in self.staged:
            stg.basedir = udir

    def _install_linux(self):
        self.stgs['nuosql'].stagefiles('bin', 'bin', ['nuosql'])
        self.stgs['nuodump'].stagefiles('bin', 'bin', ['nuodump'])
        self.stgs['nuoloader'].stagefiles('bin', 'bin', ['nuoloader'])

        self.stgs['nuoclient'].stagefiles('lib64', 'lib64', ['libnuoclient.so'])

        # Include linux quickstart script
        self.stgs['nuoclient'].stage('samples', [os.path.join('samples', 'nuoadmin-quickstart')])

        # Add in shared libraries for packages that need it
        soglobs = ['libicu*.so.*', 'libmpir.so.*']
        for stg in ['nuosql', 'nuodump', 'nuoloader', 'nuoclient']:
            self.stgs[stg].stagefiles('lib64', 'lib64', soglobs)

        # C++ driver depends on the C driver
        self.stgs['nuoremote'].stagefiles('lib64', 'lib64', ['libNuoRemote.so'])
        self.stgs['nuoremote'].stage('lib64',
                                     self.stgs['nuoclient'].getstaged('lib64'))

        if 'nuodbmgr' in self.stgs:
            self.stgs['nuodbmgr'].stagefiles('jar', 'jar', ['nuodbmanager.jar'])
            # Get the client-specific version of these scripts
            self.stgs['nuodbmgr'].stage('bin', [os.path.join(Globals.bindir, 'nuodbmgr')])
            self.stgs['nuodbmgr'].stage('etc', [os.path.join(Globals.etcdir, 'run-java-app.sh')])

    def _install_windows(self):
        self.stgs['nuosql'].stagefiles('bin', 'bin', ['nuosql.exe'])
        self.stgs['nuodump'].stagefiles('bin', 'bin', ['nuodump.exe'])
        self.stgs['nuoloader'].stagefiles('bin', 'bin', ['nuoloader.exe'])

        self.stgs['nuoclient'].stagefiles('bin', 'bin', ['nuoclient.dll', 'nuoclient.pdb'])
        self.stgs['nuoclient'].stagefiles('lib', 'lib', ['nuoclient.lib'])

        # Include windows quickstart script
        self.stgs['nuoclient'].stage('samples', [os.path.join('samples', 'nuoadmin-quickstart.bat')])

        # Add in shared libraries for packages that need it
        soglobs = ['icu*.dll', 'mpir*.dll', 'msvcp140.dll', 'vcruntime140.dll']
        for stg in ['nuosql', 'nuodump', 'nuoloader', 'nuoclient']:
            self.stgs[stg].stagefiles('bin', 'bin', soglobs)

        # C++ driver depends on the C driver
        self.stgs['nuoremote'].stagefiles('lib', 'lib', ['NuoRemote.lib'])
        self.stgs['nuoremote'].stagefiles('bin', 'bin',
                                          ['NuoRemote.dll', 'NuoRemote.pdb'])
        self.stgs['nuoremote'].stage(
            'bin', self.stgs['nuoclient'].getstaged('bin'),
            ignore=lambda dst, lst: [f for f in lst if f.endswith('.pdb')])

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
        self.stgs['nuoclient'].stagefiles('include', 'include', ['nuodb'])
        self.stgs['nuoclient'].stage('samples', [os.path.join('samples', 'doc', 'c')])
        self.stgs['nuoremote'].stagefiles('include', 'include',
                                          ['NuoDB.h', 'SQLException.h',
                                           'SQLExceptionConstants.h', 'NuoRemote'])
        self.stgs['nuoremote'].stage('samples', [os.path.join('samples', 'doc', 'cpp')])

        # Include common Quickstart Hockey SQL sample files to be used in training sessions
        self.stgs['nuoclient'].stage('samples', [os.path.join('samples', 'quickstart')])
        self.stgs['nuoclient'].stage('samples', [os.path.join('samples', 'quickstart.py')])

        for stg in self.staged:
            stg.stage('doc', ['README.txt', 'license.txt', 'ce_license.txt'])


# Create and register this package
NuoDBPackage()
