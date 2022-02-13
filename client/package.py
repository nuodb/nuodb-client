# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.
#
# Base class for creating a package in nuodb-client.
# Each component in the client package should define a subclass of Package
# and override the methods necessary to add that component into the package.
#
# The steps in building a package are as follows:
#    prereqs()       : Set up any prerequisite packages
#    download()      : Download the third party package
#    validate()      : Validate the download
#    unpack()        : Unpack the downloaded content package
#    patch()         : Apply local patches to the package
#    test()          : Test the package
#    install()       : Install the package
#
#    clean()         : Clean the package

import os
import inspect

from datetime import datetime
from string import Template

from client.utils import Globals, info, rmdir


class Package(object):
    """Base class for a package."""

    _PACKAGES = {}

    @staticmethod
    def get_packages():
        return list(Package._PACKAGES)

    @staticmethod
    def get_package(name):
        return Package._PACKAGES.get(name)

    @classmethod
    def build_all(cls, pkglist):
        # Recursively discover prerequisites.  We won't try to remove
        # dups: we'll just only build things once.  It can get stuck in
        # infinite loop so... just don't do that!
        prereqs = []
        nextlist = list(pkglist)
        while nextlist:
            prereqs += list(nextlist)
            newlist = []
            for name in nextlist:
                pkg = Package._PACKAGES[name]
                newlist += pkg.prereqs()
            nextlist = newlist

        # The prereqs we want to build first are at the end
        prereqs.reverse()

        built = []
        for name in prereqs:
            if name not in built:
                pkg = Package._PACKAGES[name]
                pkg.build()
                built.append(name)

    @classmethod
    def getlicense(cls, name, holder='NuoDB, Inc.'):
        return Template(cls._LICENCES[name]).substitute({'YEAR': datetime.today().year, 'HOLDER': holder})

    def __init__(self, name):
        if name in Package._PACKAGES:
            raise RuntimeError("Duplicate Package object for package {}".format(name))
        Package._PACKAGES[name] = self

        self.name = name
        self.pkgroot = None
        self.building = False
        self.staged = []

    def _setup(self):
        if self.pkgroot:
            return

        self.pkgroot = os.path.join(Globals.pkgroot, self.name)

        fnm = inspect.getfile(self.__class__)
        fnm = '{}.py'.format(os.path.splitext(fnm)[0])
        modtm = os.path.getmtime(fnm)
        for stg in self.staged:
            stg.setup(self.pkgroot)

        for stg in self.staged:
            if os.path.exists(stg.stagefile) and modtm >= os.path.getmtime(stg.stagefile):
                stg.reset()

    def setversion(self, version):
        for stg in self.staged:
            stg.version = version

    def build(self):
        assert not self.building

        self._setup()

        self.building = True
        try:
            def runstep(name, func):
                info('{}: {}'.format(self.name, name.capitalize()))
                func()

            completed = all([stg.completed for stg in self.staged])

            if completed:
                info('{}: Reusing install'.format(self.name))
            else:
                runstep('download', self.download)
                runstep('validate', self.validate)
                runstep('unpack', self.unpack)
                runstep('patch', self.patch)
                runstep('make', self.make)
                runstep('test', self.test)

            runstep('install', self.install)

            info('{}: Staging'.format(self.name))
            for stg in self.staged:
                stg.complete()

        finally:
            self.building = False

    @staticmethod
    def prereqs():
        """Return a list of packages that need to be built before this one."""
        return []

    def clean(self, real=False):
        """Clean up the package."""
        self._setup()
        rmdir(self.pkgroot)
        for stg in self.staged:
            stg.clean()
        if real:
            rmdir(os.path.join(Globals.downloadroot, self.name))

    # ----- Package build steps

    def download(self):
        """Download anything needed to install the package."""
        pass

    def validate(self):
        """Validate the download."""
        pass

    def unpack(self):
        """Unpack the downloaded content into self.pkgroot."""
        pass

    def patch(self):
        """Apply any patches."""
        pass

    def make(self):
        """Perform any make operations."""
        pass

    def test(self):
        """Run any tests."""
        pass

    def install(self):
        """Install the final package contents into self.distroot.

        You can use the helper variables self.bindir, self.libdir, etc.
        """
        # Every package needs an install step
        raise NotImplementedError("install")

    # ---- Licenses

    _LICENCES = {'3BSD': """Copyright ${YEAR} ${HOLDER}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""",

                 'MIT': """Copyright ${YEAR} ${HOLDER}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""}
