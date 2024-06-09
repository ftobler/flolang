import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret
import pytest


def test_alloc_1():
    assert len(tokenize("@alloc")) == 2

def test_alloc_2():
    assert len(tokenize("@alloc allocator_name")) == 3

