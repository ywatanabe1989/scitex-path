#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:00:00 (ywatanabe)"
# File: ./tests/scitex_path/test__mk_spath.py

"""Tests for ``scitex_path.mk_spath``.

PA-306: no ``unittest.mock``, no ``monkeypatch``. Collaborators are
swapped at module namespace level via real save/restore context managers.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, has
AAA markers, and a descriptive multi-token name.
"""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, Callable, Iterator, Tuple

import pytest

import scitex_path._mk_spath as _mk_spath_mod
from scitex_path import mk_spath

# ---------------------------------------------------------------------------
# Collaborator swaps (test seams — no mocks, no monkeypatch)
# ---------------------------------------------------------------------------


@contextmanager
def _swap_split(fn: Callable[[str], Tuple[str, str, str]]) -> Iterator[None]:
    """Replace ``_mk_spath.split`` with ``fn``."""
    saved = _mk_spath_mod.split
    _mk_spath_mod.split = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        _mk_spath_mod.split = saved  # type: ignore[assignment]


@contextmanager
def _swap_inspect_stack(stack: Any) -> Iterator[None]:
    """Replace ``inspect.stack`` (as imported into the module) with one returning ``stack``."""
    saved = _mk_spath_mod.inspect.stack
    _mk_spath_mod.inspect.stack = lambda: stack  # type: ignore[assignment]
    try:
        yield
    finally:
        _mk_spath_mod.inspect.stack = saved  # type: ignore[assignment]


@contextmanager
def _swap_module_dunder_file(new_file: str) -> Iterator[None]:
    """Replace ``_mk_spath.__file__`` with ``new_file``."""
    saved = _mk_spath_mod.__file__
    _mk_spath_mod.__file__ = new_file
    try:
        yield
    finally:
        _mk_spath_mod.__file__ = saved


@contextmanager
def _swap_os_makedirs(fn: Callable[..., None]) -> Iterator[list]:
    """Replace ``_mk_spath.os.makedirs`` with ``fn``; yield call recorder."""
    saved = _mk_spath_mod.os.makedirs
    calls: list = []

    def recording(*args: Any, **kwargs: Any) -> None:
        calls.append((args, kwargs))
        return fn(*args, **kwargs)

    _mk_spath_mod.os.makedirs = recording  # type: ignore[assignment]
    try:
        yield calls
    finally:
        _mk_spath_mod.os.makedirs = saved  # type: ignore[assignment]


def _frame(filename: str) -> SimpleNamespace:
    return SimpleNamespace(filename=filename)


# ---------------------------------------------------------------------------
# Default behaviour
# ---------------------------------------------------------------------------


def test_mk_spath_default_returns_string_path():
    # Arrange
    fake_stack = [None, _frame("/test/path/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/path/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/path/module.py"),
    ):
        result = mk_spath("output.txt")
    # Assert
    assert isinstance(result, str)


def test_mk_spath_default_ends_with_module_dir_plus_filename():
    # Arrange
    fake_stack = [None, _frame("/test/path/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/path/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/path/module.py"),
    ):
        result = mk_spath("output.txt")
    # Assert
    assert result.endswith("module/output.txt")


# ---------------------------------------------------------------------------
# Subdirectory in filename
# ---------------------------------------------------------------------------


def test_mk_spath_with_subdirectory_preserves_subpath_after_module_dir():
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/module.py"),
    ):
        result = mk_spath("subdir/output.txt")
    # Assert
    assert result.endswith("module/subdir/output.txt")


# ---------------------------------------------------------------------------
# makedirs=False suppresses directory creation
# ---------------------------------------------------------------------------


def test_mk_spath_makedirs_false_does_not_invoke_os_makedirs():
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    def noop_makedirs(*_a: Any, **_kw: Any) -> None:
        return None

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/module.py"),
        _swap_os_makedirs(noop_makedirs) as calls,
    ):
        mk_spath("output.txt", makedirs=False)
    # Assert
    assert calls == []


# ---------------------------------------------------------------------------
# makedirs=True creates the parent directory tree
# ---------------------------------------------------------------------------


def test_mk_spath_makedirs_true_creates_parent_directory_on_disk():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_module.py")
        fake_stack = [None, _frame(test_file)]

        def fake_split(path: str) -> Tuple[str, str, str]:
            if path == test_file:
                return (tmpdir + "/", "test_module", ".py")
            dir_part = os.path.dirname(path)
            if not dir_part.endswith("/"):
                dir_part += "/"
            return (dir_part, os.path.basename(path), "")

        expected_dir = os.path.join(tmpdir, "test_module", "subdir")
        # Act
        with (
            _swap_split(fake_split),
            _swap_inspect_stack(fake_stack),
            _swap_module_dunder_file(test_file),
        ):
            mk_spath("subdir/output.txt", makedirs=True)
        # Assert
        assert os.path.exists(expected_dir)


# ---------------------------------------------------------------------------
# iPython environment — function still returns a string
# ---------------------------------------------------------------------------


def test_mk_spath_in_ipython_environment_returns_string():
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    saved_user = os.environ.get("USER")
    os.environ["USER"] = "testuser"
    try:
        # Act
        with (
            _swap_split(fake_split),
            _swap_inspect_stack(fake_stack),
            _swap_module_dunder_file("/path/to/ipython/module.py"),
        ):
            result = mk_spath("output.txt")
        # Assert
        assert isinstance(result, str)
    finally:
        if saved_user is None:
            os.environ.pop("USER", None)
        else:
            os.environ["USER"] = saved_user


# ---------------------------------------------------------------------------
# Empty filename
# ---------------------------------------------------------------------------


def test_mk_spath_empty_filename_returns_module_dir_with_trailing_slash():
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/module.py"),
    ):
        result = mk_spath("")
    # Assert
    assert result.endswith("module/")


# ---------------------------------------------------------------------------
# Deep subdirectory path
# ---------------------------------------------------------------------------


def test_mk_spath_with_multiple_directory_levels_preserves_full_subpath():
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/module.py"),
    ):
        result = mk_spath("level1/level2/level3/output.txt")
    # Assert
    assert result.endswith("module/level1/level2/level3/output.txt")


# ---------------------------------------------------------------------------
# Extensions — one test per extension so each asserts one fact
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ext", [".txt", ".csv", ".json", ".tar.gz"])
def test_mk_spath_preserves_extension_in_returned_path(ext: str):
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/module.py"),
    ):
        result = mk_spath(f"output{ext}")
    # Assert
    assert result.endswith(f"module/output{ext}")


# ---------------------------------------------------------------------------
# Absolute input path is appended verbatim (legacy quirk)
# ---------------------------------------------------------------------------


def test_mk_spath_absolute_input_filename_is_concatenated_after_module_dir():
    # Arrange
    fake_stack = [None, _frame("/test/script.py")]

    def fake_split(_p: str) -> Tuple[str, str, str]:
        return ("/test/", "module", ".py")

    # Act
    with (
        _swap_split(fake_split),
        _swap_inspect_stack(fake_stack),
        _swap_module_dunder_file("/test/module.py"),
    ):
        result = mk_spath("/absolute/path/file.txt")
    # Assert
    assert result.endswith("module//absolute/path/file.txt")


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
