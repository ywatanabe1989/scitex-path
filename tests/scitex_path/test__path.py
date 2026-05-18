#!/usr/bin/env python3
# Time-stamp: "2024-11-08 05:54:25 (ywatanabe)"
# File: ./tests/scitex_path/test__path.py

"""Tests for ``scitex_path._path`` (legacy alias module).

These mirror ``test__this_path.py`` but exercise the public-name aliases
exported from ``_path``.

PA-306: no ``unittest.mock``, no ``monkeypatch``. Collaborators are
swapped at the module namespace via real save/restore context managers.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, has
AAA markers, and a descriptive multi-token name.
"""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, Iterator, List

import pytest

import scitex_path._this_path as _this_path_mod
from scitex_path import get_this_path, this_path

# ---------------------------------------------------------------------------
# Collaborator swaps (test seams — no mocks, no monkeypatch)
# ---------------------------------------------------------------------------


@contextmanager
def _swap_inspect_stack(stack: List[Any]) -> Iterator[None]:
    """Replace ``_this_path.inspect.stack`` with a function returning ``stack``."""
    saved = _this_path_mod.inspect.stack
    _this_path_mod.inspect.stack = lambda: stack  # type: ignore[assignment]
    try:
        yield
    finally:
        _this_path_mod.inspect.stack = saved  # type: ignore[assignment]


@contextmanager
def _swap_module_dunder_file(new_file: str) -> Iterator[None]:
    """Replace ``_this_path.__file__`` with ``new_file``."""
    saved = _this_path_mod.__file__
    _this_path_mod.__file__ = new_file
    try:
        yield
    finally:
        _this_path_mod.__file__ = saved


def _frame(filename: str) -> SimpleNamespace:
    return SimpleNamespace(filename=filename)


# ---------------------------------------------------------------------------
# this_path() returns module ``__file__`` regardless of caller
# ---------------------------------------------------------------------------


def test_this_path_returns_dunder_file_for_normal_python_caller():
    # Arrange
    stack = [None, _frame("/home/user/project/my_script.py")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/home/user/project/scitex/path/_this_path.py"),
    ):
        result = this_path()
    # Assert
    assert result == "/home/user/project/scitex/path/_this_path.py"


def test_this_path_returns_dunder_file_for_ipython_caller_filename():
    # Arrange
    stack = [None, _frame("<ipython console>")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/some/path/with/ipython/in/it.py"),
    ):
        result = this_path()
    # Assert
    assert result == "/some/path/with/ipython/in/it.py"


def test_this_path_ignores_custom_ipython_fake_path_kwarg():
    # Arrange
    stack = [None, _frame("<ipython console>")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/path/with/ipython/kernel.py"),
    ):
        result = this_path(ipython_fake_path="/my/custom/path.py")
    # Assert
    assert result == "/path/with/ipython/kernel.py"


def test_this_path_returns_dunder_file_regardless_of_frame_depth():
    # Arrange
    stack = [
        _frame("/path/to/this_function.py"),
        _frame("/path/to/calling_function.py"),
        _frame("/path/to/caller_of_caller.py"),
    ]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/scitex/path/_this_path.py"),
    ):
        result = this_path()
    # Assert
    assert result == "/scitex/path/_this_path.py"


# ---------------------------------------------------------------------------
# Various paths — parametrised, one fact per case
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "test_path",
    [
        "/absolute/path/to/file.py",
        "relative/path/file.py",
        "../parent/file.py",
        "C:\\Windows\\path\\file.py",
        "/path with spaces/file.py",
        "/path/with-special_chars@123/file.py",
    ],
)
def test_this_path_returns_dunder_file_for_each_input_pattern(test_path: str):
    # Arrange
    stack = [None, _frame(test_path)]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file(test_path):
        result = this_path()
    # Assert
    assert result == test_path


# ---------------------------------------------------------------------------
# ipython literal not present in module path
# ---------------------------------------------------------------------------


def test_this_path_returns_dunder_file_when_ipython_token_absent():
    # Arrange
    stack = [None, _frame("/normal/python/script.py")]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/normal/module/path.py"):
        result = this_path()
    # Assert
    assert result == "/normal/module/path.py"


def test_this_path_returned_value_does_not_contain_ipython_when_path_lacks_it():
    # Arrange
    stack = [None, _frame("/normal/python/script.py")]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/normal/module/path.py"):
        result = this_path()
    # Assert
    assert "ipython" not in result


# ---------------------------------------------------------------------------
# Edge cases — empty / None frame filename
# ---------------------------------------------------------------------------


def test_this_path_returns_dunder_file_when_frame_filename_is_empty():
    # Arrange
    stack = [None, _frame("")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/scitex/path/_this_path.py"),
    ):
        result = this_path()
    # Assert
    assert result == "/scitex/path/_this_path.py"


def test_this_path_returns_dunder_file_when_frame_filename_is_none():
    # Arrange
    stack = [None, _frame(None)]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/scitex/path/_this_path.py"),
    ):
        result = this_path()
    # Assert
    assert result == "/scitex/path/_this_path.py"


# ---------------------------------------------------------------------------
# Alias
# ---------------------------------------------------------------------------


def test_get_this_path_is_same_object_as_this_path():
    # Arrange
    # (no setup needed)
    # Act
    same = get_this_path is this_path
    # Assert
    assert same is True


# ---------------------------------------------------------------------------
# Documents the legacy bug: caller filename is NOT returned
# ---------------------------------------------------------------------------


def test_this_path_returns_module_file_not_caller_filename_legacy_quirk():
    # Arrange
    stack = [None, _frame("/caller/file.py")]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/module/file.py"):
        result = this_path()
    # Assert
    assert result == "/module/file.py"


def test_this_path_legacy_ignores_ipython_fake_path_when_module_path_has_ipython():
    # Arrange
    stack = [None, _frame("<ipython-input-1>")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/has/ipython/in/path.py"),
    ):
        result = this_path(ipython_fake_path="/custom/fallback.py")
    # Assert
    assert result == "/has/ipython/in/path.py"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

# EOF
