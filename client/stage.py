# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.

import os
import json

from client.utils import Globals, loadfile, savefile, getcontents
from client.utils import mkdir, rmdir, rmfile, copy, copyinto


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
    omitcontents = []

    def __init__(self, name, title=None, requirements=None):
        self.name = name
        self.title = title
        self.requirements = requirements
        self._staged = {}

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

    def stage(self, dest, files):
        if dest not in self._staged:
            self._staged[dest] = []
        self._staged[dest].extend(files)

    def stagefiles(self, dest, src, files):
        if dest not in self._staged:
            self._staged[dest] = []
        self._staged[dest].extend([os.path.join(src, f) for f in files])

    def clean(self):
        rmfile(self.stagefile)
        rmdir(self.stagedir)

    def complete(self):
        self.clean()
        for dest, files in self._staged.items():
            if dest in ['doc', 'sample']:
                ddir = os.path.join(self.stagedir, dest, self.name)
            else:
                ddir = os.path.join(self.stagedir, dest)
            mkdir(ddir)
            for f in files:
                if not os.path.isabs(f):
                    f = os.path.join(self.basedir, f)
                if f.endswith('/'):
                    copyinto(f[:-1], ddir)
                else:
                    copy(f, ddir)

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
        return [f for f in contents if f not in self.omitcontents]
