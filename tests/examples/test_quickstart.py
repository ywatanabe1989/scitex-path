"""PS303 example mirror stub: ensure examples/quickstart.py is syntactically valid."""

import subprocess
import sys
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "quickstart.py"


def test_quickstart_example_file_compiles_without_syntax_errors():
    # Arrange
    example = EXAMPLE
    # Act
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(example)],
        capture_output=True,
    )
    # Assert
    assert proc.returncode == 0, (
        f"py_compile failed for {example}: "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )
