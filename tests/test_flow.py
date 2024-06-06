import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native
import pytest

def eval(expression: str, env=None):
    tok = tokenize(expression)
    ast = parse(tok)
    if not env:
        env = default_environment()
    val = interpret(ast, env)
    return to_native(val)

def test_function():

    with pytest.raises(Exception):
        x = 1 / 0

    # declare a function
    assert eval("""
fn foo():
    return 1234
""") == "<RuntimeFunction>" #not liking the result, but its for now what is coming out here

    # funtion with returntype
    assert eval("""
fn foo() int:
    return 1234
foo()
""") == 1234

    # function with no return type
    assert eval("""
fn foo():
    return
foo()
""") == None

    # simple additive function
    assert eval("""
fn add(int a, int b):
    return a + b
add(5, 3)
""") == 8

    # check that A argument is really A
    assert eval("""
fn returnA(int a, int b):
    return a
returnA(5, 3)
""") == 5

    # check that B argument is really B
    assert eval("""
fn returnB(int a, int b):
    return b
returnB(5, 3)
""") == 3

    # check nesting function calls
    assert eval("""
fn bar():
    return 456
fn foo():
    return bar()
bar()
""") == 456

    # check that the order of declaration does not matter
    assert eval("""
foo()
fn foo():
    return global_var
const int global_var = 789
""") == 789

    # put a function on a variable
    assert eval("""
fn foo():
    return 963
const int bar = foo
bar()
""") == 963

def test_condition():
    # check an if which is branching
    assert eval("""
var int i = 0
if True:
    i = 1
i
""") == 1

    # check an if which is skipping
    assert eval("""
var int i = 0
if False:
    i = 1
i
""") == 0

    # check an if-else which is iffing
    assert eval("""
var int i = 0
if True:
    i = 1
else:
    i = 2
i
""") == 1

    # check an if-else which is elseing
    assert eval("""
var int i = 0
if False:
    i = 1
else:
    i = 2
i
""") == 2

    # check an if-elif-else which is ifing
    assert eval("""
var int i = 0
if True:
    i = 1
elif False:
    i = 2
else:
    i = 3
i
""") == 1

    # check an if-elif-else which is elifing
    assert eval("""
var int i = 0
if False:
    i = 1
elif True:
    i = 2
else:
    i = 3
i
""") == 2

    # check an if-elif-else which is elseing
    assert eval("""
var int i = 0
if False:
    i = 1
elif False:
    i = 2
else:
    i = 3
i
""") == 3

    # check an if-elif which is ifing
    assert eval("""
var int i = 0
if True:
    i = 1
elif True:
    i = 2
i
""") == 1

    # check an if-elif-else which is elifing
    assert eval("""
var int i = 0
if False:
    i = 1
elif True:
    i = 2
i
""") == 2

    # check an if-elif-else which is skipping
    assert eval("""
var int i = 0
if False:
    i = 1
elif False:
    i = 2
i
""") == 0

def test_while():

    # check a simple while loop with pass
    # expect count to 0
    assert eval("""
var int i = 10
while --i:
    pass
i
""") == 0

    # check a simple while loop
    # expect 9 loops
    assert eval("""
var int i = 10
var int n = 0
while --i:
    n++
n
""") == 9


    # check a simple while loop with pass
    # pass is not allowed after a statement
    with pytest.raises(Exception):
        assert eval("""
var int i = 10
var int n = 0
while --i:
    n++
    pass
n # this 'n' is an extra statement after the block
    """) == 10

    # check a simple while loop with pass
    # pass is not allowed after a statement
    with pytest.raises(Exception):
        assert eval("""
var int i = 10
var int n = 0
while --i:
    n++
    pass
    """) == 10

#     # check a simple while loop with break
#     # expect 5 loops
#     assert eval("""
# var int i = 10
# var int n = 0
# while --i:
#     if i < 5:
#         break
# n
# """) == 5

    # check a simple while loop with break
    # the check decrement has been executed once
    assert eval("""
var int i = 10
while i--:
    break
i
""") == 9

    # check a simple while loop with break
    assert eval("""
var int i = 10
while i:
    i--
i
""") == 0

def test_unreachable_code():
    #unreachable keyword is never reached
    assert eval("""
if False:
    unreachable
""") == None

    # unreachable is used to assert that control flow will never reach a
    # particular location (1:1 what they state in zig)
    assert eval("""
const int x = 1
const int y = 2
if x + y != 3:
    unreachable
""") == None

    # unreachable at runtime creates an exception
    with pytest.raises(Exception):
        assert eval("""
unreachable
""") == None

def test_scopes():
    # if block has its own scope and does not change base variable
    assert eval("""
var int a = 123
if True:
    var int a = 456
a
""") == 123

    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
var int a = 123
var int b = 0
if True:
    var int a = 456
    b = a
b
""") == 456