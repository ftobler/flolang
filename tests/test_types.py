import pytest
from flolang.interpreter import NativeFunction


def test_native_function_1():

    def callback(a):
        return a

    nf = NativeFunction(callback)

    assert str(nf) == "<native_function>"


def test_native_function_2():
    with pytest.raises(Exception):
        NativeFunction("not a callback")











