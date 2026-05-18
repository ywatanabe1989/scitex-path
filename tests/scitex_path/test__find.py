#!/usr/bin/env python3
# Time-stamp: "2024-11-08 05:53:35 (ywatanabe)"
# File: ./tests/scitex_path/test__find.py

"""Tests for ``scitex_path.find_git_root``, ``find_dir``, ``find_file``, and ``_find``.

PA-306: no ``unittest.mock``, no ``monkeypatch``. Collaborators are
swapped at module namespace level via real save/restore context managers.

STX-TQ001 / 002 / 003 / 007: every test asserts exactly one fact, has
the three AAA marker comments, and has a descriptive multi-token name.
"""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Tuple

import pytest

pytest.importorskip("git")

import scitex_path._find as _find_mod
from scitex_path import find_dir, find_file, find_git_root
from scitex_path._find import _find

# ---------------------------------------------------------------------------
# Collaborator swaps (test seams — no mocks, no monkeypatch)
# ---------------------------------------------------------------------------


@contextmanager
def _swap_git_repo(fn: Callable[..., Any]) -> Iterator[List[Tuple[Any, Any]]]:
    """Replace ``git.Repo`` with ``fn``; yield a recorder list of (args, kwargs)."""
    import git

    saved = git.Repo
    calls: List[Tuple[Any, Any]] = []

    def recording(*args: Any, **kwargs: Any) -> Any:
        calls.append((args, kwargs))
        return fn(*args, **kwargs)

    git.Repo = recording  # type: ignore[assignment]
    try:
        yield calls
    finally:
        git.Repo = saved  # type: ignore[assignment]


@contextmanager
def _swap_module_find(fn: Callable[..., Any]) -> Iterator[List[Tuple[Any, Any]]]:
    """Replace ``_find._find`` with ``fn``; yield a recorder list of (args, kwargs)."""
    saved = _find_mod._find
    calls: List[Tuple[Any, Any]] = []

    def recording(*args: Any, **kwargs: Any) -> Any:
        calls.append((args, kwargs))
        return fn(*args, **kwargs)

    _find_mod._find = recording  # type: ignore[assignment]
    try:
        yield calls
    finally:
        _find_mod._find = saved  # type: ignore[assignment]


@contextmanager
def _swap_os_walk(
    walk_result: List[Tuple[str, List[str], List[str]]],
) -> Iterator[None]:
    """Replace ``_find.os.walk`` with one that yields ``walk_result``."""
    saved = _find_mod.os.walk

    def fake_walk(_root: str) -> Iterator[Tuple[str, List[str], List[str]]]:
        for entry in walk_result:
            yield entry

    _find_mod.os.walk = fake_walk  # type: ignore[assignment]
    try:
        yield
    finally:
        _find_mod.os.walk = saved  # type: ignore[assignment]


@contextmanager
def _swap_os_path_isfile(fn: Callable[[str], bool]) -> Iterator[None]:
    saved = _find_mod.os.path.isfile
    _find_mod.os.path.isfile = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        _find_mod.os.path.isfile = saved  # type: ignore[assignment]


@contextmanager
def _swap_os_path_isdir(fn: Callable[[str], bool]) -> Iterator[None]:
    saved = _find_mod.os.path.isdir
    _find_mod.os.path.isdir = fn  # type: ignore[assignment]
    try:
        yield
    finally:
        _find_mod.os.path.isdir = saved  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Lightweight stand-ins
# ---------------------------------------------------------------------------


class _FakeRepo:
    def __init__(self, working_tree_dir: str) -> None:
        self.working_tree_dir = working_tree_dir


# =============================================================================
# find_git_root
# =============================================================================


class TestFindGitRoot:
    def test_find_git_root_returns_working_tree_dir_from_git_repo(self):
        # Arrange
        def make_repo(_dot: str, **_kwargs: Any) -> _FakeRepo:
            return _FakeRepo("/home/user/my_project")

        # Act
        with _swap_git_repo(make_repo):
            result = find_git_root()
        # Assert
        assert result == "/home/user/my_project"

    def test_find_git_root_calls_git_repo_with_search_parent_directories_true(self):
        # Arrange
        def make_repo(_dot: str, **_kwargs: Any) -> _FakeRepo:
            return _FakeRepo("/home/user/my_project")

        # Act
        with _swap_git_repo(make_repo) as calls:
            find_git_root()
        # Assert
        assert calls[0][1]["search_parent_directories"] is True

    def test_find_git_root_passes_dot_as_positional_search_root(self):
        # Arrange
        def make_repo(_dot: str, **_kwargs: Any) -> _FakeRepo:
            return _FakeRepo("/home/user/my_project")

        # Act
        with _swap_git_repo(make_repo) as calls:
            find_git_root()
        # Assert
        assert calls[0][0] == (".",)

    def test_find_git_root_propagates_invalid_git_repository_error(self):
        # Arrange
        import git

        def raise_invalid(*_args: Any, **_kwargs: Any) -> _FakeRepo:
            raise git.InvalidGitRepositoryError("Not a git repo")

        # Act
        ctx = pytest.raises(git.InvalidGitRepositoryError)
        # Assert
        with _swap_git_repo(raise_invalid), ctx:
            find_git_root()


