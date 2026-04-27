"""scitex-path quickstart: filesystem path utilities."""

import tempfile
from pathlib import Path

import scitex_path


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        # 1. split — split a path into (dir, basename, ext).
        head, base, ext = scitex_path.split("/tmp/foo/bar.txt")
        print("split:", head, base, ext)
        assert ext == ".txt"

        # 2. clean — normalize a path string.
        cleaned = scitex_path.clean("/tmp//foo/./bar")
        print("clean:", cleaned)

        # 3. getsize — bytes for a file.
        f = td / "data.bin"
        f.write_bytes(b"\0" * 1024)
        print("getsize:", scitex_path.getsize(str(f)))
        assert scitex_path.getsize(str(f)) == 1024

        # 4. find_file / find_dir — recursive locator.
        sub = td / "sub"
        sub.mkdir()
        target = sub / "needle.txt"
        target.write_text("x")
        hits = scitex_path.find_file(str(td), "needle.txt")
        print("find_file hits:", hits)
        assert any("needle.txt" in h for h in hits)


if __name__ == "__main__":
    main()
