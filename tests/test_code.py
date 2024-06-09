import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret
import pytest

# run a script file per filename
def run_file(file_path):
    basename = os.path.basename(file_path)
    with open(resolve_path(file_path), "r") as f:
        code = f.read()
        tok = tokenize(code, filename=basename)
        ast = parse(tok)
        env = default_environment()
        value = interpret(ast, env)
        print(value)

# get a list of all script files to test
def get_test_files():
    directory = resolve_path("./code")
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(".txt")]

# TEST
# Generate test cases dynamically based on files found
@pytest.mark.parametrize("filename", get_test_files())
def test_file_automatic(filename):
    run_file(filename)

# TEST
# check that the function getting the script files is not broken
# this ensures that no tests are accidentally skipped
def test_get_test_files_testcase_works():
    assert len(get_test_files()) > 0