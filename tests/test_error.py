import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret
from flolang.lexer import Symbols
import pytest

import flolang.error as err
import flolang.abstract_source_tree as ast
import flolang.lexer as lexer


def test_runtime_error_1():
    with pytest.raises(err.RuntimeException):
        err.runtime_error("comment")


def test_runtime_error_2():
    with pytest.raises(err.RuntimeException):
        tok = lexer.Token(Symbols("filename", 123, 2, "full_line"), "type", None)
        err.runtime_error("comment", ast.Location(tok, tok))


def test_runtime_error_3():
    # technically not specified to be allowed
    # but it works now, so want to see when it breaks
    with pytest.raises(err.RuntimeException):
        tok = lexer.Token(Symbols(None, 123, 2, None), None, None)
        err.runtime_error(None, ast.Location(tok, tok))


def test_runtime_error_4():
    # technically not specified to be allowed
    # but it works now, so want to see when it breaks
    with pytest.raises(err.RuntimeException):
        err.runtime_error(None, None)


def test_parser_error_1():
    with pytest.raises(err.ParserError):
        tok = lexer.Token(Symbols("filename", 123, 2, "full_line"), "type", None)
        err.parser_error("comment", tok, tok)


def test_parser_error_2():
    # technically not specified to be allowed
    # but it works now, so want to see when it breaks
    with pytest.raises(err.ParserError):
        tok = lexer.Token(Symbols(None, 123, 2, None), None, None)
        err.parser_error(None, tok, tok)


def test_error_token_1():
    with pytest.raises(err.TokenError):
        tok = lexer.Token(Symbols("filename", 123, 2, "full_line"), "type", None)
        err.error_token("comment", tok)


def test_error_token2():
    # technically not specified to be allowed
    # but it works now, so want to see when it breaks
    with pytest.raises(err.TokenError):
        tok = lexer.Token(Symbols(None, 123, 2, None), None, None)
        err.error_token(None, tok)


def test_error_symbol_1():
    with pytest.raises(err.TokenError):
        symbol = Symbols("filename", 123, 2, "full_line")
        err.error_symbol("comment", symbol)


def test_error_symbol_3():
    with pytest.raises(err.TokenError):
        symbol = Symbols(None, 123, 2, "full_line")
        err.error_symbol("comment", symbol)


def test_error_symbol_4():
    # technically not specified to be allowed
    # but it works now, so want to see when it breaks
    with pytest.raises(err.TokenError):
        symbol = Symbols(None, 123, 2, None)
        err.error_symbol(None, symbol)

