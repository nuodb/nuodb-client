# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the NuoDB hibernate clients

import os

from client.package import Package
from client.stage import Stage
from client.artifact import MavenMetadata, Artifact
from client.utils import mkdir, rmdir, copy, savefile


class HibernatePackage(Package):
    """Add the NuoDB Hibernate 5 client."""

    __PKGNAME = 'hibernate'

    __PATH = 'com/nuodb/hibernate/nuodb-hibernate'
    __JAR = 'nuodb-hibernate-{}.jar'

    def __init__(self):
        super(HibernatePackage, self).__init__(self.__PKGNAME)
        self._hib = None

        self.staged = [Stage(name='hibernate5',
                             title='Hibernate5 Driver',
                             requirements='Java 8 or 11')]

        self.stage = self.staged[0]

    def download(self):
        mvn = MavenMetadata(self.__PATH)

        # Find the newest hib5 versions
        for ver in mvn.metadata.find('versioning/versions'):
            self.stage.version = ver.text

        self._hib = Artifact(self.name, 'nuodb-hibernate-hib5.jar',
                              '{}/{}/{}'.format(mvn.baseurl,
                                                self.stage.version, self.__JAR.format(self.stage.version)))

        # We only download the actual jar files
        self._hib.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        copy(self._hib.path, os.path.join(self.pkgroot, 'nuodb-hibernate-hib5.jar'))
        savefile(os.path.join(self.pkgroot, 'LICENSE.txt'), self.getlicense('3BSD'))

    def install(self):
        self.stage.stage('jar', ['nuodb-hibernate-hib5.jar'])
        self.stage.stage('doc', ['LICENSE.txt'])


# Create and register this package
HibernatePackage()
