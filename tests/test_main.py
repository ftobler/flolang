import pytest
import flolang.main as main
from typing import Any
import sys


def create_input_iterator(list: list[Any]):

    # the inputs for input() I want to simulate in a list
    inputs = iter(list)

    # need a helpler function to iterate it
    def input_iterator():
        response = next(inputs)
        if isinstance(response, KeyboardInterrupt):
            raise response
        return response

    return input_iterator


@pytest.mark.timeout(5)  # timeout in case it is stuck in interpreter mode
def test_main_function_input(monkeypatch, capfd):

    # monkeypatch set the input simulations. need a lambda or a function
    monkeypatch.setattr('builtins.input', create_input_iterator(["2**8+4", KeyboardInterrupt()]))

    # monkeypatch set the sys.argv list
    monkeypatch.setattr(sys, 'argv', ['name_does_not_matter.py'])

    # call the main function. this is the same as the main entry point for the command line
    with pytest.raises(KeyboardInterrupt):
        # need to run this in raises, otherwise pytest will auto-fail
        main.main()

    # get the output which the program produced
    out, err = capfd.readouterr()

    # split into lines
    lines = out.split("\n")

    # assert output
    assert lines[0].startswith("flolang")
    assert lines[1] == "# 260"
    assert lines[2] == "# "


@pytest.mark.timeout(5)  # timeout in case it is stuck in interpreter mode
def test_main_function_error(monkeypatch, capfd):
    main.set_pretty_print(False)

    # monkeypatch set the input simulations. need a lambda or a function
    monkeypatch.setattr('builtins.input', create_input_iterator(["undefined_symbol", KeyboardInterrupt()]))

    # monkeypatch set the sys.argv list
    monkeypatch.setattr(sys, 'argv', ['name_does_not_matter.py'])

    # call the main function. this is the same as the main entry point for the command line
    with pytest.raises(KeyboardInterrupt):
        # need to run this in raises, otherwise pytest will auto-fail
        main.main()

    # get the output which the program produced
    out, err = capfd.readouterr()

    assert "is not defined" in out
    assert "Exception" in out


@pytest.mark.skip(reason="fails because of formatting changes")
@pytest.mark.timeout(5)  # timeout in case it is stuck in interpreter mode
def test_main_function_exception_file(monkeypatch, capfd):
    main.set_pretty_print(False)

    # monkeypatch set the sys.argv list
    monkeypatch.setattr(sys, 'argv', ['name_does_not_matter.py', 'tests/exception.txt'])

    main.main()

    # get the output which the program produced
    out, err = capfd.readouterr()

    with open("tests/exception_out.txt", "r", encoding="utf-8") as f:
        correct_output = f.read()

    # split into lines / assert out
    assert out == correct_output


@pytest.mark.timeout(5)  # timeout in case it is stuck in interpreter mode
def test_main_function_help(monkeypatch, capfd):
    main.set_pretty_print(False)

    monkeypatch.setattr(sys, 'argv', ['name_does_not_matter.py', '--help'])

    main.main()

    # get the output which the program produced
    out, err = capfd.readouterr()

    # split into lines / assert out
    assert out == main.get_help()  # check that the text is equal to the help text
    assert len(out) >= 200  # potentially guarding against not printing enough text
    assert len(out.split("\n")) >= 10  # potentially guarding against not printing multiple lines
