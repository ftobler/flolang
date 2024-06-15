import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval
import pytest


def test_function_0():

    with pytest.raises(Exception):
        x = 1 / 0


def test_function_1():
    # declare a function
    assert eval("""
fn foo():
    return 1234
""") == "<RuntimeFunction>"  # not liking the result, but its for now what is coming out here


def test_function_2():
    # funtion with returntype
    assert eval("""
fn foo() int:
    return 1234
foo()
""") == 1234


def test_function_3():
    # function with no return type
    assert eval("""
fn foo():
    return
foo()
""") == None


def test_function_4():
    # simple additive function
    assert eval("""
fn add(int a, int b):
    return a + b
add(5, 3)
""") == 8


def test_function_5():
    # check that A argument is really A
    assert eval("""
fn returnA(int a, int b):
    return a
returnA(5, 3)
""") == 5


def test_function_6():
    # check that B argument is really B
    assert eval("""
fn returnB(int a, int b):
    return b
returnB(5, 3)
""") == 3


def test_function_7():
    # check nesting function calls
    assert eval("""
fn bar():
    return 456
fn foo():
    return bar()
bar()
""") == 456


def test_function_8():
    # check nesting function calls
    with pytest.raises(Exception):
        eval("""
let foo = 0
foo()
""")


def test_function_variable_scope_1():
    # check that the order of declaration does not matter
    assert eval("""
foo()
fn foo():
    return global_var
let int global_var = 789
""") == 789


def test_function_variable_scope_2():
    # put a function on a variable
    assert eval("""
fn foo():
    return 963
let bar = foo
bar()
""") == 963


def test_condition_if_1():
    # check an if which is branching
    assert eval("""
let mut int i = 0
if True:
    i = 1
i
""") == 1


def test_condition_if_2():
    # check an if which is skipping
    assert eval("""
let int i = 0
if False:
    i = 1
i
""") == 0


def test_condition_if_else_1():
    # check an if-else which is iffing
    assert eval("""
let mut int i = 0
if True:
    i = 1
else:
    i = 2
i
""") == 1


def test_condition_if_else_2():
    # check an if-else which is elseing
    assert eval("""
let mut int i = 0
if False:
    i = 1
else:
    i = 2
i
""") == 2



def test_condition_if_elif_else_1():
    # check an if-elif-else which is ifing
    assert eval("""
let mut int i = 0
if True:
    i = 1
elif False:
    i = 2
else:
    i = 3
i
""") == 1


def test_condition_if_elif_else_2():
    # check an if-elif-else which is elifing
    assert eval("""
let mut int i = 0
if False:
    i = 1
elif True:
    i = 2
else:
    i = 3
i
""") == 2


def test_condition_if_elif_else_3():
    # check an if-elif-else which is elseing
    assert eval("""
let mut int i = 0
if False:
    i = 1
elif False:
    i = 2
else:
    i = 3
i
""") == 3


def test_condition_if_elif_1():
    # check an if-elif which is ifing
    assert eval("""
let mut int i = 0
if True:
    i = 1
elif True:
    i = 2
i
""") == 1


def test_condition_if_elif_2():
    # check an if-elif-else which is elifing
    assert eval("""
let mut int i = 0
if False:
    i = 1
elif True:
    i = 2
i
""") == 2


def test_condition_if_elif_3():
    # check an if-elif-else which is skipping
    assert eval("""
let int i = 0
if False:
    i = 1
elif False:
    i = 2
i
""") == 0

def test_condition_very_long_block_1():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this PASSED
    assert eval("""
let int i = 0
if False          :
    i = 1
elif               False :
    i = 2
i
""") == 0

def test_condition_very_long_block_2():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this PASSED
    assert eval("""
let int i = 0
if False:
    i = 123456789
elif False :
    i = 123456789
i
""") == 0

def test_condition_very_long_block_3():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this PASSED
    assert eval("""
let int i = 0
if False:
    print("very very many")
    i = 123456789
elif False :
    print("lines of code")
    i = 123456789
i
""") == 0

