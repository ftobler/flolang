import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval, eval_parse
import pytest
from flolang.lexer import potentially_reserved_keywords
from flolang.error import ParserError



@pytest.mark.parametrize("keyword", potentially_reserved_keywords)
def test_potentially_reserved_identifiers(keyword):
    # Expect '=' following type and identifier for 'let' declaration.
    with pytest.raises(ParserError):
        eval("let int %s = 0" % keyword)


def test_potentially_reserved_identifiers_valid_check():
    assert eval("let int i = 0") == 0

