#!/usr/bin/env python3
# Timestamp: "2025-06-02 12:50:00 (ywatanabe)"
# File: ./tests/scitex_path/test__increment_version.py

"""Tests for ``scitex_path.increment_version``.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, carries
AAA markers, has a descriptive name.
"""

import os
import tempfile
from pathlib import Path

import pytest

from scitex_path import increment_version

# ---------------------------------------------------------------------------
# No prior versioned files
# ---------------------------------------------------------------------------


def test_increment_version_starts_at_001_when_no_files_exist():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v001.txt")


# ---------------------------------------------------------------------------
# Single existing file
# ---------------------------------------------------------------------------


def test_increment_version_increments_to_002_when_v001_exists():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v002.txt")


# ---------------------------------------------------------------------------
# Multiple files with gaps in version sequence
# ---------------------------------------------------------------------------


def test_increment_version_returns_max_plus_one_with_sparse_versions():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in [1, 2, 3, 5, 7]:
            Path(os.path.join(tmpdir, f"test_file_v{i:03d}.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v008.txt")


# ---------------------------------------------------------------------------
# Custom version prefix
# ---------------------------------------------------------------------------


def test_increment_version_respects_custom_version_prefix():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file-ver001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file-ver002.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt", version_prefix="-ver")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file-ver003.txt")


# ---------------------------------------------------------------------------
# Extension filtering
# ---------------------------------------------------------------------------


def test_increment_version_for_txt_ignores_files_with_csv_extension():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v001.csv")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.csv")).touch()
        # Act
        result_txt = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result_txt) == os.path.join(tmpdir, "test_file_v002.txt")


def test_increment_version_for_csv_ignores_files_with_txt_extension():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v001.csv")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.csv")).touch()
        # Act
        result_csv = increment_version(tmpdir, "test_file", ".csv")
        # Assert
        assert str(result_csv) == os.path.join(tmpdir, "test_file_v003.csv")


# ---------------------------------------------------------------------------
# Special characters in filename
# ---------------------------------------------------------------------------


def test_increment_version_handles_dots_in_base_filename():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = "test.file.name"
        Path(os.path.join(tmpdir, f"{fname}_v001.txt")).touch()
        # Act
        result = increment_version(tmpdir, fname, ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, f"{fname}_v002.txt")


def test_increment_version_handles_parentheses_in_base_filename():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = "test_file(1)"
        Path(os.path.join(tmpdir, f"{fname}_v001.txt")).touch()
        # Act
        result = increment_version(tmpdir, fname, ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, f"{fname}_v002.txt")


# ---------------------------------------------------------------------------
# Large version numbers
# ---------------------------------------------------------------------------


def test_increment_version_rolls_over_999_to_1000():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v999.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v1000.txt")


# ---------------------------------------------------------------------------
# Mix of valid and invalid version filenames
# ---------------------------------------------------------------------------


def test_increment_version_skips_files_with_nonnumeric_version_token():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_vABC.txt")).touch()
        Path(os.path.join(tmpdir, "test_file.txt")).touch()
        Path(os.path.join(tmpdir, "other_file_v001.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v003.txt")


# ---------------------------------------------------------------------------
# Empty directory string
# ---------------------------------------------------------------------------


def test_increment_version_returns_relative_filename_when_dirname_empty():
    # Arrange
    dirname = ""
    # Act
    result = increment_version(dirname, "test_file", ".txt")
    # Assert
    assert str(result) == "test_file_v001.txt"


# ---------------------------------------------------------------------------
# Nested directory
# ---------------------------------------------------------------------------


def test_increment_version_operates_on_nested_directory_path():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_dir = os.path.join(tmpdir, "sub1", "sub2")
        os.makedirs(nested_dir)
        Path(os.path.join(nested_dir, "test_file_v001.txt")).touch()
        # Act
        result = increment_version(nested_dir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(nested_dir, "test_file_v002.txt")


# ---------------------------------------------------------------------------
# Compound extension
# ---------------------------------------------------------------------------


def test_increment_version_handles_compound_tar_gz_extension():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.tar.gz")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".tar.gz")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v002.tar.gz")


# ---------------------------------------------------------------------------
# Similar filenames
# ---------------------------------------------------------------------------


def test_increment_version_only_matches_exact_basename_prefix():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file2_v005.txt")).touch()
        Path(os.path.join(tmpdir, "prefix_test_file_v010.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v002.txt")


# ---------------------------------------------------------------------------
# Zero-padded versions
# ---------------------------------------------------------------------------


def test_increment_version_uses_three_digit_padding_when_input_padding_smaller():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v01.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test_file", ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, "test_file_v003.txt")


# ---------------------------------------------------------------------------
# Dots in basename (separate from compound extension)
# ---------------------------------------------------------------------------


def test_increment_version_dots_in_basename_yields_correct_next_path():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = "test.file.name"
        Path(os.path.join(tmpdir, f"{fname}_v001.txt")).touch()
        # Act
        result = increment_version(tmpdir, fname, ".txt")
        # Assert
        assert str(result) == os.path.join(tmpdir, f"{fname}_v002.txt")


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
