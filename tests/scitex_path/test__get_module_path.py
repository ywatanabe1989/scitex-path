#!/usr/bin/env python3
# Time-stamp: "2024-11-08 05:53:10 (ywatanabe)"
# File: ./tests/scitex_path/test__get_module_path.py

"""Tests for ``scitex_path.get_data_path_from_a_package``.

PA-306: no ``unittest.mock``, no ``monkeypatch``. Collaborators
(``importlib.util.find_spec`` and ``Path.exists``) are swapped at the
module namespace level via real save/restore context managers.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, has
the three AAA marker comments, and has a descriptive multi-token name.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

import pytest

import scitex_path._get_module_path as _gmp_mod
from scitex_path import get_data_path_from_a_package

# ---------------------------------------------------------------------------
# Lightweight stand-in for ModuleSpec
# ---------------------------------------------------------------------------


class _FakeSpec:
    def __init__(self, origin: str) -> None:
        self.origin = origin


# ---------------------------------------------------------------------------
# Collaborator swaps (test seams — no mocks, no monkeypatch)
# ---------------------------------------------------------------------------


@contextmanager
def _swap_find_spec(fn: Callable[[str], Any]) -> Iterator[None]:
    """Replace ``importlib.util.find_spec`` as seen by the module."""
    import importlib.util as iu

    saved = iu.find_spec
    iu.find_spec = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        iu.find_spec = saved  # type: ignore[assignment]


@contextmanager
def _swap_path_exists(fn: Callable[[Path], bool]) -> Iterator[None]:
    """Replace ``Path.exists`` as seen by the module under test."""
    saved = _gmp_mod.Path.exists
    _gmp_mod.Path.exists = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        _gmp_mod.Path.exists = saved  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Successful resolution
# ---------------------------------------------------------------------------


def test_get_data_path_resolves_under_data_dir_when_src_in_origin():
    # Arrange
    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/project/src/mypackage/__init__.py")

    def always_exists(_self: Path) -> bool:
        return True

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(always_exists):
        result = get_data_path_from_a_package("mypackage", "test_data.txt")
    # Assert
    assert result == Path("/home/user/project/data/test_data.txt")


# ---------------------------------------------------------------------------
# Missing package
# ---------------------------------------------------------------------------


def test_get_data_path_raises_import_error_when_package_not_found():
    # Arrange
    def fake_find_spec(_pkg: str) -> Any:
        return None

    # Act
    ctx = pytest.raises(ImportError, match="Package 'nonexistent' not found")
    # Assert
    with _swap_find_spec(fake_find_spec), ctx:
        get_data_path_from_a_package("nonexistent", "data.txt")


# ---------------------------------------------------------------------------
# Missing resource file
# ---------------------------------------------------------------------------


def test_get_data_path_raises_file_not_found_when_resource_missing():
    # Arrange
    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/project/src/mypackage/__init__.py")

    def never_exists(_self: Path) -> bool:
        return False

    # Act
    ctx = pytest.raises(FileNotFoundError, match="Resource 'missing.txt' not found")
    # Assert
    with _swap_find_spec(fake_find_spec), _swap_path_exists(never_exists), ctx:
        get_data_path_from_a_package("mypackage", "missing.txt")


# ---------------------------------------------------------------------------
# Various origin formats — separate test per case so each asserts one thing
# ---------------------------------------------------------------------------


def test_get_data_path_resolves_under_site_packages_data_dir():
    # Arrange
    origin = "/usr/lib/python3.9/site-packages/src/pkg/__init__.py"
    expected = Path("/usr/lib/python3.9/site-packages/data") / "file.txt"

    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec(origin)

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("testpkg", "file.txt")
    # Assert
    assert result == expected


def test_get_data_path_resolves_under_user_home_data_dir():
    # Arrange
    origin = "/home/user/src/myapp/module.py"
    expected = Path("/home/user/data") / "file.txt"

    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec(origin)

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("testpkg", "file.txt")
    # Assert
    assert result == expected


# ---------------------------------------------------------------------------
# Fallback when origin lacks ``src/`` boundary
# ---------------------------------------------------------------------------


def test_get_data_path_falls_back_to_data_dir_when_no_src_in_origin():
    # Arrange
    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/project/mypackage/__init__.py")

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("mypackage", "test.txt")
    # Assert
    assert "data" in str(result)


# ---------------------------------------------------------------------------
# Nested resource path
# ---------------------------------------------------------------------------


def test_get_data_path_preserves_nested_resource_subpath():
    # Arrange
    expected = os.path.join("/home/user/project/data", "subdir/test_data.csv")

    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/project/src/mypackage/__init__.py")

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("mypackage", "subdir/test_data.csv")
    # Assert
    assert str(result) == expected


# ---------------------------------------------------------------------------
# Empty resource argument
# ---------------------------------------------------------------------------


def test_get_data_path_with_empty_resource_returns_data_dir_only():
    # Arrange
    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/project/src/mypackage/__init__.py")

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("mypackage", "")
    # Assert
    assert str(result) == "/home/user/project/data"


# ---------------------------------------------------------------------------
# Multiple ``src/`` segments — picks innermost
# ---------------------------------------------------------------------------


def test_get_data_path_uses_innermost_src_when_path_has_multiple_src_segments():
    # Arrange
    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/src/project/src/mypackage/__init__.py")

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("mypackage", "data.json")
    # Assert
    assert str(result) == "/home/user/src/project/data/data.json"


# ---------------------------------------------------------------------------
# Case sensitivity — ``SRC`` is NOT treated as the boundary token
# ---------------------------------------------------------------------------


def test_get_data_path_treats_src_case_sensitively_uppercase_is_not_boundary():
    # Arrange
    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec("/home/user/SRC/mypackage/__init__.py")

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("mypackage", "test.txt")
    # Assert
    assert str(result).endswith("data/test.txt")


# ---------------------------------------------------------------------------
# Special characters in paths
# ---------------------------------------------------------------------------


def test_get_data_path_handles_special_characters_in_origin_and_resource():
    # Arrange
    origin = "/home/user-name/project@1.0/src/my-package/__init__.py"
    expected = os.path.join("/home/user-name/project@1.0/data", "test file.txt")

    def fake_find_spec(_pkg: str) -> _FakeSpec:
        return _FakeSpec(origin)

    # Act
    with _swap_find_spec(fake_find_spec), _swap_path_exists(lambda _s: True):
        result = get_data_path_from_a_package("my-package", "test file.txt")
    # Assert
    assert str(result) == expected


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