def test_condition_very_long_block_4():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this PASSED
    assert eval("""
let int i = 0
if False       :
    print("very very many")
    i = 123456789
elif False:
    print("lines of code")
    i = 123456789

i
""") == 0

def test_condition_very_long_block_5():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this FAILED
    assert eval("""
let int i = 0
if False       :
    print("very very many")
    i = -1
elif False:
    print("lines of code")
    i = 123456789

i
""") == 0

def test_condition_very_long_block_6():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this FAILED
    assert eval("""
let int i = 0
if False       :
    print("very very many")
    i = 123456789
elif False:
    print("lines of code")
    i = -1

i
""") == 0

def test_condition_very_long_block_7():
    # got once strange behaviour when the lines before or after a block
    # had length corresponding or not to the block
    # type was the 'Location' could not __repr__ to string
    # => this FAILED
    assert eval("""
let int i = 0
if False       :
    print("very very many")
    i = -1
elif False:
    print("lines of code")
    i = -1

i
""") == 0


def test_condition_if_inline_statement_1():
    assert eval("""
let mut int i = 123
if True: i = 456
i
""") == 456


def test_condition_if_inline_statement_2():
    assert eval("""
let mut int i = 123
if False: i = 456
i
""") == 123


def test_condition_if_inline_statement_3():
    assert eval("""
let mut int i = 123
if True: i = 456 else: i = 789
i
""") == 456


def test_condition_if_inline_statement_4():
    assert eval("""
let mut int i = 123
if False: i = 456 else: i = 789
i
""") == 789


def test_condition_if_inline_statement_5():
    assert eval("""
let mut int i = 123
if True: i = 456 else:
    i = 789
i
""") == 456


def test_condition_if_inline_statement_6():
    assert eval("""
let mut int i = 123
if False: i = 456 else:
    i = 789
i
""") == 789


def test_condition_if_inline_statement_7():
    assert eval("""
let mut int i = 123
if True:
    i = 456
else: i = 789
i
""") == 456


def test_condition_if_inline_statement_8():
    assert eval("""
let mut int i = 123
if False:
    i = 456
else: i = 789
i
""") == 789


def test_condition_if_inline_statement_9():
    with pytest.raises(Exception):
        eval("""
let int i = 123
if True:
    i = 456 else:
    i = 789
i
""") == 789


def test_condition_if_inline_statement_10():
    with pytest.raises(Exception):
        eval("""
let int i = 123
if False:
    i = 456 else:
    i = 789
i
""") == 456


def test_while_1():
    # check a simple while loop with pass
    # expect count to 0
    assert eval("""
let mut int i = 10
while --i:
    pass
i
""") == 0


def test_while_2():
    # check a simple while loop
    # expect 9 loops
    assert eval("""
let mut int i = 10
let mut int n = 0
while --i:
    n++
n
""") == 9


def test_while_3():
    # check a simple while loop with pass
    # pass is not allowed after a statement
    with pytest.raises(Exception):
        eval("""
let int i = 10
let int n = 0
while --i:
    n++
    pass
n # this 'n' is an extra statement after the block
    """) == 10


def test_while_4():
    # check a simple while loop with pass
    # pass is not allowed after a statement
    with pytest.raises(Exception):
        eval("""
let int i = 10
let int n = 0
while --i:
    n++
    pass
    """) == 10


def test_while_5():
    # check a simple while loop with break
    # expect 5 loops
    assert eval("""
let mut int i = 10
let mut int n = 0
while --i:
    if i < 5:
        break
    n++
n
""") == 5


def test_while_6():
    # check a simple while loop with break
    # the check decrement has been executed once
    assert eval("""
let mut int i = 10
while i--:
    break
i
""") == 9


def test_while_7():
    # check a simple while loop with break
    assert eval("""
let mut int i = 10
while i:
    i--
i
""") == 0


def test_unreachable_code_1():
    #unreachable keyword is never reached
    assert eval("""
if False:
    unreachable
""") == None


def test_unreachable_code_2():
    # unreachable is used to assert that control flow will never reach a
    # particular location (1:1 what they state in zig)
    assert eval("""
let int x = 1
let int y = 2
if x + y != 3:
    unreachable
""") == None


