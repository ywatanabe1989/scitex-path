# Changelog

All notable changes to `scitex-path` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0]

- feat: port `title2path` from `scitex_gen._fs._title2path` (Phase B of
  the scitex-gen full retirement wave). New public symbol; the dict
  branch delegates lazily to `scitex_dict.to_str`.
- Note on `symlink`: scitex_gen carried a tiny `(tgt, src, force=False)`
  wrapper around `os.symlink`. The richer `scitex_path.symlink`
  (`(src, dst, overwrite=False, ..., relative=False)`) already covers
  every use case the legacy wrapper supported, and Phase A inventory
  found no consumer of the gen variant, so it is being dropped (not
  ported) in the scitex_gen retirement PR.

## [0.1.4]

- Initial CHANGELOG entry — see git log for prior history.
