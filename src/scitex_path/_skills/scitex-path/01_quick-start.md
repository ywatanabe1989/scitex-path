---
name: quick-start
description: scitex-path — Quick Start — see file body for details.
tags: [scitex-path, scitex-package]
---

<!-- 01_quick-start.md -->

# scitex-path — Quick Start

## Install

```bash
pip install scitex-path
```

## Import

```python
from scitex_path import (
    clean, split, this_path, find_file, find_git_root,
    mk_spath, increment_version, symlink,
)
```

## Usage

### Get the path of the currently executing script

```python
from scitex_path import this_path

here = this_path()         # /abs/path/to/your_script.py
```

### Split a path into (dirname, stem, ext)

```python
from scitex_path import split

d, stem, ext = split("/data/run/output.csv")
# d = "/data/run", stem = "output", ext = ".csv"
```

### Find the enclosing git repo root

```python
from scitex_path import find_git_root

root = find_git_root()     # nearest ancestor containing .git
```

### Versioned output path

```python
from scitex_path import increment_version

# Given existing ./out_v001, returns ./out_v002 (does not create it)
next_dir = increment_version("./out")
```
