import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval
import pytest, math, time


def test_dynamic_array_1():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = [1,2,3]
b[1]
""") == 2


def test_dynamic_array_2():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = [1,2,3]
b[1] = 100
b[1]
""") == 100


def test_dynamic_array_3():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = [1,2,3]
b[1] = b[0]
b[1]
""") == 1


def test_dynamic_array_4():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let int a = 1
let int b = 2
let int c = 3
let mut int array = [a,b,c]
array[1]
""") == 2


def test_dynamic_object_1():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert str(eval("""
let mut int b = {a: 1, b: 2}
b
""")) == "{'a': 1, 'b': 2}"


def test_dynamic_object_2():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b.a = 10
""") == 10


def test_dynamic_object_3():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b.a = 10
b.a
""") == 10


def test_dynamic_object_4():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b.a
""") == 1


def test_dynamic_object_5():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b.a = b.b
b.a
""") == 2


def test_dynamic_object_6():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b["a"] = 10
b["a"]
""") == 10


def test_dynamic_object_7():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b["a"]
""") == 1


def test_dynamic_object_8():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let mut int b = {a: 1, b: 2}
b["a"] = b["b"]
b["a"]
""") == 2


def test_dynamic_object_9():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let int a = 1
let int b = 2
let int c = 3
let mut int object = {a,b,c}
object.b
""") == 2