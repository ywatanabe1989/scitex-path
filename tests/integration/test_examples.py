"""Smoke test: every example script under examples/ runs to completion."""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(Path(__file__).resolve().parents[2].joinpath("examples").glob("*.py"))


def test_examples_directory_contains_at_least_one_script():
    # Arrange
    examples = EXAMPLES
    # Act
    count = len(examples)
    # Assert
    assert count > 0, "No example scripts found under examples/"


@pytest.mark.parametrize("example", EXAMPLES, ids=[p.name for p in EXAMPLES])
def test_example_script_runs_to_completion_with_zero_exit_code(example: Path, tmp_path):
    # Arrange
    cmd = [sys.executable, str(example)]
    # Act
    proc = subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Assert
    assert proc.returncode == 0, (
        f"{example.name} failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
