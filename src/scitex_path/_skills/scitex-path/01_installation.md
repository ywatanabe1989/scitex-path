---
description: |
  [TOPIC] scitex-path Installation
  [DETAILS] pip install scitex-path (pure Python, no required deps); smoke verify with import + find_git_root.
tags: [scitex-path-installation]
---

# Installation

## Standard

```bash
pip install scitex-path
```

Pure-Python; no required runtime dependencies (uses only stdlib
`pathlib` / `os.path`).

## Verify

```bash
python -c "import scitex_path; print(scitex_path.__version__)"
python -c "from scitex_path import find_file, find_git_root, get_spath, mk_spath; print('ok')"
```

## Editable install (development)

```bash
git clone https://github.com/ywatanabe1989/scitex-path
cd scitex-path
pip install -e '.[dev]'
```

## Umbrella alternative

```bash
pip install scitex   # exposes scitex.path as a submodule
```

See SKILL.md for the standalone-vs-umbrella import rule.
