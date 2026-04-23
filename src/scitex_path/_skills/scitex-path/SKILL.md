---
name: scitex-path
description: Project-aware path utilities for scientific Python — finding files/dirs/git roots, SciTeX `script_out/` session-path conventions, versioned directories, and symlink hygiene. Public API — search/location (`find_file`, `find_dir`, `find_git_root`, `find_latest`), path manipulation (`clean`, `split`, `getsize`, `increment_version`), SciTeX session paths (`get_spath`, `mk_spath`, `get_this_path`, `this_path`, `get_data_path_from_a_package`), symlink toolkit (`symlink`, `create_relative_symlink`, `readlink`, `is_symlink`, `list_symlinks`, `resolve_symlinks`, `unlink_symlink`, `fix_broken_symlinks`). No CLI, no MCP tools. Drop-in replacement for hand-rolling `pathlib.Path.rglob` loops to locate files, walking up directories to find `.git/`, ad-hoc `os.path.splitext`+`basename` chains, manual `v001`/`v002` versioning logic, and bespoke `os.symlink`+`os.readlink`+`os.path.islink` scripts that miss relative-symlink edge cases. Use whenever the user asks to "find a file up/down the tree", "locate the git root", "find the latest versioned output directory", "split a path into dir/stem/ext", "build a script_out path for this session", "create a relative symlink", "list all symlinks under a directory", "fix broken symlinks", "bump the v00X version of an output folder", or mentions `scitex.path`, `get_spath`, `find_git_root`, SciTeX session paths.
user-invocable: false
---

# scitex-path

Path helpers tailored to SciTeX conventions (`script_out/`, versioned run
directories, symlink hygiene). Wraps `os.path` / `pathlib` with project-aware
semantics.

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-path
import scitex_path
scitex_path.find_file(...)

# Umbrella — pip install scitex
import scitex.path
scitex.path.find_file(...)
```

`pip install scitex-path` alone does NOT expose the `scitex` namespace;
`import scitex.path` raises `ModuleNotFoundError`. To use the
`scitex.path` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.

## Sub-skills

- [01_quick-start.md](01_quick-start.md) — install, import, 3 usage snippets
- [02_python-api.md](02_python-api.md) — all public functions, grouped

No CLI, no MCP tools.
