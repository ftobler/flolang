import subprocess
import pytest


flake8_ignores = ["F401", "F403"]
ignore = " ".join([f"--ignore={code}" for code in flake8_ignores])


def test_flake8_flolang():
    """Runs flake8 on all python files."""

    process = subprocess.run(["flake8", ignore, "flolang"], capture_output=True, text=True)

    if process.returncode != 0:
        pytest.fail(f"flake8 found issues:\n{process.stdout}")


def test_flake8_tests():
    """Runs flake8 on all python files."""

    process = subprocess.run(["flake8", ignore, "tests"], capture_output=True, text=True)

    if process.returncode != 0:
        pytest.fail(f"flake8 found issues:\n{process.stdout}")
