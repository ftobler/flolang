import pytest
from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret



def test_alloc_1():
    assert len(tokenize("@alloc")) == 2


def test_alloc_2():
    assert len(tokenize("@alloc allocator_name")) == 3
