import pytest
from flolang.argument_parser import ArgumentParser
from typing import NamedTuple, Any


class Mutation(NamedTuple):
    valid: bool
    data: Any


mutate_switches = [
    Mutation(True, []),
    Mutation(True, ["sw_first"]),
    Mutation(True, ["sw_first", "sw_second"]),
    Mutation(True, ["sw_first", "sw_second", "sw_third"]),
]

mutate_arguments = [
    Mutation(True, []),
    Mutation(True, ["arg_first"]),
    Mutation(True, ["arg_first", "arg_second"]),
    Mutation(True, ["arg_first", "arg_second", "arg_third"]),
    Mutation(False, ["--notanargument"]),
]

mutate_keyvalues = [
    Mutation(True, {}),
    Mutation(True, {"key_first": "value_first"}),
    Mutation(True, {"key_first": "value_first", "key_second": "value_second"}),
    Mutation(False, {"key_first": None}),
    Mutation(False, {"--key_first": "value_first"}),
    Mutation(False, {"key_first": "key_first"}),
]


@pytest.mark.parametrize("switches", mutate_switches)
@pytest.mark.parametrize("args", mutate_arguments)
@pytest.mark.parametrize("keyvalues", mutate_keyvalues)
def test_argument_parser_auto_exact(switches, args, keyvalues):
    argv = ["/path/to/flolang"] + [f"--{s}" for s in switches.data] + args.data
    for k, v in keyvalues.data.items():
        argv.append(f"--{k}")
        if v is not None:
            argv.append(v)

    if switches.valid and args.valid and keyvalues.valid:
        keys = list(keyvalues.data.keys())

        ap = ArgumentParser(argv, switches.data, keys)
        assert ap.switches() == switches.data
        assert ap.args() == args.data
        assert ap.keyvalues() == keyvalues.data
        for s in switches.data:
            assert ap.switch(s) is True
        for k in keys:
            assert ap.key(k) == keyvalues.data[k]
        for a in args.data:
            assert a in ap.args()

    else:
        with pytest.raises((ValueError, IndexError)):
            ArgumentParser(argv)


def test_argument_parser_1a():
    argv = ["/path/to/flolang", "--switch", "script", "script_argument"]
    ap = ArgumentParser(argv, ["switch"])
    assert ap.switches() == ["switch"]
    assert ap.args() == ["script", "script_argument"]
    assert ap.switch("switch") is True
    assert ap.switch("nonincluded") is False


def test_argument_parser_1b():
    argv = ["/path/to/flolang", "--switch", "script"]
    ap = ArgumentParser(argv, ["switch"])
    assert ap.switches() == ["switch"]
    assert ap.args() == ["script"]
    assert ap.switch("switch") is True
    assert ap.switch("nonincluded") is False


def test_argument_parser_1c():
    argv = ["/path/to/flolang", "--switch", "script"]
    ap = ArgumentParser(argv, ["switch", "alternative"])
    assert ap.switches() == ["switch"]
    assert ap.args() == ["script"]
    assert ap.switch("switch") is True
    assert ap.switch("nonincluded") is False
    assert ap.switch("alternative") is False


def test_argument_parser_1d():
    argv = ["/path/to/flolang", "--switch", "--alternative", "script"]
    with pytest.raises(ValueError):
        ArgumentParser(argv, ["switch"])


def test_argument_parser_2a0():
    argv = ["/path/to/flolang", "script", "script_argument"]
    ap = ArgumentParser(argv, [])
    assert ap.switches() == []
    assert ap.args() == ["script", "script_argument"]
    assert ap.switch("switch") is False
    assert ap.switch("alternative") is False


def test_argument_parser_2a1():
    argv = ["/path/to/flolang", "script", "script_argument"]
    ap = ArgumentParser(argv, ["switch"])
    assert ap.switches() == []
    assert ap.args() == ["script", "script_argument"]
    assert ap.switch("switch") is False
    assert ap.switch("alternative") is False


