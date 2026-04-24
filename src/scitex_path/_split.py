#!/usr/bin/env python3
# Timestamp: "2026-01-08 02:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/path/_split.py

"""Path splitting utilities."""

import os
from pathlib import Path
from typing import Tuple, Union


def split(fpath: Union[str, Path]) -> Tuple[str, str, str]:
    """Split a file path into directory, filename, and extension.

    Parameters
    ----------
    fpath : str or Path
        File path to split.

    Returns
    -------
    tuple of (str, str, str)
        (directory with trailing slash, filename without extension, extension)

    Example
    -------
    >>> dirname, fname, ext = split('/path/to/file.txt')
    >>> dirname
    '/path/to/'
    >>> fname
    'file'
    >>> ext
    '.txt'
    """
    fpath = os.fspath(fpath) if not isinstance(fpath, str) else fpath
    dirname = os.path.dirname(fpath) + "/"
    basename = os.path.basename(fpath)
    fname, ext = os.path.splitext(basename)
    return dirname, fname, ext


# EOF
