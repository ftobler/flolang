import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval
from flolang.main import parse_arguments


def test_argument_parser_1a():
    argv = ["/path/to/flolang", "-switch", "command", "script", "script_argument"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch", "command")]
    assert args == ["script", "script_argument"]


def test_argument_parser_1b():
    argv = ["/path/to/flolang", "-switch", "command", "script"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch", "command")]
    assert args == ["script"]


def test_argument_parser_2a():
    argv = ["/path/to/flolang", "script", "script_argument"]
    switches, args = parse_arguments(argv)
    assert switches == []
    assert args == ["script", "script_argument"]


def test_argument_parser_2b():
    argv = ["/path/to/flolang", "script"]
    switches, args = parse_arguments(argv)
    assert switches == []
    assert args == ["script"]


def test_argument_parser_3():
    argv = ["/path/to/flolang", "-switch", "command"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch", "command")]
    assert args == []


def test_argument_parser_4a():
    argv = ["/path/to/flolang", "-switch1", "command1", "-switch2", "command2", "script", "script_argument"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch1", "command1"), ("switch2", "command2")]
    assert args == ["script", "script_argument"]


def test_argument_parser_4b():
    argv = ["/path/to/flolang", "-switch1", "command1", "-switch2", "command2", "script"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch1", "command1"), ("switch2", "command2")]
    assert args == ["script"]


def test_argument_parser_5():
    argv = ["/path/to/flolang", "-switch1", "command1", "-switch2", "command2"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch1", "command1"), ("switch2", "command2")]
    assert args == []


def test_argument_parser_6():
    argv = ["/path/to/flolang", "script", "script_argument"]
    switches, args = parse_arguments(argv)
    assert switches == []
    assert args == ["script", "script_argument"]


def test_argument_parser_6b():
    argv = ["/path/to/flolang", "script"]
    switches, args = parse_arguments(argv)
    assert switches == []
    assert args == ["script"]


def test_argument_parser_7a():
    argv = ["/path/to/flolang", "-switch", "command", "script", "-script_argument"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch", "command")]
    assert args == ["script", "-script_argument"]


def test_argument_parser_7b():
    argv = ["/path/to/flolang", "-switch", "command", "script", "-script_argument1", "-script_argument2"]
    switches, args = parse_arguments(argv)
    assert switches == [("switch", "command")]
    assert args == ["script", "-script_argument1", "-script_argument2"]


def test_argument_parser_8a():
    argv = ["/path/to/flolang", "script", "-script_argument"]
    switches, args = parse_arguments(argv)
    assert switches == []
    assert args == ["script", "-script_argument"]


def test_argument_parser_8b():
    argv = ["/path/to/flolang", "script", "-script_argument1", "-script_argument2"]
    switches, args = parse_arguments(argv)
    assert switches == []
    assert args == ["script", "-script_argument1", "-script_argument2"]