def test_argument_parser_2a2():
    argv = ["/path/to/flolang", "script", "script_argument"]
    ap = ArgumentParser(argv, ["switch", "alternative"])
    assert ap.switches() == []
    assert ap.args() == ["script", "script_argument"]
    assert ap.switch("switch") is False
    assert ap.switch("alternative") is False


def test_argument_parser_2b0():
    argv = ["/path/to/flolang", "script"]
    ap = ArgumentParser(argv, [])
    assert ap.switches() == []
    assert ap.args() == ["script"]
    assert ap.switch("switch") is False
    assert ap.switch("alternative") is False


def test_argument_parser_2b1():
    argv = ["/path/to/flolang", "script"]
    ap = ArgumentParser(argv, ["switch"])
    assert ap.switches() == []
    assert ap.args() == ["script"]
    assert ap.switch("switch") is False
    assert ap.switch("alternative") is False


def test_argument_parser_2b2():
    argv = ["/path/to/flolang", "script"]
    ap = ArgumentParser(argv, ["switch", "alternative"])
    assert ap.switches() == []
    assert ap.args() == ["script"]
    assert ap.switch("switch") is False
    assert ap.switch("alternative") is False


def test_argument_parser_3_0():
    argv = ["/path/to/flolang", "--switch"]
    with pytest.raises(ValueError):
        ArgumentParser(argv, [])


def test_argument_parser_3_1():
    argv = ["/path/to/flolang", "--switch"]
    ap = ArgumentParser(argv, ["switch"])
    assert ap.switches() == ["switch"]
    assert ap.args() == []
    assert ap.switch("switch") is True
    assert ap.switch("alternative") is False


def test_argument_parser_3_2():
    argv = ["/path/to/flolang", "--switch"]
    ap = ArgumentParser(argv, ["switch", "alternative"])
    assert ap.switches() == ["switch"]
    assert ap.args() == []
    assert ap.switch("switch") is True
    assert ap.switch("alternative") is False


# def test_argument_parser_4a():
#     argv = ["/path/to/flolang", "--switch1", "--switch2", "script", "script_argument"]
#     switches, args = parse_arguments(argv)
#     assert switches == ["--switch1", "--switch2"]
#     assert args == ["script", "script_argument"]


# def test_argument_parser_4b():
#     argv = ["/path/to/flolang", "--switch1", "--switch2", "script"]
#     switches, args = parse_arguments(argv)
#     assert switches == ["--switch1", "--switch2"]
#     assert args == ["script"]


# def test_argument_parser_5():
#     argv = ["/path/to/flolang", "--switch1", "--switch2"]
#     switches, args = parse_arguments(argv)
#     assert switches == ["--switch1", "--switch2"]
#     assert args == []


# def test_argument_parser_6():
#     argv = ["/path/to/flolang", "script", "script_argument"]
#     switches, args = parse_arguments(argv)
#     assert switches == []
#     assert args == ["script", "script_argument"]


# def test_argument_parser_6b():
#     argv = ["/path/to/flolang", "script"]
#     switches, args = parse_arguments(argv)
#     assert switches == []
#     assert args == ["script"]


# def test_argument_parser_7a():
#     argv = ["/path/to/flolang", "--switch", "script", "-script_argument"]
#     switches, args = parse_arguments(argv)
#     assert switches == ["--switch"]
#     assert args == ["script", "-script_argument"]


# def test_argument_parser_7b():
#     argv = ["/path/to/flolang", "--switch", "script", "-script_argument1", "-script_argument2"]
#     switches, args = parse_arguments(argv)
#     assert switches == ["--switch"]
#     assert args == ["script", "-script_argument1", "-script_argument2"]


# def test_argument_parser_8a():
#     argv = ["/path/to/flolang", "script", "-script_argument"]
#     switches, args = parse_arguments(argv)
#     assert switches == []
#     assert args == ["script", "-script_argument"]


# def test_argument_parser_8b():
#     argv = ["/path/to/flolang", "script", "-script_argument1", "-script_argument2"]
#     switches, args = parse_arguments(argv)
#     assert switches == []
#     assert args == ["script", "-script_argument1", "-script_argument2"]