def test_unreachable_code_3():
    # unreachable at runtime creates an exception
    with pytest.raises(Exception):
        eval("""
unreachable
""") == None


def test_scopes_1():
    # if block has its own scope and does not change base variable
    assert eval("""
let int a = 123
if True:
    let int a = 456
a
""") == 123


def test_scopes_2():
    # if block has its own scope and in itself the new variable is used
    # on assignment
    assert eval("""
let int a = 123
let mut int b = 0
if True:
    let int a = 456
    b = a
b
""") == 456


def test_function_nesting_1():
    assert eval("""
fn foo(int a):
    return a * 10
fn bar(int a):
    return a * 2
foo(bar(100))
""") == 2000


def test_function_nesting_2():
    assert eval("""
fn foo():
    return bar
fn bar(int add):
    return 100 + add
foo()(20)
""") == 120


def test_function_with_comments_and_spaces_1():
    assert eval("""
fn foo():
    return 52
foo()
""") == 52


def test_function_with_comments_and_spaces_2():
    assert eval("""
fn foo():

    return 53
foo()
""") == 53


def test_function_with_comments_and_spaces_3():
    assert eval("""
fn foo():
    # return a value
    return 54
foo()
""") == 54


def test_function_with_comments_and_spaces_4():
    assert eval("""
fn foo():

    # return a value
    return 55
foo()
""") == 55


def test_function_with_comments_and_spaces_5():
    assert eval("""
fn foo():
    let int i = 5

    # return a value

    return 56
foo()
""") == 56


def test_function_with_comments_and_spaces_6():
    assert eval("""
fn foo():
    let int i = 5
    # comment 1
    # comment 2
    return 57
foo()
""") == 57




def test_return_break_statements_1():
    # check a simple while loop with break
    # expect 5 loops
    assert eval("""
let mut int i = 10
while --i:
    if i <= 5:
        break
i
""") == 5


def test_return_break_statements_2a():
    # check a simple while loop with return
    # expect 5 loops
    assert eval("""
fn function_for_return_test():
    let mut int i = 10
    while --i:
        if i <= 5:
            return i
    i
function_for_return_test()
""") == 5


def test_return_break_statements_2b():
    # return is not allowed because it is not a function
    with pytest.raises(Exception):
        eval("""
    let mut int i = 10
    while --i:
        if i <= 5:
            return # not allowed outside function
    i
    """) == 5


def test_return_break_statements_3():
    # check a simple while loop with return
    # expect 5 loops
    assert eval("""
fn foo():
    if True:
        return "success"
    return "failed"
foo()
""") == "success"


def test_return_break_statements_4a():
    # simple test case, but can go wrong when 'break' state does propagation handling
    # is bugged.
    # got exception here at one point:
    # "Expression 'break' is not allowed outside loop.", loc = "foo()"
    assert eval("""
fn foo():
    while True:
        break
foo()
""") == None


def test_return_break_statements_4b():
    # simple test case, but can go wrong when 'break' state does propagation handling
    # is bugged.
    # got exception here at one point:
    # "Expression 'break' is not allowed outside loop.", loc = "foo()"
    assert eval("""
fn foo():
    while True:
        break
    return "this"
foo()
""") == "this"


def test_return_break_statements_5():
    # simple test cases , but can go wrong when 'break' state does propagation handling
    # is bugged
    assert eval("""
fn foo():
    while True:
        return
foo()
""") == None


def test_return_break_statements_6():
    assert eval("""
fn foo():
    while True:
        break
    while True:
        return "success"
    return "failure"
foo()
""") == "success"


def test_return_break_statements_7():
    assert eval("""
fn foo():
    while True:
        return "first"
    while True:
        return "success"
    return "failure"
foo()
""") == "first"


def test_return_break_statements_8():
    assert eval("""
fn foo():
    while True:
        while True:
            return "first"
        return "not this"
foo()
""") == "first"


def test_return_break_statements_9():
    assert eval("""
fn foo():
    while True:
        while True:
            return "first"
        return "not this"
foo()
""") == "first"


def test_return_break_statements_10():
    assert eval("""
fn foo():
    while True:
        while True:
            break
        return "here"
foo()
""") == "here"


