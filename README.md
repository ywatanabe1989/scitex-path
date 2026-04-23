# scitex-path

Scientific project path utilities for the [SciTeX](https://github.com/ywatanabe1989/scitex-python) ecosystem.

Provides file/directory finding, path splitting, symlink management, and version incrementing.

## Problem and Solution


| # | Problem | Solution |
|---|---------|----------|
| 1 | **Scripts hard-code `/home/user/proj/...` paths** -- break the moment someone else runs them | **`find_git_root()` + `get_spath(filename)`** -- paths auto-resolve to the repo root and the current script's `_out/` dir |
| 2 | **`{script}_out/` convention implemented 33 different ways across the ecosystem** -- inconsistent, error-prone | **Canonical helpers** -- `mk_spath`, `get_this_path`, `create_relative_symlink`, `find_latest` standardize the pattern |

## Installation

```bash
pip install scitex-path
```

## Usage

```python
import scitex_path as sp

# Find files by pattern
matches = sp.find_file("*.csv", root="/data/project")

# Find the nearest git root
git_root = sp.find_git_root()

# Split path into components
parts = sp.split("/home/user/project/data/results.csv")

# Symlink management
sp.symlink("/data/raw", "/project/data/raw")
sp.list_symlinks("/project/data")
sp.fix_broken_symlinks("/project/data")

# Version incrementing
next_ver = sp.increment_version("v1.2.3", part="patch")  # "v1.2.4"
latest = sp.find_latest("/results/experiment_v*")
```

## API

| Function | Description |
|---|---|
| `find_file` | Find files matching a glob pattern |
| `find_dir` | Find directories matching a glob pattern |
| `find_git_root` | Locate the nearest `.git` root |
| `split` | Split a path into structured components |
| `symlink` | Create a symlink |
| `create_relative_symlink` | Create a relative symlink |
| `list_symlinks` | List symlinks under a directory |
| `fix_broken_symlinks` | Remove or report broken symlinks |
| `resolve_symlinks` | Resolve all symlinks to real paths |
| `increment_version` | Bump a version string |
| `find_latest` | Find the latest versioned path |
| `clean` | Clean/normalize a path |
| `getsize` | Get file/directory size |
| `get_spath` / `mk_spath` | Session path helpers |
| `this_path` / `get_this_path` | Get the path of the calling script |

## License

AGPL-3.0 -- see [LICENSE](LICENSE) for details.