# =============================================================================
# find_dir
# =============================================================================


class TestFindDir:
    def test_find_dir_returns_collaborator_result_for_directory_search(self):
        # Arrange
        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return ["/path/to/dir"]

        # Act
        with _swap_module_find(fake_find):
            result = find_dir("/root", "test_*")
        # Assert
        assert result == ["/path/to/dir"]

    def test_find_dir_invokes_underlying_find_with_type_directory(self):
        # Arrange
        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return []

        # Act
        with _swap_module_find(fake_find) as calls:
            find_dir("/root", "test_*")
        # Assert
        assert calls[0][1]["type"] == "d"

    def test_find_dir_forwards_expression_argument_to_underlying_find(self):
        # Arrange
        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return []

        # Act
        with _swap_module_find(fake_find) as calls:
            find_dir("/root", "test_*")
        # Assert
        assert calls[0][1]["exp"] == "test_*"

    def test_find_dir_propagates_multi_path_results_unchanged(self):
        # Arrange
        expected_dirs = ["/root/test_dir1", "/root/sub/test_dir2"]

        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return list(expected_dirs)

        # Act
        with _swap_module_find(fake_find):
            result = find_dir("/root", "test_*")
        # Assert
        assert result == expected_dirs


# =============================================================================
# find_file
# =============================================================================


class TestFindFile:
    def test_find_file_returns_collaborator_result_for_file_search(self):
        # Arrange
        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return ["/path/to/file.txt"]

        # Act
        with _swap_module_find(fake_find):
            result = find_file("/root", "*.txt")
        # Assert
        assert result == ["/path/to/file.txt"]

    def test_find_file_invokes_underlying_find_with_type_file(self):
        # Arrange
        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return []

        # Act
        with _swap_module_find(fake_find) as calls:
            find_file("/root", "*.txt")
        # Assert
        assert calls[0][1]["type"] == "f"

    def test_find_file_forwards_expression_argument_to_underlying_find(self):
        # Arrange
        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return []

        # Act
        with _swap_module_find(fake_find) as calls:
            find_file("/root", "*.txt")
        # Assert
        assert calls[0][1]["exp"] == "*.txt"

    def test_find_file_propagates_multi_file_results_unchanged(self):
        # Arrange
        expected_files = ["/root/test.txt", "/root/sub/data.txt"]

        def fake_find(*_a: Any, **_kw: Any) -> List[str]:
            return list(expected_files)

        # Act
        with _swap_module_find(fake_find):
            result = find_file("/root", "*.txt")
        # Assert
        assert result == expected_files


# =============================================================================
# _find (low-level)
# =============================================================================