def test_return_break_statements_11():
    assert eval("""
fn foo():
    while True:
        if True:
            break
        return "not reached"
    return "at last"
foo()
""") == "at last"


def test_return_break_statements_12():
    assert eval("""
fn foo():
    while True:
        if True:
            break
        return "not reached"
    return "broken outward here"
foo()
""") == "broken outward here"


def test_return_break_statements_13():
    assert eval("""
fn foo():
    while True:
        while True:
            if True:
                break
            return "not reached"
        return "broken outward here"
    return "not this"
foo()
""") == "broken outward here"


def test_return_break_statements_14():
    assert eval("""
fn foo():
    while True:
        if True:
            return "this one"
        return "not this"
    return "not this either"
foo()
""") == "this one"


def test_return_in_while_loop():
    # Test Case 1: Testing return in a while loop
    assert eval("""
fn foo():
    while True:
        return "returned"
foo()
""") == "returned"


def test_break_in_while_loop():
    # Test Case 2: Testing break in a while loop
    assert eval("""
fn foo():
    while True:
        break
    return "loop exited"
foo()
""") == "loop exited"


def test_continue_in_while_loop():
    # Test Case 3: Testing continue in a while loop
    assert eval("""
fn foo():
    let mut int i = 0
    while i < 5:
        i += 1
        if i < 3:
            continue
        return i
foo()
""") == 3


def test_break_and_continue_in_while_loop():
    # Test Case 4: Combining break and continue in a while loop
    assert eval("""
fn foo():
    let mut int i = 0
    while i < 5:
        i += 1
        if i == 2:
            continue
        if i == 4:
            break
    return i
foo()
""") == 4


def test_nested_while_loops():
    # Test Case 5: Nested while loops with return, break, and continue
    assert eval("""
fn foo():
    let mut int outer = 0
    while outer < 3:
        let mut int inner = 0
        while inner < 3:
            inner += 1
            if inner == 2:
                continue
            if inner == 3:
                break
        outer += 1
        if outer == 2:
            return outer
foo()
""") == 2


def test_multiple_loops():
    # Comprehensive Test Case: Multiple Loops with return, break, and continue
    assert eval("""
fn foo():
    let mut int outer_count = 0
    while outer_count < 3:
        let mut int middle_count = 0
        let mut int inner_count = 0
        while middle_count < 3:
            inner_count = 0
            while inner_count < 3:
                inner_count += 1
                if inner_count == 2:
                    continue  # Skip the rest of the loop for this iteration
                if inner_count == 3:
                    break  # Exit the inner loop
            middle_count += 1
            if middle_count == 2:
                break  # Exit the middle loop
        outer_count += 1
        if outer_count == 2:
            return outer_count == 2 and middle_count == 2 and inner_count == 3
foo()
""") == True


def test_multiple_loops_with_recursion():
    # Comprehensive Test Case: Multiple Loops with Recursion
    assert eval("""
fn recursive_function(int level):
    if level == 0:
        return "base case reached"
    else:
        let mut int outer_count = 0
        while outer_count < 3:
            let mut int middle_count = 0
            while middle_count < 3:
                let mut int inner_count = 0
                while inner_count < 3:
                    inner_count += 1
                    if inner_count == 2:
                        continue  # Skip the rest of the loop for this iteration
                    if inner_count == 3:
                        break  # Exit the inner loop
                middle_count += 1
                if middle_count == 2:
                    break  # Exit the middle loop
            outer_count += 1
            if outer_count == 2:
                return recursive_function(level - 1)

recursive_function(3)
""") == "base case reached"


def test_for_loop_1():
    assert eval("""
let mut int n = 0
for int i in 10..20:
    n++
n
""") == 10


def test_for_loop_2():
    assert eval("""
let mut int n = 0
for int i in 20 ..31:
    n++
n
""") == 11



def test_for_loop_3():
    assert eval("""
let mut int n = 0
for int i in 30.. 42:
    n++
n
""") == 12


def test_for_loop_4():
    assert eval("""
let mut int n = 0
for int i in 40 .. 53:
    n++
n
""") == 13


