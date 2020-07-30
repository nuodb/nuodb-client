# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.

"""
Manage artifacts used to create the client package.
"""

import os
import hashlib
import ssl
import json
import xml.etree.ElementTree as ET

try:
    # Python3
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
except ImportError:
    # Python2
    from urllib2 import urlopen, URLError, HTTPError

from client.exceptions import *
from client.utils import *


__CONTEXT = None
def _getremotedata(url):
    """Read a remote URL and return its data.
       This is probably not efficient for large downloads..."""

    global __CONTEXT
    if __CONTEXT is None:
        # Ignore cert: insecure but...
        __CONTEXT = ssl._create_unverified_context()

    remote = None
    try:
        verbose("Downloading: {}".format(url))
        try:
            remote = urlopen(url, context=__CONTEXT)
        except AttributeError:
            remote = urlopen(url)

        return remote.read()

    except HTTPError as ex:
        raise DownloadError("HTTP Error: {}\nFailed reading {}".format(str(ex.reason), url))
    except URLError as ex:
        raise DownloadError("URL Error: {}\nFailed reading {}".format(str(ex.reason), url))
    finally:
        if remote:
            remote.close()


class GitHubMetadata(object):
    """Retrieve the metadata for a GitHub release.
       metadata is a JSON object."""

    __METAURL = 'https://api.github.com/repos/{}/{}/releases/latest'

    def __init__(self, account, repo):
        super(GitHubMetadata, self).__init__()
        url = self.__METAURL.format(account, repo)
        self.metadata = json.loads(_getremotedata(url))
        self.version = self.metadata['name']

        if self.metadata['assets']:
            self.pkgurl = self.metadata['assets'][0]['browser_download_url']
        else:
            self.pkgurl = self.metadata['zipball_url']


class PyPIMetadata(object):
    """Retrieve the metadata for a PyPI project.
       metadata is a JSON object."""

    __METAURL = 'https://pypi.org/pypi/{}/json'

    def __init__(self, repo, extension='.tar.gz'):
        super(PyPIMetadata, self).__init__()
        url = self.__METAURL.format(repo)
        self.metadata = json.loads(_getremotedata(url))
        self.version = self.metadata['info']['version']
        if extension is None:
            # User doesn't care so choose the first one
            pkg = self.metadata['urls'][0]
        else:
            # Find the one the user asked for
            for pkg in self.metadata['urls']:
                if pkg['filename'].endswith(extension):
                    break
            else:
                raise DownloadError("No package ending in {} found at {}".format(extension, url))
        self.pkgurl = pkg['url']
        self.pkgchksum = pkg['digests']['sha256']


class MavenMetadata(object):
    """Retrieve the metadata for a Maven repository.
       metadata is an XML (ElementTree) object."""

    __BASEURL = 'https://repo1.maven.org/maven2/{}'
    __METAFILE = 'maven-metadata.xml'

    def __init__(self, path):
        super(MavenMetadata, self).__init__()
        self.baseurl = self.__BASEURL.format(path)
        url = '{}/{}'.format(self.baseurl, self.__METAFILE)
        self.metadata = ET.fromstring(_getremotedata(url))
        self.version = self.metadata.find('versioning/release').text


class BaseArtifact(object):
    """Base artifact class."""
    def __init__(self, pkg, local):
        self._pkg = pkg
        self._local = local
        self.path = os.path.join(Globals.downloadroot, pkg, local)

    def get(self):
        """Retrieve the artifact.
           Subclasses implement this."""
        raise NotImplementedError("get() is not implemented")

    def validate(self):
        """Return True if we've successfully retrieved the artifact."""
        return os.path.exists(self.path) and os.stat(self.path).st_size > 0

    def update(self):
        """Get the artifact if it's not already available.
           Users call this to retrieve artifacts."""
        if not self.validate():
            self.get()


class Artifact(BaseArtifact):
    """A downloaded artifact."""

    def __init__(self, pkg, local, url, chksum=None):
        super(Artifact, self).__init__(pkg, local)
        self.url = url
        self._chksum = chksum

    def get(self):
        mkdir(os.path.dirname(self.path))
        rmfile(self.path)

        data = _getremotedata(self.url)
        with open(self.path, "wb") as local:
            local.write(data)

    def validate(self):
        if not super(Artifact, self).validate():
            return False

        if not self._chksum:
            return True

        if len(self._chksum) == 32:
            hfn = hashlib.md5()
        else:
            hfn = hashlib.sha256()

        with open(self.path, "rb") as f:
            hfn.update(f.read())
        actual = hfn.hexdigest()

        return actual != self._chksum


class GitClone(BaseArtifact):
    """Class representing a Git clone."""

    _git = which('git')

    def __init__(self, pkg, local, url, ref):
        if not self._git:
            raise EnvironmentError("No git command found")

        super(GitClone, self).__init__(pkg, local)
        self.url = url
        self._ref = ref

    def _exists(self):
        return os.path.exists(os.path.join(self.path, '.git'))

    def _run(self, *args):
        run([self._git]+args, cwd=self.path)

    def _clone(self):
        # Don't keep around any half-completed repos
        rmdir(self.path)
        mkdir(os.path.dirname(self.path))
        run([self._git, 'clone', '--recursive', self.url, self.path])

    def get(self):
        if not self._exists():
            self.update()
        self._run('checkout', '-f', self._ref)
        self._run('submodule', 'update', '--recursive')

    def update(self):
        if not self._exists():
            self._clone()
            return

        # Reset to remove any modified files
        self._run('clean', '-fdx')
        self._run('reset', '--hard')

        # See if we want a SHA and of so, if it exists.  If so nothing to do.
        if re.match(r'[a-fA-F0-9]{5,40}$', self._ref):
            (ret, _, _) = runout([self._git, 'cat-file', '-e', self._ref+'^{commit}'], cwd=self.path)
            if ret == 0:
                return

        # Check out master, then fetch and reset hard.  This is in
        # case upstream has done a force-push
        self._run('checkout', '-f', 'master')
        self._run('fetch', '-p')
        self._run('reset', '--hard', 'origin/master')
