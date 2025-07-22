import pytest
from flolang.compiler import compiler_run
import os


def test_compile_to_ast(tmp_path):
    output_path = tmp_path / "file.ast"
    compiler_run(["floc", "./tests/code/test_code.txt", "--emit", "ast", "--output", output_path])
    assert os.path.isfile(output_path)
    with open(output_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        [print(s) for s in lines]
        assert len(lines) > 10


def test_compile_to_token(tmp_path):
    output_path = tmp_path / "file.token"
    compiler_run(["floc", "./tests/code/test_code.txt", "--emit", "token", "--output", output_path])
    assert os.path.isfile(output_path)
    with open(output_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        [print(s) for s in lines]
        assert len(lines) > 10
