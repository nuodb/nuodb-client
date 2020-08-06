# (C) Copyright NuoDB, Inc. 2019  All Rights Reserved.

__all__ = ['Globals', 'info', 'verbose', 'error',
           'mkdir', 'rmrf', 'rmdir', 'rmfile', 'rmfiles',
           'copy', 'copyinto', 'copyfiles', 'getcontents',
           'loadfile', 'savefile', 'unpack_file',
           'which', 'runcmd', 'run', 'runout', 'runpip']

import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import glob

from client.exceptions import *


class Globals(object):
    """Class containing global settings."""

    clientroot = None
    bindir = None
    etcdir = None

    downloadroot = None
    finalroot = None
    tmproot = None
    targroot = None
    pkgroot = None
    stageroot = None

    target = None

    isverbose = False
    iswindows = sys.platform == 'win32'

    @classmethod
    def init(cls, **kwargs):
        for key, val in kwargs.items():
            setattr(cls, key, val)

        if cls.bindir is None:
            cls.bindir = os.path.join(cls.clientroot, 'bin')
        if cls.etcdir is None:
            cls.etcdir = os.path.join(cls.clientroot, 'etc')
        if cls.downloadroot is None:
            cls.downloadroot = os.path.join(cls.clientroot, 'downloads')
        if cls.finalroot is None:
            cls.finalroot = os.path.join(cls.clientroot, 'package')
        if cls.tmproot is None:
            cls.tmproot = os.path.join(cls.clientroot, 'obj')

    @classmethod
    def setup(cls, **kwargs):
        for key, val in kwargs.items():
            setattr(cls, key, val)

        if cls.targroot is None:
            cls.targroot = os.path.join(cls.tmproot, cls.target)
        if cls.pkgroot is None:
            cls.pkgroot = os.path.join(cls.targroot, 'pkg')
        if cls.stageroot is None:
            cls.stageroot = os.path.join(cls.targroot, 'stage')


# ----- Information

def info(text):
    sys.stdout.write(text+"\n")
    sys.stdout.flush()

def verbose(text):
    if Globals.isverbose:
        info(text)

def error(text):
    sys.stderr.write(text+"\n")
    sys.stderr.flush()

# ----- Manage directories

def mkdir(newpath):
    try:
        os.makedirs(newpath)
    except OSError as ex:
        if ex.errno != os.errno.EEXIST:
            raise

def _rmdir_helper(func, path, _):
    if func == os.remove:
        rmfile(path)
    else:
        raise OSError(1, "Failed to remove {}".format(path))

def rmdir(dirname):
    verbose("Removing directory {}".format(dirname))
    if dirname == '/' or dirname == '.':
        raise OSError(2, "Invalid path to rmdir: {}".format(dirname))
    if os.path.exists(dirname):
        shutil.rmtree(dirname, False, _rmdir_helper)

def rmfile(filename):
    verbose("Removing file {}".format(filename))
    if os.path.exists(filename):
        if not os.path.islink(filename):
            os.chmod(filename, stat.S_IREAD|stat.S_IWRITE)
        os.remove(filename)

def rmfiles(files):
    for f in files:
        rmfile(f)

def rmrf(paths):
    for path in paths:
        if os.path.isdir(path):
            rmdir(path)
        else:
            rmfile(path)

# Copies SRC to DST
# Uses shutil.copy2()
def copy(src, dst):
    verbose("  Copying {} to {}".format(src, dst))
    if os.path.isdir(src):
        if os.path.exists(dst):
            dst = os.path.join(dst, os.path.basename(src))
            if os.path.exists(dst):
                copyinto(src, dst)
                return
        shutil.copytree(src, dst, symlinks=True)
    else:
        for path in glob.glob(src):
            shutil.copy2(path, dst)


# Copies SRCDIR to DSTDIR
# Copies the contents of SRCIR into DSTDIR
def copyinto(srcdir, dstdir):
    for fnm in os.listdir(srcdir):
        copy(os.path.join(srcdir, fnm), dstdir)


# Copy SRCLIST from SRCDIR to DSTDIR
def copyfiles(srclist, srcdir, dstdir):
    for src in srclist:
        copy(os.path.join(srcdir, src), dstdir)


# Return a list of the files (not directories) starting at basedir
# but without including basedir in their paths.  If subdir is given then
# include only the contents of that subdirectory, but still rooted at basedir.
def getcontents(basedir, subdir=None):
    if not subdir:
        start = basedir
    elif subdir.startswith(basedir):
        start = subdir
    else:
        start = os.path.join(basedir, subdir)
    contents = []
    for root, _, files in os.walk(start):
        contents += [os.path.join(root, f)[len(basedir)+1:] for f in files]
    return contents


# ----- Load / save files

def loadfile(filename):
    with open(filename, "r") as f:
        return f.read()

def savefile(filename, txt):
    with open(filename, "w") as f:
        f.write(txt)

