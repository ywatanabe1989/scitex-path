#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""copy_files / copy_the_file — file-copy helpers ported from scitex-gen.

The ``copy_the_file`` upstream had two bugs (undefined ``inspect`` and
``dst`` references) that are fixed here. ``_copy_a_file`` is exposed as
a private helper so the legacy import path keeps working — both
``copy_files`` and ``copy_the_file`` delegate to it.
"""
from __future__ import annotations

import inspect
import os
import shutil
from typing import Iterable, Union


def _split_basename(path: str) -> tuple[str, str]:
    """Return (fname, ext) for ``path``. ``ext`` includes the leading dot."""
    base = os.path.basename(path)
    fname, ext = os.path.splitext(base)
    return fname, ext


def _copy_a_file(src: str, dst: str, allow_overwrite: bool = False) -> None:
    """Copy a single file from ``src`` to ``dst``.

    If ``dst`` ends with ``/`` it is treated as a directory; the source
    basename is appended.

    Parameters
    ----------
    src : str
        Path to the source file.
    dst : str
        Path to the destination file or directory (with trailing slash).
    allow_overwrite : bool, optional
        Overwrite ``dst`` if it already exists. Defaults to False.
    """
    if src == "/dev/null":
        print("\n/dev/null was not copied.\n")
        return

    if dst.endswith(os.sep) or dst.endswith("/"):
        src_fname, src_ext = _split_basename(src)
        dst = dst + src_fname + src_ext

    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
        print(f'\nCopied "{src}" to "{dst}".\n')
        return

    if allow_overwrite:
        shutil.copyfile(src, dst)
        print(f'\nCopied "{src}" to "{dst}" (overwritten).\n')
        return

    print(f'\n"{dst}" exists and copying from "{src}" was aborted.\n')


def copy_files(
    src_files: Union[str, Iterable[str]],
    dists: Union[str, Iterable[str]],
    allow_overwrite: bool = False,
) -> None:
    """Copy one or more files to one or more destinations.

    Each (src, dst) pair runs through :func:`_copy_a_file`. ``dists``
    entries ending with ``/`` are treated as directories.

    Parameters
    ----------
    src_files : str or iterable of str
        Source path(s).
    dists : str or iterable of str
        Destination path(s) — file or directory (trailing slash).
    allow_overwrite : bool, optional
        Overwrite existing destinations. Defaults to False.
    """
    if isinstance(src_files, str):
        src_files = [src_files]
    if isinstance(dists, str):
        dists = [dists]
    for sf in src_files:
        for dst in dists:
            _copy_a_file(sf, dst, allow_overwrite=allow_overwrite)


def copy_the_file(sdir: str) -> None:
    """Copy the caller's source file to ``sdir``.

    Resolves the caller's filename via :mod:`inspect` and copies it to
    ``sdir`` (which should end with ``/`` for the dest-as-directory
    code path of :func:`_copy_a_file`).

    Skipped when the caller's filename contains ``ipython`` (which is
    how the legacy helper avoided crashing inside REPL sessions).
    """
    caller_filename = inspect.stack()[1].filename
    if "ipython" in caller_filename:
        return

    if not sdir.endswith(os.sep) and not sdir.endswith("/"):
        sdir = sdir + os.sep
    _copy_a_file(caller_filename, sdir)