class TestFindLowLevel:
    def test_find_returns_matching_files_only_with_glob_pattern(self):
        # Arrange
        walk_result = [
            ("/root", ["dir1", "dir2"], ["file1.txt", "file2.py"]),
            ("/root/dir1", [], ["file3.txt"]),
            ("/root/dir2", [], ["file4.py"]),
        ]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp="*.txt")
        # Assert
        assert result == ["/root/file1.txt", "/root/dir1/file3.txt"]

    def test_find_returns_matching_directories_only(self):
        # Arrange
        walk_result = [
            ("/root", ["test_dir1", "test_dir2", "other_dir"], ["file1.txt"]),
            ("/root/test_dir1", ["test_sub"], []),
        ]
        expected = ["/root/test_dir1", "/root/test_dir2", "/root/test_dir1/test_sub"]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isdir(lambda _p: True):
            result = _find("/root", type="d", exp="test_*")
        # Assert
        assert result == expected

    def test_find_with_type_none_returns_files_and_directories_sorted(self):
        # Arrange
        walk_result = [("/root", ["test_dir"], ["test_file.txt"])]
        expected = sorted(["/root/test_file.txt", "/root/test_dir"])
        # Act
        with (
            _swap_os_walk(walk_result),
            _swap_os_path_isfile(lambda _p: True),
            _swap_os_path_isdir(lambda _p: True),
        ):
            result = _find("/root", type=None, exp="test_*")
        # Assert
        assert sorted(result) == expected

    def test_find_with_string_expression_returns_single_match(self):
        # Arrange
        walk_result = [("/root", [], ["test.txt"])]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp="*.txt")
        # Assert
        assert len(result) == 1

    def test_find_with_list_expression_returns_union_of_matches(self):
        # Arrange
        walk_result = [("/root", [], ["test.txt", "data.csv", "script.py"])]
        expected = sorted(["/root/test.txt", "/root/data.csv"])
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp=["*.txt", "*.csv"])
        # Assert
        assert sorted(result) == expected

    def test_find_excludes_files_under_lib_env_build_directories(self):
        # Arrange
        walk_result = [
            ("/root", ["normal", "lib", "env", "build"], []),
            ("/root/normal", [], ["file.txt"]),
            ("/root/lib", [], ["lib_file.txt"]),
            ("/root/env", [], ["env_file.txt"]),
            ("/root/build", [], ["build_file.txt"]),
        ]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp="*.txt")
        # Assert
        assert result == ["/root/normal/file.txt"]

    def test_find_excludes_paths_containing_lib_segment(self):
        # Arrange
        walk_result = [
            ("/root", ["lib", "project"], []),
            ("/root/lib/src", [], ["file.txt"]),
            ("/root/project", [], ["main.py"]),
        ]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp="*")
        # Assert
        assert result == ["/root/project/main.py"]

    def test_find_returns_empty_list_for_empty_directory(self):
        # Arrange
        walk_result = [("/root", [], [])]
        # Act
        with _swap_os_walk(walk_result):
            result = _find("/root", type="f", exp="*")
        # Assert
        assert result == []

    def test_find_returns_empty_list_when_no_pattern_matches(self):
        # Arrange
        walk_result = [("/root", [], ["file.txt", "data.csv"])]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp="*.py")
        # Assert
        assert result == []

    def test_find_supports_character_class_glob_pattern(self):
        # Arrange
        walk_result = [
            ("/root", [], ["test_1.txt", "test_2.txt", "test_abc.txt", "data.txt"])
        ]
        expected = sorted(["/root/test_1.txt", "/root/test_2.txt"])
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda _p: True):
            result = _find("/root", type="f", exp="test_[0-9].txt")
        # Assert
        assert sorted(result) == expected

    def test_find_type_file_includes_only_file_paths(self):
        # Arrange
        walk_result = [("/root", ["dir1"], ["file1.txt"])]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isfile(lambda p: "file" in p):
            result = _find("/root", type="f", exp="*")
        # Assert
        assert all("file" in p for p in result)

    def test_find_type_directory_includes_only_directory_paths(self):
        # Arrange
        walk_result = [("/root", ["dir1"], ["file1.txt"])]
        # Act
        with _swap_os_walk(walk_result), _swap_os_path_isdir(lambda p: "dir" in p):
            result = _find("/root", type="d", exp="*")
        # Assert
        assert all("dir" in p for p in result)


# =============================================================================
# Integration with real filesystem
# =============================================================================


class TestFindRealFilesystem:
    def test_find_real_txt_files_finds_one_outside_excluded_lib(self):
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "subdir"))
            os.makedirs(os.path.join(tmpdir, "test_dir"))
            os.makedirs(os.path.join(tmpdir, "lib"))  # excluded
            open(os.path.join(tmpdir, "test.txt"), "w").close()
            open(os.path.join(tmpdir, "data.csv"), "w").close()
            open(os.path.join(tmpdir, "subdir", "test.py"), "w").close()
            open(os.path.join(tmpdir, "lib", "excluded.txt"), "w").close()
            # Act
            txt_files = _find(tmpdir, type="f", exp="*.txt")
            # Assert
            assert len(txt_files) == 1

    def test_find_real_directories_with_test_prefix_finds_one(self):
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "test_dir"))
            os.makedirs(os.path.join(tmpdir, "lib"))
            # Act
            dirs = _find(tmpdir, type="d", exp="test_*")
            # Assert
            assert len(dirs) == 1

    def test_find_real_all_files_skips_excluded_lib_directory(self):
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "subdir"))
            os.makedirs(os.path.join(tmpdir, "lib"))
            open(os.path.join(tmpdir, "test.txt"), "w").close()
            open(os.path.join(tmpdir, "data.csv"), "w").close()
            open(os.path.join(tmpdir, "subdir", "test.py"), "w").close()
            open(os.path.join(tmpdir, "lib", "excluded.txt"), "w").close()
            # Act
            all_files = _find(tmpdir, type="f", exp="*")
            # Assert
            assert len(all_files) == 3


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
