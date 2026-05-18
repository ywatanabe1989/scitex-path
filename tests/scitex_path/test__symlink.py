#!/usr/bin/env python3
# Time-stamp: "2026-01-04 (ywatanabe)"
# File: ./tests/scitex_path/test__symlink.py

"""Tests for scitex_path symlink utilities.

STX-TQ001 / 002 / 003 / 007: each test asserts exactly one fact, has the
three AAA marker comments, and has a descriptive multi-token name.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from scitex_path import (
    create_relative_symlink,
    fix_broken_symlinks,
    is_symlink,
    list_symlinks,
    readlink,
    resolve_symlinks,
    symlink,
    unlink_symlink,
)

# =============================================================================
# symlink()
# =============================================================================


class TestSymlink:
    """Tests for symlink() function."""

    def test_symlink_basic_file_returns_dst_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test content")
            # Act
            result = symlink(src, dst)
            # Assert
            assert result == dst

    def test_symlink_basic_file_creates_symlink_at_dst(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test content")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_symlink_basic_file_resolves_to_source_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test content")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.read_text() == "test content"

    def test_symlink_basic_directory_returns_dst_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source_dir"
            dst = Path(temp_dir) / "link_dir"
            src.mkdir()
            (src / "file.txt").write_text("in dir")
            # Act
            result = symlink(src, dst)
            # Assert
            assert result == dst

    def test_symlink_basic_directory_creates_symlink_at_dst(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source_dir"
            dst = Path(temp_dir) / "link_dir"
            src.mkdir()
            (src / "file.txt").write_text("in dir")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_symlink_basic_directory_exposes_child_file_through_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source_dir"
            dst = Path(temp_dir) / "link_dir"
            src.mkdir()
            (src / "file.txt").write_text("in dir")
            # Act
            symlink(src, dst)
            # Assert
            assert (dst / "file.txt").read_text() == "in dir"

    def test_symlink_raises_file_exists_error_when_overwrite_false(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("source")
            dst.write_text("existing")
            # Act
            ctx = pytest.raises(FileExistsError)
            # Assert
            with ctx:
                symlink(src, dst, overwrite=False)

    def test_symlink_overwrite_true_replaces_old_link_with_new_target_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src1 = Path(temp_dir) / "source1.txt"
            src2 = Path(temp_dir) / "source2.txt"
            dst = Path(temp_dir) / "link.txt"
            src1.write_text("first")
            src2.write_text("second")
            symlink(src1, dst)
            # Act
            symlink(src2, dst, overwrite=True)
            # Assert
            assert dst.read_text() == "second"

    def test_symlink_overwrite_true_replaces_regular_file_with_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "existing.txt"
            src.write_text("source")
            dst.write_text("existing regular file")
            # Act
            symlink(src, dst, overwrite=True)
            # Assert
            assert dst.is_symlink()

    def test_symlink_overwrite_true_replaces_regular_file_with_source_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "existing.txt"
            src.write_text("source")
            dst.write_text("existing regular file")
            # Act
            symlink(src, dst, overwrite=True)
            # Assert
            assert dst.read_text() == "source"

    def test_symlink_overwrite_true_replaces_existing_directory_with_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "existing_dir"
            src.write_text("source")
            dst.mkdir()
            (dst / "file.txt").write_text("in existing dir")
            # Act
            symlink(src, dst, overwrite=True)
            # Assert
            assert dst.is_symlink()

    def test_symlink_relative_true_creates_symlink_object(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            # Act
            symlink(src, dst, relative=True)
            # Assert
            assert dst.is_symlink()

    def test_symlink_relative_true_stores_relative_target_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            # Act
            symlink(src, dst, relative=True)
            target = os.readlink(dst)
            # Assert
            assert not Path(target).is_absolute()

    def test_symlink_relative_with_subdirs_creates_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src_dir = Path(temp_dir) / "a" / "b"
            dst_dir = Path(temp_dir) / "c" / "d"
            src_dir.mkdir(parents=True)
            dst_dir.mkdir(parents=True)
            src = src_dir / "source.txt"
            dst = dst_dir / "link.txt"
            src.write_text("nested")
            # Act
            symlink(src, dst, relative=True)
            # Assert
            assert dst.is_symlink()

    def test_symlink_relative_with_subdirs_resolves_to_source_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src_dir = Path(temp_dir) / "a" / "b"
            dst_dir = Path(temp_dir) / "c" / "d"
            src_dir.mkdir(parents=True)
            dst_dir.mkdir(parents=True)
            src = src_dir / "source.txt"
            dst = dst_dir / "link.txt"
            src.write_text("nested")
            # Act
            symlink(src, dst, relative=True)
            # Assert
            assert dst.read_text() == "nested"

    def test_symlink_creates_missing_parent_directories_for_dst(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "nested" / "path" / "link.txt"
            src.write_text("test")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.parent.exists()

    def test_symlink_after_parent_creation_dst_is_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "nested" / "path" / "link.txt"
            src.write_text("test")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_symlink_to_nonexistent_target_creates_dangling_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "nonexistent.txt"
            dst = Path(temp_dir) / "link.txt"
            # Act
            symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_symlink_to_nonexistent_target_dst_does_not_resolve(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "nonexistent.txt"
            dst = Path(temp_dir) / "link.txt"
            # Act
            symlink(src, dst)
            # Assert
            assert not dst.exists()

    def test_symlink_with_string_paths_returns_path_object_of_dst(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "source.txt")
            dst = os.path.join(temp_dir, "link.txt")
            Path(src).write_text("test")
            # Act
            result = symlink(src, dst)
            # Assert
            assert result == Path(dst)

    def test_symlink_with_string_paths_creates_symlink_at_dst(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "source.txt")
            dst = os.path.join(temp_dir, "link.txt")
            Path(src).write_text("test")
            # Act
            symlink(src, dst)
            # Assert
            assert Path(dst).is_symlink()

    def test_symlink_unicode_filename_creates_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "源文件.txt"
            dst = Path(temp_dir) / "链接.txt"
            src.write_text("unicode test")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_symlink_unicode_filename_resolves_to_source_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "源文件.txt"
            dst = Path(temp_dir) / "链接.txt"
            src.write_text("unicode test")
            # Act
            symlink(src, dst)
            # Assert
            assert dst.read_text() == "unicode test"


# =============================================================================
# is_symlink()
# =============================================================================


class TestIsSymlink:
    """Tests for is_symlink() function."""

    def test_is_symlink_returns_true_for_real_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            result = is_symlink(dst)
            # Assert
            assert result is True

    def test_is_symlink_returns_false_for_regular_file(self):
        # Arrange
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        try:
            # Act
            result = is_symlink(f.name)
            # Assert
            assert result is False
        finally:
            os.unlink(f.name)

    def test_is_symlink_returns_false_for_regular_directory(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Act
            result = is_symlink(temp_dir)
            # Assert
            assert result is False

    def test_is_symlink_returns_false_for_nonexistent_path(self):
        # Arrange
        nonexistent = "/nonexistent/path"
        # Act
        result = is_symlink(nonexistent)
        # Assert
        assert result is False

    def test_is_symlink_returns_true_for_broken_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "nonexistent.txt"
            dst = Path(temp_dir) / "broken_link.txt"
            dst.symlink_to(src)
            # Act
            result = is_symlink(dst)
            # Assert
            assert result is True

    def test_is_symlink_returns_true_when_called_with_string_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "source.txt")
            dst = os.path.join(temp_dir, "link.txt")
            Path(src).write_text("test")
            Path(dst).symlink_to(src)
            # Act
            result = is_symlink(dst)
            # Assert
            assert result is True


# =============================================================================
# readlink()
# =============================================================================


class TestReadlink:
    """Tests for readlink() function."""

    def test_readlink_returns_path_object(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            target = readlink(dst)
            # Assert
            assert isinstance(target, Path)

    def test_readlink_target_resolves_to_source(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            target = readlink(dst)
            # Assert
            assert src.name in str(target) or target.resolve() == src.resolve()

    def test_readlink_raises_os_error_for_regular_file(self):
        # Arrange
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        try:
            # Act
            ctx = pytest.raises(OSError, match="not a symbolic link")
            # Assert
            with ctx:
                readlink(f.name)
        finally:
            os.unlink(f.name)

    def test_readlink_raises_os_error_for_directory(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Act
            ctx = pytest.raises(OSError, match="not a symbolic link")
            # Assert
            with ctx:
                readlink(temp_dir)

    def test_readlink_returns_target_for_broken_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "nonexistent.txt"
            dst = Path(temp_dir) / "broken_link.txt"
            dst.symlink_to(src)
            # Act
            target = readlink(dst)
            # Assert
            assert "nonexistent.txt" in str(target)

    def test_readlink_with_string_path_returns_path_object(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "source.txt")
            dst = os.path.join(temp_dir, "link.txt")
            Path(src).write_text("test")
            Path(dst).symlink_to(src)
            # Act
            target = readlink(dst)
            # Assert
            assert isinstance(target, Path)


# =============================================================================
# resolve_symlinks()
# =============================================================================


class TestResolveSymlinks:
    """Tests for resolve_symlinks() function."""

    def test_resolve_symlinks_single_link_equals_source_resolved(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            resolved = resolve_symlinks(dst)
            # Assert
            assert resolved == src.resolve()

    def test_resolve_symlinks_single_link_returns_absolute_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            resolved = resolve_symlinks(dst)
            # Assert
            assert resolved.is_absolute()

    def test_resolve_symlinks_chain_resolves_to_original_source(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link1 = Path(temp_dir) / "link1.txt"
            link2 = Path(temp_dir) / "link2.txt"
            src.write_text("test")
            link1.symlink_to(src)
            link2.symlink_to(link1)
            # Act
            resolved = resolve_symlinks(link2)
            # Assert
            assert resolved == src.resolve()

    def test_resolve_symlinks_regular_file_returns_its_own_resolved_path(self):
        # Arrange
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        try:
            # Act
            resolved = resolve_symlinks(f.name)
            # Assert
            assert resolved == Path(f.name).resolve()
        finally:
            os.unlink(f.name)

    def test_resolve_symlinks_directory_returns_absolute_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Act
            resolved = resolve_symlinks(temp_dir)
            # Assert
            assert resolved.is_absolute()

    def test_resolve_symlinks_directory_returns_existing_directory(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Act
            resolved = resolve_symlinks(temp_dir)
            # Assert
            assert resolved.is_dir()

    def test_resolve_symlinks_with_string_path_returns_path_object(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            # Act
            resolved = resolve_symlinks(temp_dir)
            # Assert
            assert isinstance(resolved, Path)


# =============================================================================
# create_relative_symlink()
# =============================================================================


class TestCreateRelativeSymlink:
    """Tests for create_relative_symlink() function."""

    def test_create_relative_symlink_returns_dst_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            # Act
            result = create_relative_symlink(src, dst)
            # Assert
            assert result == dst

    def test_create_relative_symlink_creates_symlink_at_dst(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            # Act
            create_relative_symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_create_relative_symlink_stores_relative_target(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            # Act
            create_relative_symlink(src, dst)
            target = os.readlink(dst)
            # Assert
            assert not Path(target).is_absolute()

    def test_create_relative_symlink_overwrite_replaces_existing_link_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src1 = Path(temp_dir) / "source1.txt"
            src2 = Path(temp_dir) / "source2.txt"
            dst = Path(temp_dir) / "link.txt"
            src1.write_text("first")
            src2.write_text("second")
            create_relative_symlink(src1, dst)
            # Act
            create_relative_symlink(src2, dst, overwrite=True)
            # Assert
            assert dst.read_text() == "second"

    def test_create_relative_symlink_across_directories_creates_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src_dir = Path(temp_dir) / "src"
            dst_dir = Path(temp_dir) / "dst"
            src_dir.mkdir()
            dst_dir.mkdir()
            src = src_dir / "source.txt"
            dst = dst_dir / "link.txt"
            src.write_text("test")
            # Act
            create_relative_symlink(src, dst)
            # Assert
            assert dst.is_symlink()

    def test_create_relative_symlink_across_directories_resolves_to_source_content(
        self,
    ):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src_dir = Path(temp_dir) / "src"
            dst_dir = Path(temp_dir) / "dst"
            src_dir.mkdir()
            dst_dir.mkdir()
            src = src_dir / "source.txt"
            dst = dst_dir / "link.txt"
            src.write_text("test")
            # Act
            create_relative_symlink(src, dst)
            # Assert
            assert dst.read_text() == "test"


# =============================================================================
# unlink_symlink()
# =============================================================================


class TestUnlinkSymlink:
    """Tests for unlink_symlink() function."""

    def test_unlink_symlink_removes_symlink_entry(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            unlink_symlink(dst)
            # Assert
            assert not dst.is_symlink()

    def test_unlink_symlink_preserves_source_file(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("test")
            dst.symlink_to(src)
            # Act
            unlink_symlink(dst)
            # Assert
            assert src.exists()

    def test_unlink_symlink_missing_ok_true_does_not_raise(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dst = Path(temp_dir) / "nonexistent_link.txt"
            # Act
            unlink_symlink(dst, missing_ok=True)
            # Assert
            assert not dst.exists()

    def test_unlink_symlink_missing_ok_false_raises_file_not_found(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dst = Path(temp_dir) / "nonexistent_link.txt"
            # Act
            ctx = pytest.raises(FileNotFoundError)
            # Assert
            with ctx:
                unlink_symlink(dst, missing_ok=False)

    def test_unlink_symlink_raises_os_error_for_regular_file(self):
        # Arrange
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        try:
            # Act
            ctx = pytest.raises(OSError, match="not a symbolic link")
            # Assert
            with ctx:
                unlink_symlink(f.name)
        finally:
            os.unlink(f.name)

    def test_unlink_symlink_removes_broken_symlink_entry(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dst = Path(temp_dir) / "broken_link.txt"
            dst.symlink_to("/nonexistent/target")
            # Act
            unlink_symlink(dst)
            # Assert
            assert not dst.is_symlink()

    def test_unlink_symlink_with_string_path_removes_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = os.path.join(temp_dir, "link.txt")
            src.write_text("test")
            Path(dst).symlink_to(src)
            # Act
            unlink_symlink(dst)
            # Assert
            assert not Path(dst).exists()


# =============================================================================
# list_symlinks()
# =============================================================================


class TestListSymlinks:
    """Tests for list_symlinks() function."""

    def test_list_symlinks_returns_expected_count_of_links(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link1 = Path(temp_dir) / "link1.txt"
            link2 = Path(temp_dir) / "link2.txt"
            src.write_text("test")
            link1.symlink_to(src)
            link2.symlink_to(src)
            # Act
            result = list_symlinks(temp_dir)
            # Assert
            assert len(result) == 2

    def test_list_symlinks_contains_every_created_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link1 = Path(temp_dir) / "link1.txt"
            link2 = Path(temp_dir) / "link2.txt"
            src.write_text("test")
            link1.symlink_to(src)
            link2.symlink_to(src)
            # Act
            result = list_symlinks(temp_dir)
            # Assert
            assert {link1, link2}.issubset(set(result))

    def test_list_symlinks_returns_empty_when_no_symlinks_present(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            (Path(temp_dir) / "regular.txt").write_text("test")
            # Act
            result = list_symlinks(temp_dir)
            # Assert
            assert result == []

    def test_list_symlinks_non_recursive_returns_only_top_level_count(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link_top = Path(temp_dir) / "link_top.txt"
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            link_sub = subdir / "link_sub.txt"
            src.write_text("test")
            link_top.symlink_to(src)
            link_sub.symlink_to(src)
            # Act
            result = list_symlinks(temp_dir, recursive=False)
            # Assert
            assert result == [link_top]

    def test_list_symlinks_recursive_returns_links_from_all_subdirs(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link_top = Path(temp_dir) / "link_top.txt"
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            link_sub = subdir / "link_sub.txt"
            src.write_text("test")
            link_top.symlink_to(src)
            link_sub.symlink_to(src)
            # Act
            result = list_symlinks(temp_dir, recursive=True)
            # Assert
            assert set(result) == {link_top, link_sub}

    def test_list_symlinks_includes_broken_symlinks_in_result(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken_link = Path(temp_dir) / "broken.txt"
            broken_link.symlink_to("/nonexistent/target")
            # Act
            result = list_symlinks(temp_dir)
            # Assert
            assert result == [broken_link]

    def test_list_symlinks_returns_path_objects_for_each_entry(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link = Path(temp_dir) / "link.txt"
            src.write_text("test")
            link.symlink_to(src)
            # Act
            result = list_symlinks(temp_dir)
            # Assert
            assert all(isinstance(p, Path) for p in result)


# =============================================================================
# fix_broken_symlinks()
# =============================================================================


class TestFixBrokenSymlinks:
    """Tests for fix_broken_symlinks() function."""

    def test_fix_broken_symlinks_records_broken_link_in_found(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / "broken.txt"
            broken.symlink_to("/nonexistent/target")
            # Act
            result = fix_broken_symlinks(temp_dir)
            # Assert
            assert result["found"] == [broken]

    def test_fix_broken_symlinks_default_does_not_remove_anything(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / "broken.txt"
            broken.symlink_to("/nonexistent/target")
            # Act
            result = fix_broken_symlinks(temp_dir)
            # Assert
            assert result["removed"] == []

    def test_fix_broken_symlinks_default_does_not_fix_anything(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / "broken.txt"
            broken.symlink_to("/nonexistent/target")
            # Act
            result = fix_broken_symlinks(temp_dir)
            # Assert
            assert result["fixed"] == []

    def test_fix_broken_symlinks_ignores_valid_symlinks(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            valid_link = Path(temp_dir) / "valid.txt"
            src.write_text("test")
            valid_link.symlink_to(src)
            # Act
            result = fix_broken_symlinks(temp_dir)
            # Assert
            assert result["found"] == []

    def test_fix_broken_symlinks_remove_true_records_removed_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / "broken.txt"
            broken.symlink_to("/nonexistent/target")
            # Act
            result = fix_broken_symlinks(temp_dir, remove=True)
            # Assert
            assert result["removed"] == [broken]

    def test_fix_broken_symlinks_remove_true_removes_link_from_filesystem(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / "broken.txt"
            broken.symlink_to("/nonexistent/target")
            # Act
            fix_broken_symlinks(temp_dir, remove=True)
            # Assert
            assert not broken.is_symlink()

    def test_fix_broken_symlinks_repoint_records_fixed_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            new_src = Path(temp_dir) / "new_source.txt"
            broken = Path(temp_dir) / "broken.txt"
            new_src.write_text("new content")
            broken.symlink_to("/nonexistent/target")
            # Act
            result = fix_broken_symlinks(temp_dir, new_target=new_src)
            # Assert
            assert result["fixed"] == [broken]

    def test_fix_broken_symlinks_repoint_makes_link_resolve_to_new_content(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            new_src = Path(temp_dir) / "new_source.txt"
            broken = Path(temp_dir) / "broken.txt"
            new_src.write_text("new content")
            broken.symlink_to("/nonexistent/target")
            # Act
            fix_broken_symlinks(temp_dir, new_target=new_src)
            # Assert
            assert broken.read_text() == "new content"

    def test_fix_broken_symlinks_recursive_finds_links_in_subdirs(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            broken_top = Path(temp_dir) / "broken_top.txt"
            broken_sub = subdir / "broken_sub.txt"
            broken_top.symlink_to("/nonexistent/top")
            broken_sub.symlink_to("/nonexistent/sub")
            # Act
            result = fix_broken_symlinks(temp_dir, recursive=True)
            # Assert
            assert set(result["found"]) == {broken_top, broken_sub}

    def test_fix_broken_symlinks_non_recursive_skips_subdir_links(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            broken_top = Path(temp_dir) / "broken_top.txt"
            broken_sub = subdir / "broken_sub.txt"
            broken_top.symlink_to("/nonexistent/top")
            broken_sub.symlink_to("/nonexistent/sub")
            # Act
            result = fix_broken_symlinks(temp_dir, recursive=False)
            # Assert
            assert result["found"] == [broken_top]

    def test_fix_broken_symlinks_detects_broken_relative_symlink(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / "broken_relative.txt"
            broken.symlink_to("nonexistent_file.txt")
            # Act
            result = fix_broken_symlinks(temp_dir)
            # Assert
            assert result["found"] == [broken]

    def test_fix_broken_symlinks_mixed_only_records_broken_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            valid = Path(temp_dir) / "valid.txt"
            broken = Path(temp_dir) / "broken.txt"
            src.write_text("test")
            valid.symlink_to(src)
            broken.symlink_to("/nonexistent/target")
            # Act
            result = fix_broken_symlinks(temp_dir)
            # Assert
            assert result["found"] == [broken]


# =============================================================================
# Integration
# =============================================================================


class TestSymlinkIntegration:
    """Integration tests combining multiple symlink operations.

    Each integration test asserts a single fact at the end of a longer
    workflow; intermediate steps are setup (Arrange).
    """

    def test_create_then_readlink_then_unlink_workflow_removes_link(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            dst = Path(temp_dir) / "link.txt"
            src.write_text("workflow test")
            symlink(src, dst)
            readlink(dst)  # exercise read path
            # Act
            unlink_symlink(dst)
            # Assert
            assert not is_symlink(dst)

    def test_relative_symlink_portability_resolves_through_relative_path(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            src = project / "data" / "source.txt"
            dst = project / "links" / "link.txt"
            src.parent.mkdir()
            dst.parent.mkdir()
            src.write_text("portable content")
            # Act
            create_relative_symlink(src, dst)
            # Assert
            assert dst.read_text() == "portable content"

    def test_chain_of_three_symlinks_resolves_to_original_source(self):
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            src = Path(temp_dir) / "source.txt"
            link1 = Path(temp_dir) / "link1.txt"
            link2 = Path(temp_dir) / "link2.txt"
            link3 = Path(temp_dir) / "link3.txt"
            src.write_text("chained")
            link1.symlink_to(src)
            link2.symlink_to(link1)
            link3.symlink_to(link2)
            # Act
            resolved = resolve_symlinks(link3)
            # Assert
            assert resolved == src.resolve()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
