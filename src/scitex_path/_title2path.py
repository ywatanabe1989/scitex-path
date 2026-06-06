#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: 2024-05-12 21:02:21 (7)
# File: ./src/scitex_path/_title2path.py
"""Convert a title (str or dict) to a path-friendly string.

Ported from scitex_gen._fs._title2path (Phase B retirement wave).
The dict-input branch delegates to ``scitex_dict.to_str`` (lazy import).
"""

from __future__ import annotations


def title2path(title):
    """
    Convert a title (string or dictionary) to a path-friendly string.

    Parameters
    ----------
    title : str or dict
        The input title to be converted.

    Returns
    -------
    str
        A path-friendly string derived from the input title.

    Example
    -------
    >>> title2path("My Title: A=1; B=2")
    'my_title_a1_b2'
    """
    if isinstance(title, dict):
        from scitex_dict import to_str

        title = to_str(title)

    path = title

    patterns = [":", ";", "=", "[", "]"]
    for pattern in patterns:
        path = path.replace(pattern, "")

    path = path.replace("_-_", "-")
    path = path.replace(" ", "_")

    while "__" in path:
        path = path.replace("__", "_")

    return path.lower()


# EOF
