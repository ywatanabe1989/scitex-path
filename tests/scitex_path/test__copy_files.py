#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_path.copy_files / copy_the_file / _copy_a_file."""
from __future__ import annotations

import os

import pytest

from scitex_path import _copy_a_file, copy_files, copy_the_file


class TestCopyAFile:
    def test_copies_to_explicit_dst(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("hello")
        dst = tmp_path / "dst.txt"
        _copy_a_file(str(src), str(dst))
        assert dst.read_text() == "hello"

    def test_dir_dest_with_trailing_slash(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("hello")
        dst_dir = tmp_path / "out"
        dst_dir.mkdir()
        _copy_a_file(str(src), str(dst_dir) + "/")
        assert (dst_dir / "src.txt").read_text() == "hello"

    def test_no_overwrite_by_default(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("new")
        dst = tmp_path / "dst.txt"
        dst.write_text("old")
        _copy_a_file(str(src), str(dst))
        assert dst.read_text() == "old"

    def test_allow_overwrite(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("new")
        dst = tmp_path / "dst.txt"
        dst.write_text("old")
        _copy_a_file(str(src), str(dst), allow_overwrite=True)
        assert dst.read_text() == "new"


class TestCopyFiles:
    def test_single_src_single_dst(self, tmp_path):
        src = tmp_path / "a.txt"
        src.write_text("A")
        dst = tmp_path / "dst.txt"
        copy_files(str(src), str(dst))
        assert dst.read_text() == "A"

    def test_multi_src_multi_dst(self, tmp_path):
        src1 = tmp_path / "a.txt"
        src1.write_text("A")
        src2 = tmp_path / "b.txt"
        src2.write_text("B")
        out1 = tmp_path / "out1"
        out2 = tmp_path / "out2"
        out1.mkdir()
        out2.mkdir()
        copy_files(
            [str(src1), str(src2)],
            [str(out1) + "/", str(out2) + "/"],
        )
        for out in (out1, out2):
            assert (out / "a.txt").read_text() == "A"
            assert (out / "b.txt").read_text() == "B"


class TestCopyTheFile:
    def test_copies_caller_file(self, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        copy_the_file(str(out) + "/")
        # The caller is this test file, so the copy should land there.
        assert (out / "test__copy_files.py").exists()

    def test_ipython_caller_skipped(self, tmp_path, monkeypatch):
        # Simulate an ipython frame by patching inspect.stack so the
        # filename contains 'ipython'.
        import inspect

        class FakeFrame:
            filename = "/tmp/ipython-shell-input"

        original_stack = inspect.stack

        def fake_stack():
            real = original_stack()
            return [real[0], FakeFrame()]  # type: ignore[list-item]

        monkeypatch.setattr(inspect, "stack", fake_stack)
        out = tmp_path / "out"
        out.mkdir()
        copy_the_file(str(out) + "/")
        assert list(out.iterdir()) == []
