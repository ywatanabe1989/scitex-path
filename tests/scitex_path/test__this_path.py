#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:15:00 (ywatanabe)"
# File: ./tests/scitex_path/test__this_path.py

"""Tests for ``scitex_path.this_path`` (the legacy ``_this_path`` module).

The legacy contract: ``this_path()`` captures the caller via
``inspect.stack()[1]`` but ultimately returns ``__file__`` of the
``_this_path`` module. Tests below codify that quirk.

PA-306: no ``unittest.mock``, no ``monkeypatch``. Collaborators are
swapped at the module namespace via real save/restore context managers.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, has
AAA markers, and a descriptive multi-token name.
"""

from __future__ import annotations

import os
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
# Legacy behaviour — returns ``__file__`` regardless of caller
# ---------------------------------------------------------------------------


def test_this_path_returns_module_dunder_file_in_normal_environment():
    # Arrange
    stack = [None, _frame("/path/to/calling/script.py")]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/path/to/module.py"):
        result = this_path()
    # Assert
    assert result == "/path/to/module.py"


def test_this_path_returns_module_dunder_file_for_ipython_caller():
    # Arrange
    stack = [None, _frame("<ipython-input-1>")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/path/to/ipython/module.py"),
    ):
        result = this_path()
    # Assert
    assert result == "/path/to/ipython/module.py"


def test_this_path_ignores_custom_ipython_fake_path_argument():
    # Arrange
    stack = [None, _frame("<ipython-input-1>")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/path/to/ipython/module.py"),
    ):
        result = this_path(ipython_fake_path="/custom/fake.py")
    # Assert
    assert result == "/path/to/ipython/module.py"


def test_this_path_returns_module_file_when_called_through_wrapper():
    # Arrange
    stack = [
        _frame("this_path.py"),
        _frame("wrapper.py"),
        _frame("test.py"),
    ]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/module/path.py"):
        result = this_path()
    # Assert
    assert result == "/module/path.py"


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------


def test_get_this_path_is_alias_for_this_path():
    # Arrange
    # (no setup needed)
    # Act
    same = get_this_path is this_path
    # Assert
    assert same is True


# ---------------------------------------------------------------------------
# Argument-less and return-type smoke tests
# ---------------------------------------------------------------------------


def test_this_path_returns_non_none_when_called_without_arguments():
    # Arrange
    stack = [None, _frame("/test.py")]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/module.py"):
        result = this_path()
    # Assert
    assert result is not None


def test_this_path_returns_string_value():
    # Arrange
    stack = [None, _frame("/test.py")]
    # Act
    with _swap_inspect_stack(stack), _swap_module_dunder_file("/module.py"):
        result = this_path()
    # Assert
    assert isinstance(result, str)


def test_this_path_returns_absolute_path_when_module_file_is_absolute():
    # Arrange
    stack = [None, _frame("/test.py")]
    # Act
    with (
        _swap_inspect_stack(stack),
        _swap_module_dunder_file("/absolute/path/to/module.py"),
    ):
        result = this_path()
    # Assert
    assert os.path.isabs(result)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
