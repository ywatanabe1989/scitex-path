---
description: |
  [TOPIC] scitex-path Python API
  [DETAILS] Public callables grouped — finders, session paths, versioning, symlink helpers, misc.
tags: [scitex-path-python-api]
---

# Python API

## Imports

```python
from scitex_path import (
    # Finders
    find_file, find_dir, find_git_root,
    # Session paths (SciTeX `script_out/`)
    get_spath, mk_spath,
    # Versioning
    increment_version, find_latest,
    # Symlinks
    create_relative_symlink, fix_broken_symlinks,
    is_symlink, list_symlinks, readlink, resolve_symlinks,
    symlink, unlink_symlink,
    # Misc
    clean, getsize, split,
    get_this_path, this_path,
    get_data_path_from_a_package,
)
```

## Finders

| Symbol | Purpose |
|---|---|
| `find_file(name)` | Walk up directories looking for `name` |
| `find_dir(name)` | Same, for directories |
| `find_git_root()` | Locate nearest enclosing `.git/` |

## Session paths (SciTeX convention)

| Symbol | Purpose |
|---|---|
| `get_spath()` | Return the current script's `script_out/<session>/` |
| `mk_spath(rel)` | Same path, joined with `rel`; creates parent dirs |

These are the canonical scitex outputs path used by `@stx.session`.

## Versioning

| Symbol | Purpose |
|---|---|
| `increment_version(prefix)` | Next free `prefix` + zero-padded number |
| `find_latest(prefix)` | Highest existing version under `prefix` |

## Symlinks

| Symbol | Purpose |
|---|---|
| `create_relative_symlink(target, link)` | Symlink with relative target |
| `fix_broken_symlinks(root)` | Remove dangling symlinks under `root` |
| `is_symlink(p)` | Bool predicate |
| `list_symlinks(root)` | Iterate all symlinks under `root` |
| `readlink(p)` | Resolve one level (stdlib-compatible) |
| `resolve_symlinks(p)` | Fully resolve symlink chain |
| `symlink(target, link)` | Wrapped `os.symlink` |
| `unlink_symlink(link)` | Safe unlink (no-op if absent) |

## Misc

| Symbol | Purpose |
|---|---|
| `clean(p)` | Normalize a path string (strip trailing /, expand ~) |
| `getsize(p)` | Recursive size in bytes |
| `split(p)` | Split into `(parent, stem, suffix)` |
| `get_this_path()` / `this_path()` | Path of the calling script |
| `get_data_path_from_a_package(pkg)` | Resolve `pkg/data/` for installed package |

## Two import paths

```python
import scitex_path        # standalone
import scitex.path        # umbrella (requires `pip install scitex`)
```
