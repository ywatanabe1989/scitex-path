---
name: scitex-path
description: Scientific project path utilities — find_file files/dirs/git root, clean and split paths, symlink management, and versioned output paths. Use when writing SciTeX scripts that need conventional paths.
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
