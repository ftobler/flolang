from flolang.interpreter import *
import pytest




def test_native_function_1():

    def callback(a):
        return a

    nf = NativeFunction(callback)

    assert str(nf) == "<native_function>"


def test_native_function_2():
    with pytest.raises(Exception):
        nf = NativeFunction("not a callback")











