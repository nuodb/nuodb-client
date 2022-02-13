# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the nuodb-jdbc client

import os

from client.package import Package
from client.stage import Stage
from client.artifact import MavenMetadata, Artifact
from client.utils import mkdir, rmdir, copy, savefile


class JDBCPackage(Package):
    """Add the NuoDB JDBC client."""

    __PKGNAME = 'jdbc'

    __PATH = 'com/nuodb/jdbc/nuodb-jdbc'
    __JAR = 'nuodb-jdbc-{}.jar'

    def __init__(self):
        super(JDBCPackage, self).__init__(self.__PKGNAME)
        self._jar = None

        self.staged = [Stage('nuodbjdbc',
                             title='NuoDB JDBC Driver',
                             requirements='Java 8 or 11')]

        self.stage = self.staged[0]

    def prereqs(self):
        # We need nuodb to get the samples
        return ['nuodb']

    def download(self):
        # Find the latest release
        mvn = MavenMetadata(self.__PATH)

        self.setversion(mvn.version)

        self._jar = Artifact(self.name, 'nuodbjdbc.jar',
                             '{}/{}/{}'.format(mvn.baseurl, mvn.version, self.__JAR.format(mvn.version)))

        # We only download the actual jar file
        self._jar.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        copy(self._jar.path, self.pkgroot)
        savefile(os.path.join(self.pkgroot, 'LICENSE.txt'), self.getlicense('3BSD'))

    def install(self):
        self.stage.stage('jar', ['nuodbjdbc.jar'])
        self.stage.stage('doc', ['LICENSE.txt'])

        nuodb = self.get_package('nuodb')
        self.stage.stage('samples', [os.path.join(nuodb.staged[0].basedir, 'samples', 'doc', 'java')])


# Create and register this package
JDBCPackage()