def unpack_file(filenm, dest):
    # Ugh.  On Windows we have to use --force-local with tar otherwise
    # filenames with drive specifiers are considered remote files.  But we
    # can't use this always because MacOS doesn't use GNU tar and their
    # tar doesn't support --force-local.
    tarargs = ['--force-local'] if Globals.iswindows else []

    mkdir(dest)

    if filenm.endswith('.tar.xz'):
        run("xz -d -c {} | tar xf - {}".format(filenm, ' '.join(tarargs)),
            cwd=dest, shell=True)
        return

    if filenm.endswith('.tar.bz2'):
        cmd = ['tar', '-x']+tarargs+['-j', '-f', filenm]

    elif filenm.endswith('.tar.gz') or filenm.endswith('.tgz'):
        cmd = ['tar', '-x']+tarargs+['-z', '-f', filenm]

    elif filenm.endswith('.tar.lz') or filenm.endswith('.tlz'):
        cmd = ['tar', '-x']+tarargs+['--lzip', '-f', filenm]

    elif filenm.endswith('.tar'):
        cmd = ['tar', '-x']+tarargs+['-f', filenm]

    elif filenm.endswith('.zip'):
        cmd = ['unzip', filenm]

    else:
        raise UnpackError("Unknown local file type: "+filenm)

    verbose("Unpacking {} using {} ...".format(filenm, cmd[0]))
    (ret, out, err) = runout(cmd, cwd=dest)
    if ret != 0:
        raise UnpackError("Failed to extract {}:\n{}{}".format(filenm, out, err))

# ----- Run commands

# Find a program (taken from build/test/shared/python/NuoDBOS.py:
# If the program is fully-qualified
# - Looks first in extrapaths if given.
# - Lastly looks in PATH
def which(prog, extrapaths=None):
    if os.path.dirname(prog):
        # It's a pathname, not just a file, so don't search paths
        return findprog(prog)

    def ext_candidates(path):
        if Globals.iswindows:
            # If path has an extension already try path first.
            if os.path.splitext(path)[1]:
                yield path
            # Next try adding each extension in PATHEXT
            for evar in os.environ.get("PATHEXT", "").lower().split(os.pathsep):
                yield path + evar
        else:
            yield path

    def findprog(path):
        for exe in ext_candidates(path):
            if os.path.isfile(exe) and os.access(exe, os.X_OK):
                return exe
        return None

    paths = list(extrapaths) if extrapaths else []
    paths += os.environ.get("PATH", "").split(os.pathsep)

    for path in paths:
        exe = findprog(os.path.join(path, prog))
        if exe is not None:
            return exe
    return None

_SPECIAL_CHARS = None
def _quotearg(arg):
    global _SPECIAL_CHARS
    if not _SPECIAL_CHARS:
        _SPECIAL_CHARS = re.compile(r"[\s~`'!#$&*{}|;<>[\]\""+(r'' if Globals.iswindows else r'\\')+'?]')

    if arg and not _SPECIAL_CHARS.search(arg):
        return arg

    if Globals.iswindows:
        return '"{}'.format(arg.replace('"', r'\"'))

    return "'{}'".format(arg.replace("'", r"'\''"))

def _getcmd(args, kwargs):
    shl = ', shell={}'.format(str(kwargs['shell']) if 'shell' in kwargs else '')
    return '{}>> {}{}'.format(kwargs.get('cwd', '.'),
                              ' '.join([_quotearg(a) for a in args]),
                              shl)

def runcmd(args, **kwargs):
    argstr = _getcmd(args, kwargs)

    # If we want to run a shell, just use a single string
    if kwargs.get('shell'):
        args = ' '.join(args)

    verbose(argstr)

    # The crazy preexec_fn stuff works around a horrible bug in Python 2.7,
    # which they "fixed" in Python 3 but have not backported.  This causes all
    # kinds of subtle havoc.  See:
    #
    #  http://bugs.python.org/issue1652
    #  http://www.chiark.greenend.org.uk/ucgi/~cjwatson/blosxom/2009-07-02-python-sigpipe.html
    #  https://blog.nelhage.com/2010/02/a-very-subtle-bug/
    #  http://gmplib.org/list-archives/gmp-bugs/2008-August/001114.html

    def _wrap_sigdfl(func=None):
        if func:
            func()
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    ufn = kwargs.get('preexec_fn')
    kwargs['preexec_fn'] = lambda: _wrap_sigdfl(ufn)

    # Run the program
    sys.stdout.flush()
    return subprocess.Popen(args, **kwargs)

def run(args, **kwargs):
    try:
        proc = runcmd(args, **kwargs)
    except Exception as ex:
        if not Globals.isverbose:
            info("Starting: {}".format(_getcmd(args, kwargs)))
        info("{}\nFailed!".format(str(ex)))
        raise
    ret = proc.wait()
    if ret != 0:
        raise CommandError("Failed ({}): {}".format(ret, _getcmd(args, kwargs)))

def runout(args, **kwargs):
    # Run a command and return (code, stdout, stderr)
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.PIPE
    try:
        proc = runcmd(args, **kwargs)
        (out, err) = proc.communicate()
        return (proc.wait(), out, err)
    except StandardError as ex:
        return (1, '', str(ex))


def runpip(package_name, package_root):
    return run([sys.executable, '-m', 'pip', 'install', package_name, '-t', package_root])
