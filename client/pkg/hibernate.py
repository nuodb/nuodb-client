# (C) Copyright NuoDB, Inc. 2019-2023  All Rights Reserved.
#
# Add the NuoDB hibernate clients

import os

from client.package import Package
from client.stage import Stage
from client.artifact import MavenMetadata, Artifact
from client.utils import mkdir, rmdir, copy, savefile
from client.bundles import Bundles


class HibernatePackage(Package):
    """Add the NuoDB Hibernate 5 and 6 client."""

    __PKGNAME = 'hibernate'

    __PATH = 'com/nuodb/hibernate/nuodb-hibernate'
    __JAR = 'nuodb-hibernate-{}.jar'

    def __init__(self):
        super(HibernatePackage, self).__init__(self.__PKGNAME)
        self._hib5 = None
        self._hib6 = None

        self.staged = [Stage(name='hibernate5',
                             title='Hibernate5 Driver',
                             requirements='Java 8 or 11',
                             bundle=Bundles.DRIVERS,
                             package=self.__PKGNAME),
                       Stage(name='hibernate6',
                             title='Hibernate6 Driver',
                             requirements='Java 11',
                             bundle=Bundles.DRIVERS,
                             package=self.__PKGNAME)]

        self.stage5 = self.staged[0]
        self.stage6 = self.staged[1]

    def download(self):
        # Hibernate is complicated because both versions 3 and 5 are released
        # in the same Maven repository.
        mvn = MavenMetadata(self.__PATH)
        self.set_repo(mvn.friendlytitle, mvn.friendlyurl)

        # Find the newest hib5 version
        for ver in mvn.metadata.find('versioning/versions'):
            if ver.text.endswith('hib5'):
                self.stage5.version = ver.text
            elif ver.text.endswith('hib6'):
                self.stage6.version = ver.text

        self._hib5 = Artifact(self.name, 'nuodb-hibernate-hib5.jar',
                             '{}/{}/{}'.format(mvn.baseurl,
                                               self.stage5.version,
                                               self.__JAR.format(self.stage5.version)))
        self._hib6 = Artifact(self.name, 'nuodb-hibernate-hib6.jar',
                             '{}/{}/{}'.format(mvn.baseurl,
                                               self.stage6.version,
                                               self.__JAR.format(self.stage6.version)))

        # We only download the actual jar files
        self._hib5.update()
        self._hib6.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        copy(self._hib5.path, os.path.join(self.pkgroot, 'nuodb-hibernate-hib5.jar'))
        copy(self._hib6.path, os.path.join(self.pkgroot, 'nuodb-hibernate-hib6.jar'))
        savefile(os.path.join(self.pkgroot, 'LICENSE.txt'), self.getlicense('3BSD'))

    def install(self):
        self.stage5.stage('jar', ['nuodb-hibernate-hib5.jar'])
        self.stage5.stage('doc', ['LICENSE.txt'])

        self.stage6.stage('jar', ['nuodb-hibernate-hib6.jar'])
        self.stage6.stage('doc', ['LICENSE.txt'])


# Create and register this package
HibernatePackage()
