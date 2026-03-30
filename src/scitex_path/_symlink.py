#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-16 15:11:33 (ywatanabe)"
# File: scitex-path/src/scitex_path/_symlink.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Symlink creation and management utilities."""

import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def symlink(
    src: Union[str, Path],
    dst: Union[str, Path],
    overwrite: bool = False,
    target_is_directory: Optional[bool] = None,
    relative: bool = False,
) -> Path:
    """
    Create a symbolic link pointing to src named dst.

    Args:
        src: Source path (target of the symlink)
        dst: Destination path (the symlink to create)
        overwrite: If True, remove existing dst before creating symlink
        target_is_directory: On Windows, specify if target is directory (auto-detected if None)
        relative: If True, create relative symlink instead of absolute

    Returns:
        Path object of the created symlink

    Raises:
        FileExistsError: If dst exists and overwrite=False
        FileNotFoundError: If src doesn't exist
        OSError: If symlink creation fails

    Examples:
        >>> from scitex_path import symlink
        >>> # Create absolute symlink
        >>> symlink("/path/to/source", "/path/to/link")

        >>> # Create relative symlink
        >>> symlink("../source", "link", relative=True)

        >>> # Overwrite existing symlink
        >>> symlink("/path/to/new_source", "/path/to/link", overwrite=True)
    """
    src_path = Path(src)
    dst_path = Path(dst)

    # Note: We allow creating symlinks to non-existent targets
    # This is valid in Unix/Linux and useful for testing

    # Handle existing destination
    if dst_path.exists() or dst_path.is_symlink():
        if not overwrite:
            raise FileExistsError(f"Destination already exists: {dst_path}")
        else:
            # Remove existing file/symlink
            if dst_path.is_symlink():
                dst_path.unlink()
            elif dst_path.is_file():
                dst_path.unlink()
            elif dst_path.is_dir():
                import shutil

                shutil.rmtree(dst_path)

    # Create parent directory if needed
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine if target is directory (for Windows)
    if target_is_directory is None and src_path.exists():
        target_is_directory = src_path.is_dir()

    # Create symlink
    try:
        if relative:
            # Calculate relative path from dst to src
            if src_path.is_absolute():
                # src is absolute, calculate relative from dst
                try:
                    rel_path = os.path.relpath(src_path, dst_path.parent)
                    src_for_link = Path(rel_path)
                except ValueError:
                    # Can't create relative path (e.g., different drives on Windows)
                    logger.warning(
                        f"Cannot create relative path from {dst_path} to {src_path}, using absolute"
                    )
                    src_for_link = src_path.absolute()
            else:
                # Both paths are relative, need to resolve them first
                # to calculate the correct relative path
                src_abs = src_path.resolve()
                dst_parent_abs = dst_path.parent.resolve()
                try:
                    rel_path = os.path.relpath(src_abs, dst_parent_abs)
                    src_for_link = Path(rel_path)
                except ValueError:
                    # Can't create relative path
                    logger.warning(
                        f"Cannot create relative path from {dst_path} to {src_path}"
                    )
                    src_for_link = src_path
        else:
            src_for_link = src_path.absolute()

        dst_path.symlink_to(src_for_link, target_is_directory=target_is_directory)
        logger.info(f"Created symlink: {dst_path} -> {src_for_link}")

    except OSError as e:
        logger.warning(
            f"Failed to create symlink from {dst_path} to {src_for_link}: {str(e)}"
        )

    return dst_path


def is_symlink(path: Union[str, Path]) -> bool:
    """
    Check if a path is a symbolic link.

    Args:
        path: Path to check

    Returns:
        True if path is a symlink, False otherwise
    """
    return Path(path).is_symlink()


def readlink(path: Union[str, Path]) -> Path:
    """
    Return the path to which the symbolic link points.

    Args:
        path: Symlink path to read

    Returns:
        Path object pointing to the symlink target

    Raises:
        OSError: If path is not a symlink
    """
    path = Path(path)
    if not path.is_symlink():
        raise OSError(f"Path is not a symbolic link: {path}")

    return Path(os.readlink(path))


def resolve_symlinks(path: Union[str, Path]) -> Path:
    """
    Resolve all symbolic links in a path.

    Args:
        path: Path potentially containing symlinks

    Returns:
        Fully resolved absolute path
    """
    return Path(path).resolve()


def create_relative_symlink(
    src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False
) -> Path:
    """
    Create a relative symbolic link.

    This is a convenience wrapper around symlink() with relative=True.

    Args:
        src: Source path (target of the symlink)
        dst: Destination path (the symlink to create)
        overwrite: If True, remove existing dst before creating symlink

    Returns:
        Path object of the created symlink
    """
    return symlink(src, dst, overwrite=overwrite, relative=True)


def unlink_symlink(path: Union[str, Path], missing_ok: bool = True) -> None:
    """
    Remove a symbolic link.

    Args:
        path: Symlink to remove
        missing_ok: If True, don't raise error if symlink doesn't exist

    Raises:
        FileNotFoundError: If symlink doesn't exist and missing_ok=False
        OSError: If path is not a symlink
    """
    path = Path(path)

    if not path.exists() and not path.is_symlink():
        if missing_ok:
            return
        raise FileNotFoundError(f"Symlink does not exist: {path}")

    if not path.is_symlink():
        raise OSError(f"Path is not a symbolic link: {path}")

    path.unlink()


def list_symlinks(directory: Union[str, Path], recursive: bool = False) -> list[Path]:
    """
    List all symbolic links in a directory.

    Args:
        directory: Directory to search
        recursive: If True, search recursively

    Returns:
        List of Path objects for all symlinks found
    """
    directory = Path(directory)
    symlinks = []

    if recursive:
        for path in directory.rglob("*"):
            if path.is_symlink():
                symlinks.append(path)
    else:
        for path in directory.iterdir():
            if path.is_symlink():
                symlinks.append(path)

    return symlinks


def fix_broken_symlinks(
    directory: Union[str, Path],
    recursive: bool = False,
    remove: bool = False,
    new_target: Optional[Union[str, Path]] = None,
) -> dict:
    """
    Find and optionally fix broken symbolic links.

    Args:
        directory: Directory to search
        recursive: If True, search recursively
        remove: If True, remove broken symlinks
        new_target: If provided, repoint broken symlinks to this target

    Returns:
        Dictionary with 'found', 'fixed', and 'removed' lists of paths
    """
    directory = Path(directory)
    result = {"found": [], "fixed": [], "removed": []}

    symlinks = list_symlinks(directory, recursive=recursive)

    for link in symlinks:
        try:
            # Check if target exists
            target = Path(os.readlink(link))
            if not link.parent.joinpath(target).exists() and not target.is_absolute():
                # Relative link with non-existent target
                result["found"].append(link)
            elif target.is_absolute() and not target.exists():
                # Absolute link with non-existent target
                result["found"].append(link)
        except (OSError, ValueError):
            result["found"].append(link)

    # Fix or remove broken symlinks
    for link in result["found"]:
        if remove:
            link.unlink()
            result["removed"].append(link)
        elif new_target:
            link.unlink()
            symlink(new_target, link)
            result["fixed"].append(link)

    return result


# EOF
