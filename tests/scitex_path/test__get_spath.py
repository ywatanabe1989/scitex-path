#!/usr/bin/env python3
"""Backward-compat test for get_spath — now a thin alias for mk_spath.

The old test file patched `scitex_path._get_spath.split`, which no longer
exists after the module was simplified to re-export `mk_spath`. Detailed
behavior is covered by test__mk_spath.py; here we only verify that the
deprecated public name still resolves to the same callable.
"""

from __future__ import annotations


def test_get_spath_resolves_to_same_callable_as_mk_spath():
    # Arrange
    from scitex_path import get_spath
    from scitex_path._mk_spath import mk_spath

    # Act
    same = get_spath is mk_spath
    # Assert
    assert same is True


# EOF
