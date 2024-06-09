import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret
import pytest


def read_file(file_path):
    with open(resolve_path(file_path)) as f:
        return f.read()


def check_file_is_containted_in_file(child, container, prefix='```python\n', suffix='\n```'):
    assert read_file(container).index(prefix + read_file(child) + suffix) >= 0  # means file is contained in README.md


def test_script_is_in_readme_1():
    check_file_is_containted_in_file("./code/test_code_readme_example_1.txt", "../README.md")


def test_script_is_in_readme_2():
    check_file_is_containted_in_file("./code/test_code_readme_example_2.txt", "../README.md")
