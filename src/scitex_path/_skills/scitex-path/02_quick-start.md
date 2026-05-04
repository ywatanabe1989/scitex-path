---
description: |
  [TOPIC] scitex-path Quick start
  [DETAILS] Find files, locate git root, build session paths, and create relative symlinks.
tags: [scitex-path-quick-start]
---

# Quick Start

## Find a file walking up

```python
from scitex_path import find_file, find_dir, find_git_root

cfg = find_file("config.yaml")        # walks up from cwd
data_dir = find_dir("data")
repo_root = find_git_root()           # nearest .git/
```

## SciTeX session paths

```python
from scitex_path import get_spath, mk_spath

# get_spath = "session path" — the script_out/<session_id>/ for the
# currently running script. Created on first call.
out = mk_spath("results.csv")         # ./script_out/<session>/results.csv
```

## Versioned output dirs

```python
from scitex_path import increment_version, find_latest

next_dir = increment_version("runs/v00")     # runs/v001, v002, ...
latest   = find_latest("runs/v00")           # highest existing version
```

## Symlink hygiene

```python
from scitex_path import (
    create_relative_symlink,
    fix_broken_symlinks,
    list_symlinks,
)

create_relative_symlink(target="data/raw.csv", link="latest/raw.csv")
fix_broken_symlinks("./outputs")             # auto-prune dangling links
```

## Next

- [03_python-api.md](03_python-api.md) — full API grouped by topic
- [SKILL.md](SKILL.md) — overview
