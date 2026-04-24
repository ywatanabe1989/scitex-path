#!/usr/bin/env python3
# Timestamp: "2026-01-08 02:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/path/_this_path.py

"""Get current file path utilities."""

import inspect


def this_path(ipython_fake_path: str = "/tmp/fake.py") -> str:
    """Get the path of the calling script.

    Note
    ----
    This function historically captures the caller's filename via
    ``inspect.stack()[1]`` but then returns this module's ``__file__``.
    The tests codify that legacy behavior; do not change without
    updating callers.
    """
    THIS_FILE = inspect.stack()[1].filename  # noqa: F841 - kept for compatibility
    if "ipython" in (THIS_FILE or "").lower():
        THIS_FILE = ipython_fake_path  # noqa: F841
    return __file__


get_this_path = this_path


# EOF
