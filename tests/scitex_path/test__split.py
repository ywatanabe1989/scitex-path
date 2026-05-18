#!/usr/bin/env python3
# Timestamp: "2025-06-02 13:10:00 (ywatanabe)"
# File: ./tests/scitex_path/test__split.py

"""Tests for ``scitex_path.split``.

STX-TQ001: every test asserts something.
STX-TQ002: every test carries Arrange / Act / Assert markers.
STX-TQ003: every test name has >=3 word-tokens.
STX-TQ007: every test asserts exactly one fact.
"""

import os

import pytest

from scitex_path import split

# ---------------------------------------------------------------------------
# Basic absolute file path
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_absolute_file_path():
    # Arrange
    path_in = "/path/to/file.txt"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/"


def test_split_returns_fname_for_absolute_file_path():
    # Arrange
    path_in = "/path/to/file.txt"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "file"


def test_split_returns_ext_for_absolute_file_path():
    # Arrange
    path_in = "/path/to/file.txt"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".txt"


# ---------------------------------------------------------------------------
# Relative path
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_relative_path():
    # Arrange
    path_in = "../data/01/day1/split_octave/2kHz_mat/tt8-2.mat"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "../data/01/day1/split_octave/2kHz_mat/"


def test_split_returns_fname_for_relative_path():
    # Arrange
    path_in = "../data/01/day1/split_octave/2kHz_mat/tt8-2.mat"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "tt8-2"


def test_split_returns_ext_for_relative_path():
    # Arrange
    path_in = "../data/01/day1/split_octave/2kHz_mat/tt8-2.mat"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".mat"


# ---------------------------------------------------------------------------
# No extension
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_file_without_extension():
    # Arrange
    path_in = "/path/to/README"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/"


def test_split_returns_fname_for_file_without_extension():
    # Arrange
    path_in = "/path/to/README"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "README"


def test_split_returns_empty_ext_for_file_without_extension():
    # Arrange
    path_in = "/path/to/README"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ""


# ---------------------------------------------------------------------------
# Multiple-dot filename
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_multi_dot_filename():
    # Arrange
    path_in = "/path/to/file.backup.tar.gz"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/"


def test_split_returns_stem_for_multi_dot_filename():
    # Arrange
    path_in = "/path/to/file.backup.tar.gz"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "file.backup.tar"


def test_split_returns_last_ext_for_multi_dot_filename():
    # Arrange
    path_in = "/path/to/file.backup.tar.gz"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".gz"


# ---------------------------------------------------------------------------
# Hidden files
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_hidden_file():
    # Arrange
    path_in = "/home/user/.bashrc"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/home/user/"


def test_split_returns_fname_for_hidden_file_keeps_leading_dot():
    # Arrange
    path_in = "/home/user/.bashrc"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == ".bashrc"


def test_split_returns_empty_ext_for_hidden_file_without_extension():
    # Arrange
    path_in = "/home/user/.bashrc"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ""


def test_split_returns_dirname_for_hidden_file_with_extension():
    # Arrange
    path_in = "/home/user/.config.yaml"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/home/user/"


def test_split_returns_fname_for_hidden_file_with_extension():
    # Arrange
    path_in = "/home/user/.config.yaml"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == ".config"


def test_split_returns_ext_for_hidden_file_with_extension():
    # Arrange
    path_in = "/home/user/.config.yaml"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".yaml"


# ---------------------------------------------------------------------------
# Root directory case (legacy quirk: dirname appears as "//")
# ---------------------------------------------------------------------------


def test_split_returns_double_slash_dirname_for_file_at_root():
    # Arrange
    path_in = "/file.txt"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "//"


def test_split_returns_fname_for_file_at_root():
    # Arrange
    path_in = "/file.txt"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "file"


def test_split_returns_ext_for_file_at_root():
    # Arrange
    path_in = "/file.txt"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".txt"


# ---------------------------------------------------------------------------
# File in current directory
# ---------------------------------------------------------------------------


def test_split_returns_slash_dirname_for_bare_filename():
    # Arrange
    path_in = "file.txt"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/"


def test_split_returns_fname_for_bare_filename():
    # Arrange
    path_in = "file.txt"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "file"


def test_split_returns_ext_for_bare_filename():
    # Arrange
    path_in = "file.txt"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".txt"


# ---------------------------------------------------------------------------
# Trailing slash (directory-like)
# ---------------------------------------------------------------------------


def test_split_returns_full_path_as_dirname_when_input_ends_with_slash():
    # Arrange
    path_in = "/path/to/directory/"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/directory/"


def test_split_returns_empty_fname_for_directory_input():
    # Arrange
    path_in = "/path/to/directory/"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == ""


def test_split_returns_empty_ext_for_directory_input():
    # Arrange
    path_in = "/path/to/directory/"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ""


# ---------------------------------------------------------------------------
# Empty path
# ---------------------------------------------------------------------------


def test_split_returns_slash_dirname_for_empty_path():
    # Arrange
    path_in = ""
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/"


def test_split_returns_empty_fname_for_empty_path():
    # Arrange
    path_in = ""
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == ""


def test_split_returns_empty_ext_for_empty_path():
    # Arrange
    path_in = ""
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ""


# ---------------------------------------------------------------------------
# Special characters
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_special_chars_filename():
    # Arrange
    path_in = "/path/to/file[with]special(chars).txt"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/"


def test_split_returns_fname_for_special_chars_filename():
    # Arrange
    path_in = "/path/to/file[with]special(chars).txt"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "file[with]special(chars)"


def test_split_returns_ext_for_special_chars_filename():
    # Arrange
    path_in = "/path/to/file[with]special(chars).txt"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".txt"


# ---------------------------------------------------------------------------
# Unicode characters
# ---------------------------------------------------------------------------


def test_split_returns_dirname_for_unicode_filename():
    # Arrange
    path_in = "/path/to/ファイル.txt"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/"


def test_split_returns_fname_for_unicode_filename():
    # Arrange
    path_in = "/path/to/ファイル.txt"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "ファイル"


def test_split_returns_ext_for_unicode_filename():
    # Arrange
    path_in = "/path/to/ファイル.txt"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".txt"


# ---------------------------------------------------------------------------
# Spaces in path
# ---------------------------------------------------------------------------


def test_split_returns_dirname_preserving_spaces_in_dirs():
    # Arrange
    path_in = "/path with spaces/file name.txt"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path with spaces/"


def test_split_returns_fname_preserving_spaces_in_filename():
    # Arrange
    path_in = "/path with spaces/file name.txt"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "file name"


def test_split_returns_ext_when_filename_has_spaces():
    # Arrange
    path_in = "/path with spaces/file name.txt"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".txt"


# ---------------------------------------------------------------------------
# Compound extension behavior
# ---------------------------------------------------------------------------


def test_split_compound_extension_returns_dirname():
    # Arrange
    path_in = "/path/to/archive.tar.gz"
    # Act
    dirname, _, _ = split(path_in)
    # Assert
    assert dirname == "/path/to/"


def test_split_compound_extension_returns_stem_with_inner_extension():
    # Arrange
    path_in = "/path/to/archive.tar.gz"
    # Act
    _, fname, _ = split(path_in)
    # Assert
    assert fname == "archive.tar"


def test_split_compound_extension_returns_only_outermost_extension():
    # Arrange
    path_in = "/path/to/archive.tar.gz"
    # Act
    _, _, ext = split(path_in)
    # Assert
    assert ext == ".gz"


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
