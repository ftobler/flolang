import pytest
from flolang.compiler import compiler_run
import os
import time


def test_compile_to_ast():
    t = time.time()
    compiler_run(["floc", "./tests/code/test_code.txt", "--emit", "ast"])
    assert os.path.getmtime("./tests/code/test_code.ast") > t


def test_compile_to_token():
    t = time.time()
    compiler_run(["floc", "./tests/code/test_code.txt", "--emit", "token"])
    assert os.path.getmtime("./tests/code/test_code.token") > t
