---
name: scitex-path
description: |
  [WHAT] Project-aware path utilities — find files/dirs/git roots, SciTeX session-path conventions (`get_spath`, `mk_spath`), versioned directories, and symlink hygiene helpers.
  [WHEN] Finding files up/down a tree, locating the git root, building per-session script_out paths, creating relative symlinks, fixing broken symlinks, or bumping `v00X` output versions.
  [HOW] `from scitex_path import find_file, find_git_root, get_spath, create_relative_symlink, increment_version, ...` — works on top of pathlib.
tags: [scitex-path]
primary_interface: python
interfaces:
  python: 3
  cli: 0
  mcp: 0
  skills: 2
  http: 0
---

# scitex-path

> **Interfaces:** Python ⭐⭐⭐ (primary) · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP —

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
