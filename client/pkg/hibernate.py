# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Add the NuoDB hibernate clients

import os

from client.package import Package
from client.stage import Stage
from client.artifact import MavenMetadata, Artifact
from client.utils import mkdir, rmdir, copy, savefile

class HibernatePackage(Package):
    """Add the NuoDB Hibernate (3 and 5) clients."""

    __PKGNAME = 'hibernate'

    __PATH = 'com/nuodb/hibernate/nuodb-hibernate'
    __JAR = 'nuodb-hibernate-{}.jar'

    def __init__(self):
        super(HibernatePackage, self).__init__(self.__PKGNAME)
        self._hib3 = None
        self._hib5 = None

        self.staged = [Stage(name='hibernate3',
                             title='Hibernate3 Driver',
                             requirements='Java 8 or 11'),

                       Stage(name='hibernate5',
                             title='Hibernate5 Driver',
                             requirements='Java 8 or 11')]

        self.stage3 = self.staged[0]
        self.stage5 = self.staged[1]

    def download(self):
        # Hibernate is complicated because both versions 3 and 5 are released
        # in the same Maven repository.
        mvn = MavenMetadata(self.__PATH)

        # Find the newest hib3 and hib5 versions
        for ver in mvn.metadata.find('versioning/versions'):
            if ver.text.endswith('hib3'):
                self.stage3.version = ver.text
            elif ver.text.endswith('hib5'):
                self.stage5.version = ver.text

        self._hib3 = Artifact(self.name, 'nuodb-hibernate-hib3.jar',
                              '{}/{}/{}'.format(mvn.baseurl, self.stage3.version, self.__JAR.format(self.stage3.version)))

        self._hib5 = Artifact(self.name, 'nuodb-hibernate-hib5.jar',
                              '{}/{}/{}'.format(mvn.baseurl, self.stage5.version, self.__JAR.format(self.stage5.version)))

        # We only download the actual jar files
        self._hib3.update()
        self._hib5.update()

    def unpack(self):
        rmdir(self.pkgroot)
        mkdir(self.pkgroot)
        copy(self._hib3.path, os.path.join(self.pkgroot, 'nuodb-hibernate-hib3.jar'))
        copy(self._hib5.path, os.path.join(self.pkgroot, 'nuodb-hibernate-hib5.jar'))
        savefile(os.path.join(self.pkgroot, 'LICENSE.txt'), self.getlicense('3BSD'))

    def install(self):
        self.stage3.stage('jar', ['nuodb-hibernate-hib3.jar'])
        self.stage3.stage('doc', ['LICENSE.txt'])

        self.stage5.stage('jar', ['nuodb-hibernate-hib5.jar'])
        self.stage5.stage('doc', ['LICENSE.txt'])


# Create and register this package
HibernatePackage()
