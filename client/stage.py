# (C) Copyright NuoDB, Inc. 2019-2023  All Rights Reserved.

import os
import json

from client.utils import Globals, loadfile, savefile, getcontents
from client.utils import mkdir, rmdir, rmfile, copy, copyinto
from client.bundles import Bundles

class Stage(object):
    """Class representing the staged content of a client."""

    stagedir = None
    version = None

    basedir = None
    completed = None

    stagefile = None
    stagedir = None
    _staged = None

    # Any files here will be omitted from the generated results
    omitcontents = None

    # Any files here will be added to the generated results
    extracontents = None

    def __init__(self, name, title=None, requirements=None, notes=None, bundle=None, package=None):
        self.name = name
        self.title = title
        self.requirements = requirements
        self.notes = notes
        self.bundle = bundle
        self.package = package
        self._staged = []
        self.omitcontents = []
        self.extracontents = []

    def setup(self, basedir):
        stgroot = Globals.stageroot
        self.stagefile = os.path.join(stgroot, '{}.json'.format(self.name))
        self.stagedir = os.path.join(stgroot, self.name)

        if not os.path.exists(self.stagefile):
            self.reset()
        else:
            old = json.loads(loadfile(self.stagefile))
            for key, val in old.items():
                if getattr(self, key) is None:
                    setattr(self, key, val)

        if self.basedir is None:
            self.basedir = basedir

    def reset(self):
        self.completed = False
        self.version = None

    def stage(self, dest, files, ignore=None):
        self._staged.append((dest, list(files), ignore))

    def stagefiles(self, dest, src, files, ignore=None):
        self._staged.append((dest, [os.path.join(src, f) for f in files], ignore))

    def getstaged(self, dest):
        ret = []
        def cvt(fnm):
            if os.path.isabs(fnm):
                return fnm
            return os.path.join(self.stagedir, fnm)
        for d, lst, ign in self._staged:
            if d == dest:
                if ign is None:
                    ignored = []
                else:
                    ignored = ign(d, lst)
                for ll in lst:
                    if ll not in ignored:
                        ret.append(cvt(ll))
        return ret

    def clean(self):
        rmfile(self.stagefile)
        rmdir(self.stagedir)

    def complete(self):
        self.clean()
        for dat in self._staged:
            if dat[0] in ['doc', 'sample']:
                ddir = os.path.join(self.stagedir, dat[0], self.name)
            else:
                ddir = os.path.join(self.stagedir, dat[0])
            mkdir(ddir)
            for f in dat[1]:
                if not os.path.isabs(f):
                    f = os.path.join(self.basedir, f)
                if f.endswith('/'):
                    copyinto(f[:-1], ddir, ignore=dat[2])
                else:
                    copy(f, ddir, ignore=dat[2])

        self.completed = True

        # Save the details for the next run to avoid redoing it all
        vals = {}
        for key, val in self.__dict__.items():
            if val is not None and not key.startswith('_'):
                vals[key] = val

        savefile(self.stagefile, json.dumps(vals))

    def getcontents(self):
        assert self.completed
        contents = getcontents(self.stagedir)
        return [f for f in contents if f not in self.omitcontents] + self.extracontents
