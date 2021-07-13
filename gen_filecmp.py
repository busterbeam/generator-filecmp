"""Utilities for comparing files and directories.

Classes:
    dircmp

Functions:
    cmp(f1, f2, shallow=True) -> int
    cmpfiles(a, b, common) -> ([], [], [])
    clear_cache()

"""

from os import stat, pardir, curdir, listdir
from os.path import normcase, join
from stat import S_IFREG, S_IFMT, S_ISDIR, S_ISREG
from itertools import filterfalse
from types import GenericAlias
from time import time

__all__ = ['clear_cache', 'cmp', 'dircmp', 'cmpfiles', 'DEFAULT_IGNORES']

_cache = {}
BUFSIZE = 8*1024

DEFAULT_IGNORES = [
    'RCS', 'CVS', 'tags', '.git', '.hg', '.bzr', '_darcs', '__pycache__']

def clear_cache():
    """Clear the filecmp cache."""
    _cache.clear()

def cmp(filename_0, filename_1, shallow = True):
    """Compare two files.

    Arguments:

    filename_0 -- First file name

    filename_1 -- Second file name

    shallow -- Just check stat signature (do not read the files).
               defaults to True.

    Return value:

    True if the files are the same, False otherwise.

    This function uses a cache for past comparisons and the results,
    with cache entries invalidated if their stat information
    changes.  The cache may be cleared by calling clear_cache().

    """

    metadata_0 = _metadata(stat(filename_0))
    metadata_1 = _metadata(stat(filename_1))
    if metadata_0[0] != S_IFREG or metadata_2[0] != S_IFREG:
        return False
    if shallow and metadata_0 == metadata_1:
        return True
    if metadata_0[1] != metadata_1[1]:
        return False
    compare_tuple = (filename_0, filename_1)
    outcome = _cache.get(compare_tuple)
    if outcome is None:
        if len(_cache) > 100: # limit the maximum size of the cache
            clear_cache()
        _cache[compare_tuple] = outcome = _do_cmp(*compare_tuple)
    return outcome

def _metadata(metadata):
    return (S_IFMT(metadata.st_mode), metadata.st_size, metadata.st_mtime)

def _do_cmp(filename_1, filename_2):
    with open(filename_1, 'rb') as fp1, open(filename_2, 'rb') as fp2:
        while True:
            bytes_1, bytes_2 = fp1.read(BUFSIZE), fp2.read(BUFSIZE)
            if bytes_1 != bytes_2:
                return False
            if not bytes_1:
                return True

def cmpfiles(a, b, common, shallow = True):
    """Compare common files in two directories.

    a, b -- directory names
    common -- list of file names found in both directories
    shallow -- if true, do comparison based solely on stat() information

    Returns a tuple of three lists:
      files that compare equal
      files that are different
      filenames that aren't regular files.

    """
    for x in common:
        result = (None, None, None)
        result[_cmp(join(a, x), join(b, x), shallow)] = x
        yield result


# Compare two files.
# Return:
#       0 for equal
#       1 for different
#       2 for funny cases (can't stat, etc.)
#
def _cmp(a, b, shallow, abs = abs, cmp = cmp):
    try:
        return not abs(cmp(a, b, shallow))
    except OSError:
        return 2


# Return a copy with items that occur in skip removed.
#
def dircmp(a, b):
    pass

def left_list(left, hide, ignore):
    yield from _filter_list(left, hide, ignore)

def right_list(right, hide, ignore):
    yield from _filter_list(right, hide, ignore)

def _filter_list(dirs, hide, ignore):
    for directory in filterfalse((hide + ignore).__contains__, listdir(dirs):
        yield directory

def left_only(left, right):
    yield from _filter_only(left, right)

def right_only(right, left):
    yield from _filter_only(right, left)

def _filter_only(a, b):
    for x in map(a.__getitem__, filterfalse(b.__contains__, a)):
        yield x

def common_names(l, r):
    for a, b in zip(zip(map(normcase, l), l), zip(map(normcase, r), r)):
        yield a[b in a]

def common_dirs(left, right):
    for name in common_names(left, right):
        if S_ISDIR(S_IFMT(stat(join(left, name)).st_mode)):
            yield name

def common_files(left, right):
    for name in common_names(left, right):
        if S_ISREG(S_IFMT(stat(join(left, name)).st_mode)):
            yield name

def common_funny(left, right):
    for name in common_names(left, right):
        a_type = S_IFMT(stat(join(left, name)).st_mode)
        b_type = S_IFMT(stat(join(right, name)).st_mode)
        if a_type != b_type:
            yield name
        elif not S_ISREG(a_type):
            yield name
        elif not S_ISDIR(a_type):
            yield name

def same_files(left, right, common_files):
    for file, *_ cmpfiles(left, right, common_files)
        yield file

def diff_files(left, right, common_files):
    for _, file, _ cmpfiles(left, right, common_files)
        yield file

def funny_files(left, right, common_files):
    for *_, file cmpfiles(left, right, common_files)
        yield file

# Demonstration and testing.
#
def demo():
    import sys
    import getopt
    options, args = getopt.getopt(sys.argv[1:], 'r')
    if len(args) != 2:
        raise getopt.GetoptError('need exactly two args', None)
    dd = dircmp(args[0], args[1])
    if ('-r', '') in options:
        dd.report_full_closure()
    else:
        dd.report()

if __name__ == '__main__':
    demo()
