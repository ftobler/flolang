import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret


def run_file(file_path):
    with open(resolve_path(file_path), "r") as f:
        code = f.read()
        tok = tokenize(code)
        ast = parse(tok)
        env = default_environment()
        value = interpret(ast, env)
        print(value)


def test_code():
    run_file("test_code.txt")

def test_code_readme_example_1():
    run_file("test_code_readme_example_1.txt")

def test_code_readme_example_2():
    run_file("test_code_readme_example_2.txt")