def test_for_loop_5():
    assert eval("""
let mut int n = 0
for int i in 14:
    n++
n
""") == 14



def test_for_loop_6():
    assert eval("""
let mut int n = 0
for int i in 100..110:
    n++
n
""") == 10


def test_for_loop_7():
    assert eval("""
let mut int n = 0
for int i in [10,20,30]:
    n += i
n
""") == 60


def test_for_loop_8():
    assert eval("""
let mut int n = 0
for int i in []:
    n += i
n
""") == 0

@pytest.mark.skip(reason="Type interence for string not implemented here")
def test_for_loop_9a():
    assert eval("""
let mut n = ""
for i in ["a", 'b', `c`]:
    n = n + i
n
""") == "abc"


def test_for_loop_9b():
    # this must fail because "a" is not an int
    with pytest.raises(Exception):
        assert eval("""
let mut n = ""
for int i in ["a", 'b', `c`]:
    n += i
n
""") == "abc"


@pytest.mark.skip(reason="Type interence for string not implemented here")
def test_for_loop_9c():
    assert eval("""
let mut n = ""
for i in ["a", 'b', `c`]:
    n += i
n
""") == "abc"


def test_for_loop_9d():
    assert eval("""
let mut n = ""
for str i in ["a", 'b', `c`]:
    n += i
n
""") == "abc"


def test_for_loop_10():
    assert eval("""
let mut n = 0
for i in 5:
    n += i
n
""") == 10


def test_for_loop_11():
    assert eval("""
let mut n = 0
for i in 0..5:
    n += i
n
""") == 10


def test_for_loop_12():
    assert eval("""
let start = 5
let end = 10
let mut n = 0
for i in start..end:
    n += i
n
""") == 35


def test_for_loop_13():
    assert eval("""
let int start = 5
let int end = 10
let mut n = 0
for i in start..end:
    n += i
n
""") == 35


def test_for_loop_14():
    assert eval("""
let int loops = 5
let mut n = 0
for i in loops:
    n += i
n
""") == 10


def test_for_loop_15():
    assert eval("""
let int loops = 5
let mut n = 0
for i in loops:
    n += i
n
""") == 10



def test_assignment_multiple_1():
    assert eval("""
let mut int i = 0
let mut int j = 1
i = j = 5
""") == 5 # value of i


def test_assignment_multiple_2():
    assert eval("""
let mut int i = 0
let mut int j = 1
i = j = 5
i
""") == 5 # value of i


def test_assignment_multiple_3():
    assert eval("""
let mut int i = 0
let mut int j = 1
i = j = 5
j
""") == 5 # value of j


def test_function_declaration_order():
    assert eval("""
let mut int u = 0x50
foo(4)

fn foo(int i) float:
    return bar(u - 5 / i, i) # i += i + 3

fn bar(float baaar, int q) float:
    return baaar * 5.56 + q

""") - 441.8499999 < 0.0001


def test_function_nested_return_1():
    assert eval("""
foo()
fn foo() int:
    return bar()
fn bar() int:
    return "bar"
""") == "bar"


def test_function_nested_return_3():
    assert eval("""
fn foo() int:
    return bar()
fn bar() int:
    return "bar"
foo()
""") == "bar"


def test_function_locall_variable_mutability_1():
    with pytest.raises(Exception):
        eval("""

fn foo(int i) int:
    i *= i #        <== not allowed because i is immutable
    return i

foo(4)

""") == 16


def test_function_local_variable_mutability_2():
    assert eval("""

fn foo(mut int i) int:
    i *= i #        <== allowed because i is mutable
    return i

foo(4)

""") == 16


def test_dead_code_1():
    with pytest.raises(Exception):
        eval("""

fn foo(mut int i) int:
    return i
    print(i)

foo(4)

""")


def test_dead_code_2():
    with pytest.raises(Exception):
        eval("""

fn foo(mut int i) int:
    return i
# comment
    print(i)

foo(4)

""")


def test_dead_code_3():
    with pytest.raises(Exception):
        eval("""

fn foo(mut int i) int:
    return i

    print(i)

foo(4)

""")


