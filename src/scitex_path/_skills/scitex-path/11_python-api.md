---
description: |
  [TOPIC] Python API
  [DETAILS] Public functions grouped by search/location, path manipulation, SciTeX session paths, and symlink toolkit.
tags: [scitex-path-python-api]
---

<!-- 02_python-api.md -->

# scitex-path — Python API

Grouped view of `scitex_path.__all__`.

## Basic path handling

| Symbol | One-liner |
|--------|-----------|
| `clean` | Normalize a path (collapse `//`, `..`, trailing `/`). |
| `split` | Return `(dirname, stem, ext)` tuple for a path. |
| `getsize` | Human-readable size of a file or directory. |
| `get_this_path` / `this_path` | Absolute path of the calling `.py` script. |

## Search

| Symbol | One-liner |
|--------|-----------|
| `find_file` | Search for a filename under a root directory. |
| `find_dir` | Search for a directory name under a root. |
| `find_git_root` | Nearest ancestor containing `.git`. |
| `find_latest` | Latest versioned path matching a pattern. |

## SciTeX output paths

| Symbol | One-liner |
|--------|-----------|
| `get_spath` | Compute the canonical SciTeX output path for a script. |
| `mk_spath` | Like `get_spath`, creating the directory. |
| `get_data_path_from_a_package` | Resolve a package-internal data path. |
| `increment_version` | Bump `_v00N` suffix on a versioned path. |

## Symlinks

| Symbol | One-liner |
|--------|-----------|
| `symlink` | Create a symlink (overwrite-safe). |
| `create_relative_symlink` | Create a symlink with a relative target. |
| `readlink` | Resolve a symlink one level. |
| `resolve_symlinks` | Fully resolve a path, following all links. |
| `is_symlink` | Predicate for symlink paths. |
| `list_symlinks` | Enumerate symlinks under a root. |
| `fix_broken_symlinks` | Repair or remove dangling links. |
| `unlink_symlink` | Remove a symlink only (not its target). |

## Signatures

Open `scitex_path/_*.py` for exact argument lists — this package is a thin
utility layer and the file name matches the symbol name in each case
(`_find.py`, `_split.py`, `_symlink.py`, etc.).
