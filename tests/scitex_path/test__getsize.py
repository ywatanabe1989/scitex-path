#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 19:54:02 (ywatanabe)"
# File: ./tests/scitex_path/test__getsize.py

"""Tests for ``scitex_path.getsize``.

PA-306: no ``unittest.mock``, no ``monkeypatch``. Collaborators are
swapped at the module namespace via real save/restore context managers.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, has the
three AAA marker comments, and has a descriptive multi-token name.
"""

import math
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

import scitex_path._getsize as _getsize_mod
from scitex_path import getsize

# ---------------------------------------------------------------------------
# Collaborator swaps (test seams — no mocks, no monkeypatch)
# ---------------------------------------------------------------------------


@contextmanager
def _swap_os_path_exists(fn: Callable[[str], bool]) -> Iterator[None]:
    """Replace ``_getsize.os.path.exists`` with ``fn`` for the test duration."""
    saved = _getsize_mod.os.path.exists
    _getsize_mod.os.path.exists = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        _getsize_mod.os.path.exists = saved  # type: ignore[assignment]


@contextmanager
def _swap_os_path_getsize(fn: Callable[[str], int]) -> Iterator[None]:
    """Replace ``_getsize.os.path.getsize`` with ``fn`` for the test duration."""
    saved = _getsize_mod.os.path.getsize
    _getsize_mod.os.path.getsize = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        _getsize_mod.os.path.getsize = saved  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Real-file behaviour
# ---------------------------------------------------------------------------


def test_getsize_returns_byte_length_of_text_content():
    # Arrange
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        content = "Hello, World!"
        f.write(content)
        temp_path = f.name
    try:
        # Act
        size = getsize(temp_path)
        # Assert
        assert size == len(content.encode())
    finally:
        os.unlink(temp_path)


def test_getsize_returns_integer_for_existing_file():
    # Arrange
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("hello")
        temp_path = f.name
    try:
        # Act
        size = getsize(temp_path)
        # Assert
        assert isinstance(size, int)
    finally:
        os.unlink(temp_path)


def test_getsize_returns_zero_for_empty_file():
    # Arrange
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
    try:
        # Act
        size = getsize(temp_path)
        # Assert
        assert size == 0
    finally:
        os.unlink(temp_path)


def test_getsize_returns_exact_byte_count_for_one_megabyte_file():
    # Arrange
    one_mb = 1024 * 1024
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
        f.write(b"x" * one_mb)
        temp_path = f.name
    try:
        # Act
        size = getsize(temp_path)
        # Assert
        assert size == one_mb
    finally:
        os.unlink(temp_path)


# ---------------------------------------------------------------------------
# Non-existent path
# ---------------------------------------------------------------------------


def test_getsize_returns_nan_for_nonexistent_file_path():
    # Arrange
    nonexistent_path = "/path/that/does/not/exist/file.txt"
    # Act
    size = getsize(nonexistent_path)
    # Assert
    assert math.isnan(size)


def test_getsize_returns_nan_for_empty_string_path():
    # Arrange
    empty = ""
    # Act
    size = getsize(empty)
    # Assert
    assert math.isnan(size)


# ---------------------------------------------------------------------------
# Directory
# ---------------------------------------------------------------------------


def test_getsize_directory_returns_integer_value():
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        # Act
        size = getsize(temp_dir)
        # Assert
        assert isinstance(size, int)


def test_getsize_directory_returns_nonnegative_value():
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        # Act
        size = getsize(temp_dir)
        # Assert
        assert size >= 0


# ---------------------------------------------------------------------------
# Symlinks
# ---------------------------------------------------------------------------


def test_getsize_symlink_returns_integer_size_value():
    # Arrange
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Symlink target content")
        target_path = f.name
    with tempfile.TemporaryDirectory() as temp_dir:
        symlink_path = os.path.join(temp_dir, "symlink")
        try:
            os.symlink(target_path, symlink_path)
            # Act
            size = getsize(symlink_path)
            # Assert
            assert isinstance(size, int)
        finally:
            os.unlink(target_path)


