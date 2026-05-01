# scitex-path

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-path.svg)](https://pypi.org/project/scitex-path/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-path.svg)](https://pypi.org/project/scitex-path/)
[![Tests](https://github.com/ywatanabe1989/scitex-path/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-path/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-path/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-path/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-path/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-path)
[![Docs](https://readthedocs.org/projects/scitex-path/badge/?version=latest)](https://scitex-path.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Scientific project path utilities — find files / git root, symlink mgmt, version increment.</b></p>

<p align="center">
  <a href="https://scitex-path.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-path</code>
</p>

---

## Problem and Solution

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Scripts hard-code `/home/user/proj/...` paths** — break the moment someone else runs them | **`find_git_root()` + `get_spath(filename)`** — paths auto-resolve to the repo root and the current script's `_out/` dir |
| 2 | **`{script}_out/` convention implemented 33 different ways** — inconsistent, error-prone | **Canonical helpers** — `mk_spath`, `get_this_path`, `create_relative_symlink`, `find_latest` standardize the pattern |

## Installation

```bash
pip install scitex-path
```

## Quick Start

```python
import scitex_path as sp

git_root = sp.find_git_root()
matches = sp.find_file("*.csv", root="/data/project")
```

## 1 Interfaces

<details>
<summary><strong>Python API</strong></summary>

<br>

```python
import scitex_path as sp

# Find
sp.find_file("*.csv", root="/data/project")
sp.find_dir("results_*", root="/runs")
sp.find_git_root()
sp.find_latest("/results/experiment_v*")

# Path manipulation
sp.split("/home/user/project/data/results.csv")
sp.clean("path/with/../spaces ")
sp.getsize("/path/to/dir")

# Symlinks
sp.symlink("/data/raw", "/project/data/raw")
sp.create_relative_symlink(src, dst)
sp.list_symlinks("/project/data")
sp.fix_broken_symlinks("/project/data")
sp.resolve_symlinks(path)

# Versioning
sp.increment_version("v1.2.3", part="patch")  # "v1.2.4"

# Session paths (relative to calling script)
sp.this_path() / sp.get_this_path()
sp.get_spath(filename) / sp.mk_spath(filename)
```

</details>

## Part of SciTeX

`scitex-path` is part of [**SciTeX**](https://scitex.ai).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

## License

AGPL-3.0 — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>
