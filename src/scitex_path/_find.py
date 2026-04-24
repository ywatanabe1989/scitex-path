#!/usr/bin/env python3
# Timestamp: "2026-01-08 02:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/path/_find.py

"""File and directory finding utilities."""

import fnmatch
import os
from pathlib import Path
from typing import List, Optional, Union


def find_git_root() -> str:
    """Find the root directory of the current git repository.

    Returns
    -------
    str
        Path to the git repository root.
    """
    import git

    repo = git.Repo(".", search_parent_directories=True)
    return repo.working_tree_dir


def find_dir(root_dir: Union[str, Path], exp: Union[str, List[str]]) -> List[str]:
    """Find directories matching pattern."""
    return _find(root_dir, type="d", exp=exp)


def find_file(root_dir: Union[str, Path], exp: Union[str, List[str]]) -> List[str]:
    """Find files matching pattern."""
    return _find(root_dir, type="f", exp=exp)


def _find(
    rootdir: Union[str, Path],
    type: Optional[str] = "f",
    exp: Union[str, List[str]] = "*",
) -> List[str]:
    """Mimics the Unix find command.

    Parameters
    ----------
    rootdir : str or Path
        Root directory to search in.
    type : str, optional
        'f' for files, 'd' for directories, None for both.
    exp : str or list of str
        Pattern(s) to match.

    Returns
    -------
    list of str
        Matching paths.

    Example
    -------
    >>> _find('/path/to/search', "f", "*.txt")
    """
    rootdir = str(rootdir)
    if isinstance(exp, str):
        exp = [exp]

    exclude_keys = ["/lib/", "/env/", "/build/"]
    matches: List[str] = []

    for dirpath, dirnames, filenames in os.walk(rootdir):
        candidates = []
        if type in (None, "f"):
            candidates.extend((os.path.join(dirpath, name), "f") for name in filenames)
        if type in (None, "d"):
            candidates.extend((os.path.join(dirpath, name), "d") for name in dirnames)

        for full_path, kind in candidates:
            # Verify type (tests mock os.path.isfile / isdir)
            if kind == "f" and not os.path.isfile(full_path):
                continue
            if kind == "d" and not os.path.isdir(full_path):
                continue

            name = os.path.basename(full_path)
            if not any(fnmatch.fnmatch(name, _exp) for _exp in exp if _exp):
                continue

            if any(ek in full_path for ek in exclude_keys):
                continue

            if full_path not in matches:
                matches.append(full_path)

    return matches


# EOF
