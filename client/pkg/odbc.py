# (C) Copyright NuoDB, Inc. 2022  All Rights Reserved.
#
# Add the NuoDB ODBC client

import os
import re

from client.exceptions import CommandError
from client.package import Package
from client.stage import Stage
from client.artifact import GitHubRepo
from client.utils import Globals, rmdir, mkdir, which, run, runout


class ODBCPackage(Package):
    """Add the NuoDB ODBC client."""

    __PKGNAME = 'odbc'

    __USER = 'nuodb'
    __REPO = 'nuodb-odbc'

    # For now we just get the HEAD of the repo
    __TAG = 'pds/updates'

    def __init__(self):
        super(ODBCPackage, self).__init__(self.__PKGNAME)
        self._zip = None

        self.staged = [Stage('nuodbodbc',
                             title='NuoDB ODBC Driver',
                             requirements='NuoDB C++ Driver; either UnixODBC 2.3 or Windows')]
        self.stage = self.staged[0]

    def prereqs(self):
        # We need nuodb to get the C++ driver
        return ['nuodb']

    def download(self):
        nm = '{}/{}'.format(self.__USER, self.__REPO)
        self._repo = GitHubRepo(self.__USER, self.__REPO, nm, self.__TAG)
        self._repo.update()

    def make(self):
        nuodb = self.get_package('nuodb')
        self.distdir = os.path.join(self.stage.basedir, 'dist')
        self.homedir = nuodb.staged[0].basedir

        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        self.cmake = which('cmake')
        if self.cmake is None:
            raise CommandError("Cannot find cmake installed.")
        args = [self.cmake, self._repo.path,
                '-DCMAKE_BUILD_TYPE=RelWithDebInfo',
                '-DNUODB_HOME={}'.format(self.homedir)]
        args.append('-DCMAKE_INSTALL_PREFIX={}'.format(self.distdir))

        if not Globals.iswindows:
            incpath = os.environ.get('ODBC_INCLUDE')
            if incpath is None and Globals.thirdparty_common:
                incpath = os.path.join(Globals.thirdparty_common, 'unixODBC', 'include')
            if incpath:
                args.append('-DODBC_INCLUDE={}'.format(incpath))
            libpath = os.environ.get('ODBC_LIB')
            if libpath is None and Globals.thirdparty_arch:
                libpath = os.path.join(Globals.thirdparty_arch, 'unixODBC', 'lib')
            if libpath:
                args.append('-DODBC_LIB={}'.format(libpath))

        if Globals.cc:
            args.append('-DCMAKE_C_COMPILER={}'.format(Globals.cc))
        if Globals.cxx:
            args.append('-DCMAKE_CXX_COMPILER={}'.format(Globals.cxx))

        run(args, cwd=self.pkgroot)
        run([self.cmake, '--build', '.', '--target', 'install'], cwd=self.pkgroot)

    def test(self):
        reports = os.path.join(self.stage.basedir, 'test-reports')
        rmdir(reports)
        admin = os.path.join(self.homedir, 'etc', 'nuoadmin')
        nuocmd = os.path.join(self.homedir, 'bin', 'nuocmd')
        if Globals.iswindows:
            admin += '.bat'
            nuocmd += '.bat'

        os.environ['PATH'] = (os.path.join(self.homedir, 'bin')
                              + os.pathsep + os.environ['PATH'])

        # Disable TLS and start an AP
        run([admin, 'tls', 'disable'])
        run([admin, 'start'])
        os.environ.pop('NUOCMD_CLIENT_KEY', None)
        os.environ.pop('NUOCMD_VERIFY_SERVER', None)
        try:
            tscript = os.path.join(self._repo.path, 'etc', 'runtests')
            tscript += '.bat' if Globals.iswindows else '.sh'
            tbin = os.path.join(self.stage.basedir, 'test', 'NuoODBCTest')
            run([tscript, self.distdir, tbin,
                 '--gtest_output=xml:{}'.format(os.path.join(reports, 'NuoODBCTest-results.xml'))])
        except Exception:
            run([nuocmd, 'shutdown', 'database', '--db-name', 'NuoODBCTestDB'])
            run([nuocmd, 'check', 'database', '--db-name', 'NuoODBCTestDB',
                 '--num-processes', '0', '--timeout', '30'])
            raise
        finally:
            try:
                run([admin, 'stop'])
            finally:
                run([admin, 'tls', 'enable'])

    def install(self):
        # Once we've configured/built we can determine the version
        verfile = os.path.join(self.stage.basedir, 'src', 'ProductVersion.h')
        ver = {}
        with open(verfile, 'r') as f:
            for ln in f.readlines():
                m = re.match(r'\s*#\s*define\s+NUOODBC_VERSION_([^\s]+)\s+(\d+)', ln)
                if m:
                    ver[m.group(1)] = m.group(2)
        if len(ver) != 3:
            raise CommandError("Version info not found in {}".format(verfile))
        verstr = '{}.{}.{}'.format(ver['MAJOR'], ver['MINOR'], ver['MAINT'])
        self.setversion(verstr)

        if Globals.iswindows:
            self.stage.stagefiles('lib', os.path.join(self.distdir, 'lib'),
                                  ['NuoODBC.lib'])
            self.stage.stagefiles('bin', os.path.join(self.distdir, 'bin'),
                                  ['NuoODBC.dll', 'NuoODBC.pdb'])
        else:
            self.stage.stagefiles('lib64', os.path.join(self.distdir, 'lib64'),
                                  ['libNuoODBC.so'])


# Create and register this package
ODBCPackage()
