#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 20:48:24 (ywatanabe)"
# File: scitex-path/src/scitex_path/_version.py

import os
import re
from glob import glob


def find_latest(dirname, fname, ext, version_prefix="_v"):
    """Find the latest versioned file in a directory.

    Parameters
    ----------
    dirname : str
        Directory to search in.
    fname : str
        Base filename without version number or extension.
    ext : str
        File extension including the dot (e.g., '.txt').
    version_prefix : str, optional
        Prefix before the version number. Default is '_v'.

    Returns
    -------
    str or None
        Path to the latest versioned file, or None if not found.
    """
    version_pattern = re.compile(
        rf"({re.escape(fname)}{re.escape(version_prefix)})(\d+)({re.escape(ext)})$"
    )

    glob_pattern = os.path.join(dirname, f"{fname}{version_prefix}*{ext}")
    files = glob(glob_pattern)

    highest_version = 0
    latest_file = None

    for file in files:
        filename = os.path.basename(file)
        match = version_pattern.search(filename)
        if match:
            version_num = int(match.group(2))
            if version_num > highest_version:
                highest_version = version_num
                latest_file = file

    return latest_file


def increment_version(dirname, fname, ext, version_prefix="_v"):
    """Generate the next version of a filename based on existing versioned files.

    Parameters
    ----------
    dirname : str
        Directory to search in.
    fname : str
        Base filename without version number or extension.
    ext : str
        File extension including the dot (e.g., '.txt').
    version_prefix : str, optional
        Prefix before the version number. Default is '_v'.

    Returns
    -------
    str
        Full path for the next version of the file.

    Example
    -------
    >>> increment_version('/path/to/dir', 'myfile', '.txt')
    '/path/to/dir/myfile_v001.txt'
    """
    version_pattern = re.compile(
        rf"({re.escape(fname)}{re.escape(version_prefix)})(\d+)({re.escape(ext)})$"
    )

    glob_pattern = os.path.join(dirname, f"{fname}{version_prefix}*{ext}")
    files = glob(glob_pattern)

    highest_version = 0
    base, suffix = None, None

    for file in files:
        filename = os.path.basename(file)
        match = version_pattern.search(filename)
        if match:
            base, version_str, suffix = match.groups()
            version_num = int(version_str)
            if version_num > highest_version:
                highest_version = version_num

    if base is None or suffix is None:
        base = f"{fname}{version_prefix}"
        suffix = ext
        highest_version = 0

    next_version_number = highest_version + 1
    next_version_str = f"{base}{next_version_number:03d}{suffix}"

    next_filepath = os.path.join(dirname, next_version_str)

    return next_filepath


# EOF
