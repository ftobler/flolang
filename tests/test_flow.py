import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval
import pytest

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

def test_function_variable_scope():
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

def test_condition_if():
    # check an if which is branching
    assert eval("""
let int i = 0
if True:
    i = 1
i
""") == 1

    # check an if which is skipping
    assert eval("""
let int i = 0
if False:
    i = 1
i
""") == 0

def test_condition_if_else():
    # check an if-else which is iffing
    assert eval("""
let int i = 0
if True:
    i = 1
else:
    i = 2
i
""") == 1

    # check an if-else which is elseing
    assert eval("""
let int i = 0
if False:
    i = 1
else:
    i = 2
i
""") == 2


def test_condition_if_elif_else():
    # check an if-elif-else which is ifing
    assert eval("""
let int i = 0
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
let int i = 0
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
let int i = 0
if False:
    i = 1
elif False:
    i = 2
else:
    i = 3
i
""") == 3

def test_condition_if_elif():
    # check an if-elif which is ifing
    assert eval("""
let int i = 0
if True:
    i = 1
elif True:
    i = 2
i
""") == 1

    # check an if-elif-else which is elifing
    assert eval("""
let int i = 0
if False:
    i = 1
elif True:
    i = 2
i
""") == 2

    # check an if-elif-else which is skipping
    assert eval("""
let int i = 0
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
let int i = 10
while --i:
    pass
i
""") == 0

    # check a simple while loop
    # expect 9 loops
    assert eval("""
let int i = 10
let int n = 0
while --i:
    n++
n
""") == 9


    # check a simple while loop with pass
    # pass is not allowed after a statement
    with pytest.raises(Exception):
        assert eval("""
let int i = 10
let int n = 0
while --i:
    n++
    pass
n # this 'n' is an extra statement after the block
    """) == 10

    # check a simple while loop with pass
    # pass is not allowed after a statement
    with pytest.raises(Exception):
        assert eval("""
let int i = 10
let int n = 0
while --i:
    n++
    pass
    """) == 10

#     # check a simple while loop with break
#     # expect 5 loops
#     assert eval("""
# let int i = 10
# let int n = 0
# while --i:
#     if i < 5:
#         break
# n
# """) == 5

    # check a simple while loop with break
    # the check decrement has been executed once
    assert eval("""
let int i = 10
while i--:
    break
i
""") == 9

    # check a simple while loop with break
    assert eval("""
let int i = 10
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
let int a = 123
if True:
    let int a = 456
a
""") == 123

    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let int a = 123
let int b = 0
if True:
    let int a = 456
    b = a
b
""") == 456

def test_function_nesting():
    assert eval("""
fn foo(int a):
    return a * 10
fn bar(int a):
    return a * 2
foo(bar(100))
""") == 2000

    assert eval("""
fn foo():
    return bar
fn bar(int add):
    return 100 + add
foo()(20)
""") == 120

@pytest.mark.skip(reason="not yet implemented correctly")
def test_return_break_statements():
    # check a simple while loop with break
    # expect 5 loops
    assert eval("""
let int i = 10
while --i:
    if i <= 5:
        break
i
""") == 5

    # check a simple while loop with return
    # expect 5 loops
    assert eval("""
let int i = 10
while --i:
    if i <= 5:
        return
i
""") == 5

@pytest.mark.skip(reason="not yet implemented correctly")
def test_return_break_statements2():
    # check a simple while loop with return
    # expect 5 loops
    assert eval("""
fn foo():
    if True:
        return "success"
    return "failed"
foo()
""") == "success"

@pytest.mark.skip(reason="not yet implemented correctly")
def test_for_loop():
    assert eval("""
let int n = 0
for int i in 0..50:
    n++
n
""") == 49

    assert eval("""
let int n = 0
for int i in 50:
    n++
n
""") == 49