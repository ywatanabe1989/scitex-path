#!/usr/bin/env python3
# Time-stamp: "2024-11-08 05:54:00 (ywatanabe)"
# File: ./tests/scitex_path/test__clean.py

"""Tests for path cleaning functionality.

STX-TQ001: every test asserts something.
STX-TQ002: every test carries Arrange / Act / Assert markers.
STX-TQ003: every test name has >=3 word-tokens.
STX-TQ007: every test asserts exactly one fact.
"""

import pytest

from scitex_path import clean

# ---------------------------------------------------------------------------
# Single-dot-slash collapsing via os.path.normpath
# ---------------------------------------------------------------------------


def test_clean_collapses_interior_dot_slash_sequences():
    # Arrange
    path_in = "/home/./user/./file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/file.txt"


def test_clean_strips_leading_dot_slash():
    # Arrange
    path_in = "./file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "file.txt"


def test_clean_collapses_repeated_dot_slash_at_root():
    # Arrange
    path_in = "/././file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/file.txt"


# ---------------------------------------------------------------------------
# Double-slash collapsing
# ---------------------------------------------------------------------------


def test_clean_collapses_interior_double_slashes():
    # Arrange
    path_in = "/home//user//file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/file.txt"


def test_clean_collapses_leading_double_slash():
    # Arrange
    path_in = "//network/share"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/network/share"


def test_clean_protocol_double_slash_collapses_to_single():
    # Arrange
    path_in = "file://path"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "file:/path"


# ---------------------------------------------------------------------------
# Space-to-underscore replacement
# ---------------------------------------------------------------------------


def test_clean_replaces_space_in_filename_with_underscore():
    # Arrange
    path_in = "/home/user/my file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/my_file.txt"


def test_clean_replaces_spaces_in_relative_filename():
    # Arrange
    path_in = "file with spaces.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "file_with_spaces.txt"


def test_clean_replaces_each_space_with_underscore():
    # Arrange
    path_in = "multiple   spaces"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "multiple___spaces"


# ---------------------------------------------------------------------------
# Combined cleaning
# ---------------------------------------------------------------------------


def test_clean_handles_dot_slash_double_slash_and_spaces_together():
    # Arrange
    path_in = "/home/./user//my file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/my_file.txt"


def test_clean_drops_leading_dot_in_combined_path():
    # Arrange
    path_in = "./path//to/./some file"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "path/to/some_file"


def test_clean_combined_with_network_path_collapses():
    # Arrange
    path_in = "//server/./share//my folder/./file"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/server/share/my_folder/file"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_clean_returns_empty_string_on_empty_input():
    # Arrange
    path_in = ""
    # Act
    result = clean(path_in)
    # Assert
    assert result == ""


def test_clean_leaves_absolute_path_unchanged_when_clean():
    # Arrange
    path_in = "/home/user/file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/file.txt"


def test_clean_leaves_relative_path_unchanged_when_clean():
    # Arrange
    path_in = "relative/path/file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "relative/path/file.txt"


# ---------------------------------------------------------------------------
# Windows-style input handled on POSIX
# ---------------------------------------------------------------------------


def test_clean_windows_drive_path_collapses_double_slashes_and_replaces_spaces():
    # Arrange
    path_in = "C://Users//John Doe//Documents"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "C:/Users/John_Doe/Documents"


def test_clean_windows_drive_path_collapses_dot_slash():
    # Arrange
    path_in = "D:/./Projects//my project"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "D:/Projects/my_project"


# ---------------------------------------------------------------------------
# Special cases
# ---------------------------------------------------------------------------


def test_clean_collapses_pure_dot_slash_chain_to_root():
    # Arrange
    path_in = "/.//./"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/"


def test_clean_replaces_spaces_before_collapsing_slashes():
    # Arrange
    path_in = "// // //"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/_/_/"


def test_clean_preserves_trailing_double_slash_as_trailing_slash():
    # Arrange
    path_in = "/home/user//"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/"


def test_clean_preserves_trailing_slash_after_dot():
    # Arrange
    path_in = "/home/user/./"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/"


