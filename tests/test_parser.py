import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret
import pytest

def parseeval(code: str):
    tok = tokenize(code)
    ast = parse(tok)
    return ast

def test_alloc_1():
    with pytest.raises(Exception):
        parseeval("@alloc")

def test_alloc_2():
    parseeval("@alloc identifier")




