import pytest
from flolang.compiler import compiler_run, file_ending
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


def test_file_ending_1():
    assert file_ending("file", ".txt") == "file.txt"


def test_file_ending_2():
    assert file_ending("file.txt", ".txt") == "file.txt"


def test_file_ending_3():
    assert file_ending("file.out", ".txt") == "file.out.txt"


def test_file_ending_4():
    assert file_ending(".file", ".txt") == ".file.txt"


def test_file_ending_5():
    assert file_ending(".txt", ".txt") == ".txt.txt"


def test_file_ending_():
    assert file_ending("txt", ".txt") == "txt.txt"
