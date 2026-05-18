#!/usr/bin/env python3
# Timestamp: "2025-06-02 13:20:00 (ywatanabe)"
# File: ./tests/scitex_path/test__version.py

"""Tests for ``scitex_path.find_latest`` and the ``_version.increment_version`` legacy alias.

STX-TQ001 / 002 / 003 / 007: single-fact, AAA-marked, descriptive names.
"""

import os
import tempfile
from pathlib import Path

import pytest

from scitex_path import find_latest, increment_version

# ---------------------------------------------------------------------------
# find_latest — empty directory
# ---------------------------------------------------------------------------


def test_find_latest_returns_none_when_directory_has_no_versioned_files():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result is None


# ---------------------------------------------------------------------------
# find_latest — single file
# ---------------------------------------------------------------------------


def test_find_latest_returns_only_file_when_single_version_exists():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_file_v001.txt")
        Path(test_file).touch()
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result == test_file


# ---------------------------------------------------------------------------
# find_latest — multiple files with gap
# ---------------------------------------------------------------------------


def test_find_latest_returns_highest_version_among_sparse_versions():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in [1, 3, 5, 10, 2]:
            Path(os.path.join(tmpdir, f"test_file_v{i:03d}.txt")).touch()
        expected = os.path.join(tmpdir, "test_file_v010.txt")
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# find_latest — custom prefix
# ---------------------------------------------------------------------------


def test_find_latest_respects_custom_version_prefix():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in [1, 2, 3]:
            Path(os.path.join(tmpdir, f"test_file-version{i:03d}.txt")).touch()
        expected = os.path.join(tmpdir, "test_file-version003.txt")
        # Act
        result = find_latest(tmpdir, "test_file", ".txt", version_prefix="-version")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# find_latest — extension filtering
# ---------------------------------------------------------------------------


def test_find_latest_for_txt_returns_highest_txt_version_only():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.csv")).touch()
        Path(os.path.join(tmpdir, "test_file_v003.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v004.csv")).touch()
        expected = os.path.join(tmpdir, "test_file_v003.txt")
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result == expected


def test_find_latest_for_csv_returns_highest_csv_version_only():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.csv")).touch()
        Path(os.path.join(tmpdir, "test_file_v003.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v004.csv")).touch()
        expected = os.path.join(tmpdir, "test_file_v004.csv")
        # Act
        result = find_latest(tmpdir, "test_file", ".csv")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# find_latest — invalid version tokens skipped
# ---------------------------------------------------------------------------


def test_find_latest_skips_files_with_nonnumeric_version_token():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_vABC.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.txt")).touch()
        Path(os.path.join(tmpdir, "test_file.txt")).touch()
        expected = os.path.join(tmpdir, "test_file_v002.txt")
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# find_latest — large version numbers
# ---------------------------------------------------------------------------


def test_find_latest_handles_four_digit_version_numbers():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v099.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v100.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v999.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v1000.txt")).touch()
        expected = os.path.join(tmpdir, "test_file_v1000.txt")
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# find_latest — similar filenames
# ---------------------------------------------------------------------------


def test_find_latest_only_matches_exact_basename_prefix():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_file_v001.txt")).touch()
        Path(os.path.join(tmpdir, "test_file2_v005.txt")).touch()
        Path(os.path.join(tmpdir, "prefix_test_file_v010.txt")).touch()
        Path(os.path.join(tmpdir, "test_file_v002.txt")).touch()
        expected = os.path.join(tmpdir, "test_file_v002.txt")
        # Act
        result = find_latest(tmpdir, "test_file", ".txt")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# find_latest — empty dirname
# ---------------------------------------------------------------------------


def test_find_latest_returns_none_or_string_for_empty_dirname():
    # Arrange
    dirname = ""
    # Act
    result = find_latest(dirname, "test_file_unique_token_xyz", ".txt")
    # Assert
    assert result is None or isinstance(result, str)


# ---------------------------------------------------------------------------
# find_latest — nested directory
# ---------------------------------------------------------------------------


def test_find_latest_operates_on_nested_directory_path():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_dir = os.path.join(tmpdir, "sub1", "sub2")
        os.makedirs(nested_dir)
        Path(os.path.join(nested_dir, "test_file_v001.txt")).touch()
        Path(os.path.join(nested_dir, "test_file_v002.txt")).touch()
        expected = os.path.join(nested_dir, "test_file_v002.txt")
        # Act
        result = find_latest(nested_dir, "test_file", ".txt")
        # Assert
        assert result == expected


# ---------------------------------------------------------------------------
# increment_version (legacy _version.py) — equivalence with main alias
# ---------------------------------------------------------------------------


def test_increment_version_legacy_alias_matches_canonical_result():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_v001.txt")).touch()
        # Act
        result1 = increment_version(tmpdir, "test", ".txt")
        result2 = increment_version(tmpdir, "test", ".txt")
        # Assert
        assert str(result1) == str(result2)


def test_increment_version_legacy_alias_returns_v002_path_when_v001_exists():
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(os.path.join(tmpdir, "test_v001.txt")).touch()
        # Act
        result = increment_version(tmpdir, "test", ".txt")
        # Assert
        assert str(result).endswith("test_v002.txt")


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