# ---------------------------------------------------------------------------
# Unicode handling
# ---------------------------------------------------------------------------


def test_clean_replaces_space_in_unicode_filename():
    # Arrange
    path_in = "/home/user/ñoño file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/home/user/ñoño_file.txt"


def test_clean_collapses_dot_slash_in_cyrillic_path():
    # Arrange
    path_in = "/путь//к/./файлу"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/путь/к/файлу"


def test_clean_handles_cjk_unicode_path_with_spaces():
    # Arrange
    path_in = "/文件夹/./子 文件夹//文件.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/文件夹/子_文件夹/文件.txt"


# ---------------------------------------------------------------------------
# Order-of-operations
# ---------------------------------------------------------------------------


def test_clean_replaces_space_then_normalises_then_collapses_slashes():
    # Arrange
    path_in = "/ ./ /"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/_./_/"


def test_clean_replaces_double_spaces_with_double_underscores():
    # Arrange
    path_in = "//  //"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/__/"


# ---------------------------------------------------------------------------
# Idempotence
# ---------------------------------------------------------------------------


def test_clean_is_idempotent_when_applied_twice():
    # Arrange
    path_in = "/home/./user//my file.txt"
    # Act
    once = clean(path_in)
    twice = clean(once)
    # Assert
    assert once == twice


def test_clean_idempotent_result_equals_expected_normalised_path():
    # Arrange
    path_in = "/home/./user//my file.txt"
    # Act
    once = clean(path_in)
    # Assert
    assert once == "/home/user/my_file.txt"


# ---------------------------------------------------------------------------
# Important sequence preservation
# ---------------------------------------------------------------------------


def test_clean_preserves_parent_directory_reference():
    # Arrange
    path_in = "../file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "../file.txt"


def test_clean_strips_leading_dot_slash_from_script_path():
    # Arrange
    path_in = "./script.py"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "script.py"


def test_clean_preserves_root_slash_unchanged():
    # Arrange
    path_in = "/"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/"


def test_clean_preserves_current_directory_dot():
    # Arrange
    path_in = "."
    # Act
    result = clean(path_in)
    # Assert
    assert result == "."


# ---------------------------------------------------------------------------
# Network / URL-shaped inputs
# ---------------------------------------------------------------------------


def test_clean_leaves_unc_backslash_path_unchanged():
    # Arrange
    path_in = "\\\\server\\share\\file.txt"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "\\\\server\\share\\file.txt"


def test_clean_collapses_unix_style_network_path_with_spaces():
    # Arrange
    path_in = "//server/./share//my file"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "/server/share/my_file"


def test_clean_url_like_input_collapses_double_slash_to_single():
    # Arrange
    path_in = "http://example.com/./path"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "http:/example.com/path"


def test_clean_file_url_collapses_triple_slash():
    # Arrange
    path_in = "file:///home//user"
    # Act
    result = clean(path_in)
    # Assert
    assert result == "file:/home/user"


# ---------------------------------------------------------------------------
# Performance / robustness — split into single-fact assertions
# ---------------------------------------------------------------------------


def test_clean_long_path_removes_dot_slash_segments():
    # Arrange
    long_path = "/home" + "/./user" * 100 + "//file.txt"
    # Act
    result = clean(long_path)
    # Assert
    assert "/./" not in result


def test_clean_long_path_removes_double_slash_segments():
    # Arrange
    long_path = "/home" + "/./user" * 100 + "//file.txt"
    # Act
    result = clean(long_path)
    # Assert
    assert "//" not in result


def test_clean_long_path_preserves_leading_segment():
    # Arrange
    long_path = "/home" + "/./user" * 100 + "//file.txt"
    # Act
    result = clean(long_path)
    # Assert
    assert result.startswith("/home")


def test_clean_long_path_preserves_trailing_filename():
    # Arrange
    long_path = "/home" + "/./user" * 100 + "//file.txt"
    # Act
    result = clean(long_path)
    # Assert
    assert result.endswith("file.txt")


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])

# EOF
