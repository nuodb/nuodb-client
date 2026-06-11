# (C) Copyright NuoDB, Inc. 2019-2023  All Rights Reserved.
#
# Extract client content from the NuoDB database package

import os
import subprocess

from client.exceptions import DownloadError, UnpackError
from client.package import Package
from client.stage import Stage
from client.artifact import Artifact
from client.utils import Globals, mkdir, rmdir, loadfile, unpack_file, verbose, run, runout, copyinto
from client.bundles import Bundles


class NuoDBPackage(Package):
    """Extract NuoDB clients from the database package."""

    __PKGNAME = 'nuodb'

    def __init__(self):
        super(NuoDBPackage, self).__init__(self.__PKGNAME)
        self._pkg = None
        self._dirname = None

        self.stgs = {
            'nuosql': Stage('nuosql',
                            title='NuoDB SQL (nuosql)',
                            requirements='GNU/Linux or Windows',
                            bundle=Bundles.SQL_TOOLS,
                            package=self.__PKGNAME),

            'nuoloader': Stage('nuoloader',
                               title='NuoDB Loader (nuoloader)',
                               requirements='GNU/Linux or Windows',
                               bundle=Bundles.SQL_TOOLS,
                               package=self.__PKGNAME),

            'nuodbmgr': Stage('nuodbmgr',
                              title='nuodbmgr',
                              requirements='Java 8 or 11',
                              package=self.__PKGNAME),

            'nuoclient': Stage('nuoclient',
                               title='C Driver',
                               requirements='GNU/Linux or Windows',
                               bundle=Bundles.DRIVER_C,
                               package=self.__PKGNAME),

            'nuoremote': Stage('nuoremote',
                               title='C++ Driver',
                               requirements='GNU/Linux or Windows',
                               bundle=Bundles.DRIVER_CPP,
                               package=self.__PKGNAME),

            'nuodump': Stage('nuodump',
                             title='NuoDB Dump (nuodump)',
                             requirements='GNU/Linux or Windows',
                             bundle=Bundles.SQL_TOOLS,
                             package=self.__PKGNAME)
        }

        self.staged = list(self.stgs.values())

    def download(self):
        # Use Docker to pull the NuoDB image and extract files
        docker_image = 'nuodb/nuodb:latest'
        verbose(f"Pulling Docker image: {docker_image}")

        # Pull the Docker image
        (ret, out, err) = runout(['docker', 'pull', docker_image])
        if ret != 0:
            raise DownloadError(f"Failed to pull Docker image {docker_image}: {err}")

        # Create a temporary container to extract files
        container_name = 'nuodb-extract'
        verbose(f"Creating temporary container: {container_name}")
        (ret, out, err) = runout(['docker', 'create', '--name', container_name, docker_image])
        if ret != 0:
            raise DownloadError(f"Failed to create container {container_name}: {err}")

        # Extract files from the container
        extract_path = os.path.join(Globals.downloadroot, self.name)
        mkdir(extract_path)
        verbose(f"Extracting files to: {extract_path}")
        (ret, out, err) = runout(['docker', 'cp', f'{container_name}:/opt/nuodb', extract_path])
        if ret != 0:
            raise DownloadError(f"Failed to extract files from container: {err}")

        # Clean up the container
        verbose(f"Removing temporary container: {container_name}")
        run(['docker', 'rm', '-f', container_name])

        # Set the version and package details
        self._dirname = 'nuodb'
        self._pkg = Artifact(self.name, 'nuodb-extracted', extract_path)
        self._pkg.path = extract_path
        self.setversion('latest')
        self.set_repo('NuoDB Docker Image', docker_image)

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)

        # Copy extracted files to pkgroot
        src_path = self._pkg.path
        udir = os.path.join(self.pkgroot, self._dirname)
        mkdir(udir)
        copyinto(src_path, udir)

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
        if Globals.target.startswith('lin'):
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