def test_getsize_symlink_returns_positive_size_value():
    # Arrange
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Symlink target content")
        target_path = f.name
    with tempfile.TemporaryDirectory() as temp_dir:
        symlink_path = os.path.join(temp_dir, "symlink")
        try:
            os.symlink(target_path, symlink_path)
            # Act
            size = getsize(symlink_path)
            # Assert
            assert size > 0
        finally:
            os.unlink(target_path)


# ---------------------------------------------------------------------------
# pathlib.Path
# ---------------------------------------------------------------------------


def test_getsize_accepts_pathlib_path_object():
    # Arrange
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("Pathlib test")
        temp_path = Path(f.name)
    try:
        # Act
        size = getsize(temp_path)
        # Assert
        assert size == len("Pathlib test".encode())
    finally:
        os.unlink(str(temp_path))


# ---------------------------------------------------------------------------
# Binary file
# ---------------------------------------------------------------------------


def test_getsize_binary_file_returns_exact_byte_count():
    # Arrange
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
        binary_data = bytes(range(256))
        f.write(binary_data)
        temp_path = f.name
    try:
        # Act
        size = getsize(temp_path)
        # Assert
        assert size == 256
    finally:
        os.unlink(temp_path)


# ---------------------------------------------------------------------------
# Unicode-named file
# ---------------------------------------------------------------------------


def test_getsize_unicode_filename_returns_utf8_byte_count():
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        unicode_path = os.path.join(temp_dir, "文件名.txt")
        content = "Unicode filename test"
        with open(unicode_path, "w", encoding="utf-8") as f:
            f.write(content)
        # Act
        size = getsize(unicode_path)
        # Assert
        assert size == len(content.encode("utf-8"))


# ---------------------------------------------------------------------------
# Permission errors via collaborator swap (no mocks)
# ---------------------------------------------------------------------------


def test_getsize_propagates_permission_error_from_underlying_getsize():
    # Arrange
    def always_true(_path: str) -> bool:
        return True

    def raise_permission(_path: str) -> int:
        raise PermissionError("Access denied")

    # Act
    ctx_exists = _swap_os_path_exists(always_true)
    ctx_getsize = _swap_os_path_getsize(raise_permission)
    # Assert
    with ctx_exists, ctx_getsize, pytest.raises(PermissionError):
        getsize("/restricted/file")


# ---------------------------------------------------------------------------
# Special files
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not os.path.exists("/dev/null"), reason="/dev/null not available on this platform"
)
def test_getsize_dev_null_returns_zero_byte_size():
    # Arrange
    dev_null = "/dev/null"
    # Act
    size = getsize(dev_null)
    # Assert
    assert size == 0


# ---------------------------------------------------------------------------
# Relative path
# ---------------------------------------------------------------------------


def test_getsize_accepts_relative_path_in_current_directory():
    # Arrange
    current_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            content = "Relative path test"
            with open("relative_test.txt", "w") as f:
                f.write(content)
            # Act
            size = getsize("relative_test.txt")
            # Assert
            assert size == len(content.encode())
        finally:
            os.chdir(current_dir)


# ---------------------------------------------------------------------------
# Spaces in path
# ---------------------------------------------------------------------------


def test_getsize_accepts_path_with_spaces_in_filename():
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        path_with_spaces = os.path.join(temp_dir, "file with spaces.txt")
        content = "Spaces in filename"
        with open(path_with_spaces, "w") as f:
            f.write(content)
        # Act
        size = getsize(path_with_spaces)
        # Assert
        assert size == len(content.encode())


# ---------------------------------------------------------------------------
# None path
# ---------------------------------------------------------------------------


def test_getsize_raises_type_error_when_path_is_none():
    # Arrange
    path = None
    # Act
    ctx = pytest.raises(TypeError)
    # Assert
    with ctx:
        getsize(path)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
