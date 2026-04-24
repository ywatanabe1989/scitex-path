#!/usr/bin/env python3
# Timestamp: "2026-01-08 02:00:00 (ywatanabe)"
# File: scitex-path/src/scitex_path/_getsize.py

"""File size utilities."""

import math
import os
from pathlib import Path
from typing import Union


def getsize(path: Union[str, Path]) -> Union[int, float]:
    """Get file size in bytes.

    Parameters
    ----------
    path : str or Path
        Path to file.

    Returns
    -------
    int or float
        File size in bytes, or math.nan if file doesn't exist.

    Raises
    ------
    PermissionError
        If the file cannot be accessed due to permissions.
    """
    path_str = os.fspath(path)
    if os.path.exists(path_str):
        return os.path.getsize(path_str)
    return math.nan


# EOF
