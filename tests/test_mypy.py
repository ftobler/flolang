import subprocess
import pytest


def test_mypy_flolang():
    """Runs mypy on all python files."""

    process = subprocess.run(["mypy", "flolang"], capture_output=True, text=True)

    if process.returncode != 0:
        pytest.fail(f"mypy found issues:\n{process.stdout}")


def test_mypy_tests():
    """Runs mypy on all python files."""

    process = subprocess.run(["mypy", "tests"], capture_output=True, text=True)

    if process.returncode != 0:
        pytest.fail(f"mypy found issues:\n{process.stdout}")
