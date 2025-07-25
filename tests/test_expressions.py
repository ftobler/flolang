import pytest
from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native, eval, eval_parse
import math
import time
import flolang.error as error


def test_literal_number_epressions():
    assert eval("0") == 0
    assert eval("0.1") == 0.1
    assert eval("1") == 1
    assert eval("1.0000000001") == 1.0000000001
    assert eval("1E3") == 1000
    assert eval("1E30") == 1E30
    assert eval("1.2E3") == 1200
    assert eval("-1") == -1
    assert eval("12346") == 12346
    assert eval("12.3E4") == 12.3E4
    assert eval("12") == 12
    assert eval("10E9") == 10E9
    assert eval("10E0") == 10E0
    assert eval("10E4") == 10E4
    # assert eval("10.E") == 10.E0 #this here is an interesting one
    assert eval("10.E4") == 10.E4
    assert eval("10.5E4") == 10.5E4
    assert eval("10.") == 10.
    assert eval("10.22") == 10.22
    assert eval("10") == 10
    assert eval("11") == 11
    assert eval("0.E5") == 0.E5
    assert eval("20.2") == 20.2
    assert eval("+1") == +1


def test_literal_number_epressions_special():
    assert eval("0.5") == .5     # this here is an interesting one
    # assert eval(".5") == .5    # this here is an interesting one


def test_literal_string_expressions_1():
    assert eval('""') == ""
    assert eval('"1"') == "1"
    assert eval('"1asdfasdfasd"') == "1asdfasdfasd"
    assert eval('"+*ç%&/()="') == "+*ç%&/()="
    assert eval('"\\\\\\""') == '\\"'  # this here is an interesting one


def test_literal_string_expressions_2():
    assert eval("''") == ""
    assert eval("'1'") == "1"
    assert eval("'1asdfasdfasd'") == "1asdfasdfasd"
    assert eval("'+*ç%&/()='") == "+*ç%&/()="
    assert eval("'\\\\\\''") == "\\'"  # this here is an interesting one


def test_literal_string_expressions_3():
    assert eval("``") == ""
    assert eval("`1`") == "1"
    assert eval("`1asdfasdfasd`") == "1asdfasdfasd"
    assert eval("`+*ç%&/()=`") == "+*ç%&/()="
    assert eval('`\\\\\\``') == '\\`'  # this here is an interesting one


def test_literal_string_expressions_escapement_1():
    # escapement of the delimiting character
    # this tests the string escapment in parsing
    assert eval('"\\\""') == '"'
    assert eval("'\"'") == '"'
    assert eval('`"`') == '"'


def test_literal_string_expressions_escapement_2():
    # escapement of the non-delimiting character
    # this tests the string escapment in parsing
    assert eval('"\'"') == "'"
    assert eval("'\\\''") == "'"
    assert eval("`'`") == "'"


def test_literal_string_expressions_escapement_3():
    # escapement of the non-delimiting character
    # this tests the string escapment in parsing
    assert eval('"`"') == "`"
    assert eval("'`'") == "`"
    assert eval("`\\``") == "`"


def test_nesting():
    assert eval("1") == 1
    assert eval("(1)") == 1
    assert eval("(((1)))") == 1
    assert eval("( ((1) ))") == 1
    assert eval("( ((1)     ))") == 1


def test_math_expression_basic():
    assert eval("1+1") == 2
    assert eval("1 + 1") == 2
    assert eval("1+ 1") == 2
    assert eval("2*0+3") == 3
    assert eval("2*(0+3)") == 6
    assert eval("(2*0)+3") == 3


def test_math_expression():
    # asked chatgpt for some random math expressions
    assert eval("3 + 4 * 2") == 11
    assert eval("(5 - 3) ** 2") == 4
    assert eval("9 / 3 + 2") == 5.0
    assert eval("15 % 4") == 3
    assert eval("7 * (8 + 2)") == 70
    assert eval("12 - 4 / 2") == 10.0
    assert eval("2 ** 3 + 1") == 9
    assert eval("10 // 3") == 3
    assert eval("8 + 9 * 2 - 5") == 21
    assert eval("(14 + 6) / 2") == 10.0
    assert eval("5 ** 2 - 3 * 4") == 13
    assert eval("18 % 5 + 7") == 10
    assert eval("6 * 7 - 8 / 2") == 38.0
    assert eval("(20 - 3) * 2") == 34
    assert eval("9 + (4 * 3) / 2") == 15.0
    assert eval("8 ** 2 // 4") == 16
    assert eval("16 / 4 + 3 * 2") == 10.0
    assert eval("5 + 6 - 2 * 3") == 5
    assert eval("7 % 2 + 9") == 10
    assert eval("11 * (2 + 3) - 6") == 49
    assert eval("3+4*2") == 11
    assert eval("(5 -3)**2") == 4
    assert eval("9/3+2.0") == 5.0
    assert eval("15%4") == 3
    assert eval("7*(8+2)") == 70
    assert eval("12-4/2") == 10.0
    assert eval("2**3+1.5") == 9.5
    assert eval("10 //  3") == 3
    assert eval("8+9*2 -5") == 21
    assert eval("(  14+6)/2") == 10.0
    assert eval("5**2-3*4") == 13
    assert eval("18 %5+7") == 10
    assert eval("6  *7-8/2") == 38.0
    assert eval("(20-3)*2.0") == 34.0
    assert eval("9+ (4*3)/2") == 15.0
    assert eval("8**  2//  4    ") == 16
    assert eval("16/4+3*2") == 10.0
    assert eval("5+6-2*3") == 5
    assert eval("7%2+9.0") == 10.0
    assert eval("11*   (2+3)-6") == 49
    assert eval("1.23E3 + 4.56E2") == 1686.0
    assert eval("7*(8.2+1.8)") == 70.0
    assert eval("9/1.5+2") == 8.0
    assert eval("(4.5-1.5)**3") == 27.0
    assert eval("2.0**3 + 1") == 9.0
    assert eval("10//3.0") == 3.0
    assert eval("8+9.0*2-5") == 21.0
    assert eval("(   14+6.0)/2") == 10.0
    assert eval("5**2.0-3*4") == 13.0
    assert eval("18%5.0 + 7") == 10.0


def test_logic_expressions_1():
    # asked chatgpt for some random logic expressions
    assert eval("5 > 3 and 2 < 4") is True
    assert eval("10 == 10") is True
    assert eval("10 != 10") is False
    assert eval("7 == 8 or 10 != 10") is False
    assert eval("not False") is True
    assert eval("3 < 2") is False
    assert eval("not (3 < 2)") is True
    assert eval("5 & 3") == 1
    assert eval("6 | 2") == 6
    assert eval("4 ^ 1") == 5
    assert eval("~5") == -6
    assert eval("8 >> 2") == 2
    assert eval("3 << 1") == 6
    assert eval("True and False") is False
    assert eval("False or True") is True
    assert eval("not (True and False)") is True
    assert eval("10 & 7 | 3") == 3
    assert eval("8 | 1 ^ 2") == 11
    assert eval("7 & 3 << 2") == 4
    assert eval("12 >> 2 ^ 1") == 2
    assert eval("not (6 > 2 and 4 <= 4)") is False
    assert eval("(5 | 3) & (7 ^ 2)") == 5
    assert eval("3 & ~2 | 1") == 1
    assert eval("(8 >> 1) << 2") == 16


@pytest.mark.skip(reason="not yet implemented")
def test_logic_expressions_2():
    # asked chatgpt for some random logic expressions
    assert eval("False is not True") is True
    assert eval("False is not False") is False
    assert eval("False is True") is False
    assert eval("False is False") is True


def test_logic_math_expressions():
    # asked chatgpt for some random logic expressions
    assert eval("(3 + 4 * 2) > 10 and 5 < 7") is True
    assert eval("10 / 2 == 5 or 6 - 1 != 5") is True
    assert eval("not (3 * 2 > 10)") is True
    assert eval("(5 & 3) + 2 == 3") is True
    assert eval("6 | (2 > 4)") == 6
    assert eval("(6 | 2) > 4") is True
    assert eval("6 | True") == 7
    assert eval("6 | False") == 6
    assert eval("~5 + 6 == 0") is True
    assert eval("8 >> 2 == 2 and 3 < 5") is True
    assert eval("3 << 1 == 6 or 2 > 4") is True
    assert eval("True and 5 * 2 == 10") is True
    assert eval("False or 7 - 4 == 3") is True
    assert eval("(10 & 7 | 3) > 0") is True
    assert eval("8 | (1 ^ 2)") == 11
    assert eval("(12 >> 2 ^ 1) < 4") is True
    assert eval("not (6 > 2 and 4 <= 4 - 1)") is True
    assert eval("5 + (3 | 1) > 7") is True
    assert eval("3 & ~2 | (1 + 1) == 3") == 1
    assert eval("(8 >> 1) << 2 == 16 and 4 > 2") is True
    assert eval("not (True and 10 / 2 != 5)") is True


def test_logic_math_expressions_precidence_problems_1():
    # differs from python because == has more precidence
    # assert eval("8 | (1 ^ 2) == 11") is True
    assert eval("(8 | (1 ^ 2)) == 11") is True
    assert eval("8 | (1 ^ 2) == 11") == 8


def test_logic_math_expressions_precidence_problems_2():
    # differs from python because == has more precidence
    # assert eval("7 & (3 << 2) == 4") is True
    assert eval("(7 & (3 << 2)) == 4") is True
    assert eval("7 & (3 << 2) == 4") == 0


def test_logic_math_expressions_precidence_problems_3():
    # this one is interesing because it differs from python.
    # 2>4 is evaluated first, then bitwise OR yields 6.
    # assert eval("6 | 2 > 4") is True
    assert eval("6 | 2 > 4") == 6
    # assert eval("4 ^ 1 < 6") is True


def test_inline_statements_2():
    # you can actually execute multiple statements in 1 line
    # they count as 2 separate statements. No block.
    assert eval("let int i = 10          pi") == math.pi
    assert eval("True 1") == 1

    # is the evaluation of if because that is the last statement that is executed
    assert eval("if True: 1") is None
    assert eval("if False: 1") is None
    # is the evaluation of the number at the end because that is executed either case
    assert eval("if True: 1 123") == 123
    assert eval("if False: 1 1123") == 1123


def test_assignment_1a():
    assert eval("let mut int i = 10          i = 20") == 20
    assert eval("let mut int i = 10          i += 20") == 30
    assert eval("let mut int i = 10          i -= 20") == -10
    assert eval("let mut int i = 10          i *= 20") == 200
    assert eval("let mut int i = 10          i %= 7") == 3
    assert eval("let mut int i = 0x09        i &= 0x81") == 0x01
    assert eval("let mut int i = 0x09        i ^= 0x11") == 0x18
    assert eval("let mut int i = 0x09        i |= 0x18") == 0x19
    assert eval("let mut int i = 0x09        i <<= 1") == 0x12
    assert eval("let mut int i = 0x09        i >>= 1") == 0x04


def test_assignment_1b():
    assert eval("let mut float i = 10          i = 20") == 20
    assert eval("let mut float i = 10          i += 20") == 30
    assert eval("let mut float i = 10          i -= 20") == -10
    assert eval("let mut float i = 10          i *= 20") == 200
    with pytest.raises(Exception):
        assert eval("let mut float i = 10      i %= 7") == 3
    with pytest.raises(TypeError):
        eval("let mut float i = 0x09        i &= 0x81")
    with pytest.raises(TypeError):
        eval("let mut float i = 0x09        i ^= 0x11")
    with pytest.raises(TypeError):
        eval("let mut float i = 0x09        i |= 0x18")
    with pytest.raises(TypeError):
        eval("let mut float i = 0x09        i <<= 1")
    with pytest.raises(TypeError):
        eval("let mut float i = 0x09        i >>= 1")


def test_assignment_1c():
    assert eval("let mut int i = 10          i = 20") == 20
    assert eval("let mut int i = 10          i += 20") == 30
    assert eval("let mut int i = 10          i -= 20") == -10
    assert eval("let mut int i = 10          i *= 20") == 200
    assert eval("let mut int i = 10          i %= 7") == 3
    assert eval("let mut int i = 0x09        i &= 0x81") == 0x01
    assert eval("let mut int i = 0x09        i ^= 0x11") == 0x18
    assert eval("let mut int i = 0x09        i |= 0x18") == 0x19
    assert eval("let mut int i = 0x09        i <<= 1") == 0x12
    assert eval("let mut int i = 0x09        i >>= 1") == 0x04


def test_assignment_2():
    assert eval("let mut int i = 10          i /= 20") == 0  # conversion to float does not happen
    with pytest.raises(Exception):
        assert eval("let mut int i = 10          i /= 20.0") == 0.5  # float inferred
    assert eval("let mut float i = 10        i /= 20") == 0.5  # float required
    assert eval("let mut float i = 10        i /= 20.0") == 0.5  # float required


def test_elvis_1():
    # basic
    assert eval("True ? 1 : 0") == 1
    assert eval("False ? 0 : 1") == 1

    # Additional tests
    assert eval("10 > 5 ? 42 : 99") == 42  # True condition
    assert eval("not 0 ? 3.14 : 0") == 3.14  # not 0 evaluates to True
    assert eval("True ? 1 : 0") == 1
    assert eval("False ? 0 : 1") == 1
    assert eval("10 > 5 ? 42 : 99") == 42
    assert eval("not 0 ? 3.14 : 0") == 3.14


def test_elvis_2():
    assert eval("10 > 5 ? 42 : 99") == 42
    assert eval("not 0 ? 3.14 : 1") == 3.14


def test_elvis_strings():
    # Additional tests
    assert eval('"abc" ? "yes" : "no"') == "yes"  # Non-empty string evaluates to True


def test_variables_1():
    assert eval("static int i = 0") == 0
    assert eval("static int i = 1") == 1
    assert eval("let int i = 0") == 0
    assert eval("let int i = 1") == 1
    assert eval("static mut int i = 0") == 0
    assert eval("static mut int i = 1") == 1
    assert eval("let mut int i = 0") == 0
    assert eval("let mut int i = 1") == 1


def test_variables_2a():
    assert eval("let bool i = 0") == 0
    assert eval("let bool i = True") == 1
    assert eval("let bool i = False") == 0
    assert eval("let int i = 10") == 10
    assert eval("let float i = 10") == 10


def test_variables_2b():
    assert eval("let i = 0") == 0
    assert eval("let i = True") == 1
    assert eval("let i = False") == 0
    assert eval("let i = 0.0") == 0


def test_variables_2c():
    assert eval("let int i  = -10") == -10
    assert eval("let float i = -10") == -10


def test_variables_2d():
    assert eval("let i = 10") == 10
    assert eval("let i = -10") == -10
    assert str(eval("let i = 10.0")) == "10.0"
    assert str(eval("let i = -10.0")) == "-10.0"
    assert eval("let i = 10.5") == 10.5
    assert eval("let i = -10.5") == -10.5
    assert eval("let i = ''") == ""
    assert eval("let i = {}") == {}
    assert eval("let i = []") == []
    assert eval("let i = degrees") == "<RuntimeFunction>"


def test_variables_starting_with_keywords():
    # these are critical because they start with keywords
    assert eval("let int function = 1") == 1
    assert eval("let int returnee = 1") == 1
    assert eval("let int forloop = 1") == 1
    assert eval("let int whilenot = 1") == 1
    assert eval("let int importieren = 1") == 1
    assert eval("let int iffy = 1") == 1
    assert eval("let int instance = 1") == 1
    assert eval("let int variable = 1") == 1
    assert eval("let int constant = 1") == 1
    assert eval("let int integer = 1") == 1


def test_variables_exotic_names():
    # some a bit more exotic names we allow
    eval("let int __name   = 0")
    eval("let int __0name  = 0")
    eval("let int _0_name  = 0")
    eval("let int   _name0 = 0")
    eval("let int __name__ = 0")


def test_illegal_variable_1():
    # with pytest.raises(Exception):
    eval("let i = 10")  # legal now

    with pytest.raises(Exception):
        eval("var int i = 10")

    with pytest.raises(Exception):
        eval("mut int i = 10")

    with pytest.raises(Exception):
        eval("let int* i = 10")

    with pytest.raises(Exception):
        eval("😥")

    eval('"🥰"')  # that just belongs here now


@pytest.mark.skip(reason="type checking not yet implemented")
def test_illegal_variable_2():
    with pytest.raises(Exception):
        eval("some_identifier_is_here")  # this is legal. Problem is, it currently parses because there is no type checking and this is a variable without type


def test_illegal_variable_cases():
    with pytest.raises(Exception):
        eval("let int kebap-case = 10")

    with pytest.raises(Exception):
        eval("let int emojy😥case = 10")

    with pytest.raises(Exception):
        eval("let int illegal_@_name = 10")

    with pytest.raises(Exception):
        eval("let int illegal_ä_name = 10")

    with pytest.raises(Exception):
        eval("let int illegal_$_name = 10")

    with pytest.raises(Exception):
        eval("let int illegal_!_name = 10")

    with pytest.raises(Exception):
        eval("let int illegal.name = 10")

    with pytest.raises(Exception):
        eval("let int illegalname() = 10")


def test_builtin_native_functions():
    # these are pure native functions
    assert eval("print(1)") is None
    assert abs(eval("time()") - time.time()) < 0.01  # might break if interpreter is suuuper slow


def test_builtin_native_functions_trigonometry():
    assert eval("sin(1)") == math.sin(1)
    assert eval("cos(1)") == math.cos(1)
    assert eval("tan(1)") == math.tan(1)

    assert eval("asin(1)") == math.asin(1)
    assert eval("acos(1)") == math.acos(1)
    assert eval("atan(1)") == math.atan(1)

    assert eval("atan2(1, 1)") == math.pi / 4
    assert eval("atan2(1, 2)") == math.atan2(1, 2)


def test_builtin_native_functions_round():
    assert eval("round(0.49)") == 0
    assert eval("round(0.51)") == 1


def test_builtin_native_functions_nan():
    assert eval("isnan(nan)") is True
    assert eval("isnan(pi)") is False
    assert eval("isnan(inf)") is False


def test_builtin_native_functions_inf():
    assert eval("isinf(inf)") is True
    assert eval("isinf(-inf)") is True
    assert eval("isinf(pi)") is False
    assert eval("isinf(nan)") is False


def test_builtin_functions_const():
    # these are normal functions
    assert eval("pi") == math.pi
    assert eval("euler") == math.e
    assert eval("tau") == math.tau


def test_builtin_functions_nan_inf():
    assert math.isnan(eval("nan")) is True
    assert math.isinf(eval("inf")) is True


def test_builtin_functions_floor():
    assert eval("floor(0.49)") == 0
    assert eval("floor(0.51)") == 0


def test_builtin_functions_conversion():
    assert eval("degrees(1.3)") == math.degrees(1.3)
    assert eval("radians(123)") == math.radians(123)


def test_builtin_functions_random():
    import statistics

    randmax = 2**31 - 1
    assert eval("RAND_MAX") == randmax

    # test the random number generator. Since this is not stateless, need an
    # environment which stays between eval calls
    env = default_environment()

    # check if value is each time in designated bounds
    for i in range(50):
        value = eval("rand()", env)
        assert value >= 0 and value <= randmax

    # check statistically that random is random (basic check)
    values = [eval("rand()", env) for i in range(50)]
    mean_value = statistics.mean(values)
    print(values)
    variance_value = statistics.variance(values)
    # mean must be about
    assert mean_value > randmax * 0.4 and mean_value < randmax * 0.6
    assert variance_value > randmax


def test_builtin_functions_sleep():
    import time
    t = time.time()
    assert eval("sleep(0.1)") is None
    assert time.time() - t < 0.05


def test_comments():
    assert eval("") is None
    assert eval("#") is None
    assert eval(" #") is None
    assert eval(" # ") is None
    assert eval("# ") is None
    assert eval("# comment") is None
    assert eval(" # comment") is None
    assert eval("1 # comment") == 1
    assert eval("1     #           comment") == 1


def test_comments_shebang():
    # want to allow this. Normally the ' ' after the '#' is
    # mandatory, so this is an exception
    assert eval("#!/bin/sh") is None
    assert eval("#!/usr/bin/python") is None
    assert eval("#!flolang") is None


def test_inline_double_declaration_to_itself():
    with pytest.raises(Exception):
        eval("let mut int a = 3 == a")


def test_dict_literal_1():
    eval("{a: 1, b: 2}")
    eval("{a: 1, b: 2,}")


@pytest.mark.skip(reason="not yet implemented correctly")
def test_dict_literal_2():
    eval("dyn dict i = {a: 1, b: 2}")
    eval("dyn dict i = {a: 1, b: 2}")
    eval("dyn dict i = {pi, euler, tau}")


def test_dict_literal_3():
    eval("let d = {a: 1, b: 2}")
    eval("let d = {a: 1, b: 2}")
    eval("let d = {pi, euler, tau}")


@pytest.mark.skip(reason="not yet implemented correctly")
def test_set_literal_1():
    eval("dyn set i = pi, euler, tau}")
    eval("dyn set i = {1, 2, 3}")


def test_list_literal_1():
    eval("[1, 2, 3]")
    eval("[1, 2, 3,]")


@pytest.mark.skip(reason="not yet implemented correctly")
def test_list_literal_2():
    eval("let int[] i = [1, 2, 3]")
    eval("const int[] i = [1, 2, 3]")
    eval("dyn list i = [1, 2, 3]")
    eval("dyn list i = [pi, euler, tau]")


def test_member_expression_1():
    eval_parse("foo.bar")
    eval_parse("foo.bar[1]")
    eval_parse("foo.bar()")


def test_member_expression_2():
    eval_parse("foo[0].bar")
    eval_parse("foo[0].bar[1]")
    eval_parse("foo[0].bar()")


@pytest.mark.skip(reason="Test not yet implemented correctly")
def test_member_expression_3():
    eval_parse("foo().bar")
    eval_parse("foo().bar[1]")
    eval_parse("foo().bar()")


def test_unary_1():
    with pytest.raises(Exception):
        eval("let mut i = 3       --i")  # not possible in python
    with pytest.raises(Exception):
        eval("let mut i = 3       -i")  # not possible in python
    with pytest.raises(Exception):
        eval("let mut i = 3       ++i")  # assumes 3++. i also not defined
    with pytest.raises(Exception):
        eval("let mut i = 3       +i")  # i not defined
    with pytest.raises(Exception):  # incomplete
        eval("let mut i = 3-")
    with pytest.raises(Exception):  # incomplete
        eval("let mut i = 3+")


def test_unary_2():
    assert eval("let mut i = 3       ~i") == -4
    assert eval("let mut i = 3       ~i            i") == 3
    assert eval("let mut i = 3       not i") is False
    assert eval("let mut i = 3       i++") == 3
    assert eval("let mut i = 3       i++           i") == 4
    assert eval("let mut i = 3       i--") == 3
    assert eval("let mut i = 3       i--           i ") == 2


def test_unary_3():
    # these might differ from python as python does not have --i, but will just
    # interpret it ast -(-(i))
    assert eval("let mut i = 3       i--         1") == 1
    assert eval("let mut i = 3       i++         1") == 1
    assert eval("let mut i = 3       i--        +1") == 4
    assert eval("let mut i = 3       i--        -1") == 2

    assert eval("let mut i = 3       i--1") == 1
    assert eval("let mut i = 3       i++1") == 1


def test_unary_4():
    # these are ambiguous and therefore banned
    with pytest.raises(error.ParserError):  # incomplete
        eval("let mut i = 3       i--+1")
    with pytest.raises(error.ParserError):  # incomplete
        eval("let mut i = 3       i---1")


def test_unary_5():
    assert eval("-1") == -1
    assert eval("+1") == +1
    assert eval("++1") == 2
    assert eval("--1") == 0


def test_unary_6():
    with pytest.raises(error.ParserError):
        assert eval("let mut i = 3++") == 3
    assert eval("let mut i = ++3") == 4
    assert eval("let mut i = +3") == 3
    with pytest.raises(error.ParserError):
        assert eval("let mut i = 3--") == 3
    assert eval("let mut i = --3") == 2
    assert eval("let mut i = -3") == -3


def test_unary_7():
    # these are not allowed on identifiers
    # as programmer expected to change a variable, so it must be one.
    with pytest.raises(error.ParserError):
        eval("1++")
    with pytest.raises(error.ParserError):
        eval("1--")


def test_function_default_values_1():
    assert eval("""
fn foo(int n = 123) int:
    return n
foo()
""") == 123


def test_function_default_values_2():
    # this is not allowed
    with pytest.raises(Exception):
        eval("""
fn foo(int n) int:
    return n
foo() # this is not allowed
""")


def test_function_default_values_3():
    assert eval("""
fn foo(int a, int b = 2) int:
    return a + b
foo(10)
""") == 12


def test_function_default_values_4():
    assert eval("""
fn foo(int a, int b = 2) int:
    return a + b
foo(10, 20)
""") == 30


def test_function_default_values_5():
    assert eval("""
fn foo(int a = 1, int b = 2) int:
    return a + b
foo(10, 20)
""") == 30


def test_function_default_values_6():
    assert eval("""
fn foo(int a = 1, int b) int:
    return a + b
foo(10, 20)
""") == 30


def test_function_default_values_7():
    assert eval("""
fn foo(int a, int b = 2) int:
    return a + b
foo(10)
""") == 12


def test_function_default_values_8():
    assert eval("""
fn foo(int a = 1, int b = 2) int:
    return a + b
foo(10)
""") == 12


def test_function_default_values_9():
    with pytest.raises(Exception):
        eval("""
fn foo(int a = 1, int b) int:
    return a + b
foo(10)
""")


def test_function_default_values_10():
    with pytest.raises(Exception):
        eval("""
fn foo(int a, int b = 2) int:
    return a + b
foo()
""")


def test_function_default_values_11():
    assert eval("""
fn foo(int a = 1, int b = 2) int:
    return a + b
foo()
""") == 3


def test_function_default_values_12():
    with pytest.raises(Exception):
        eval("""
fn foo(int a = 1, int b) int:
    return a + b
foo()
""")


def test_function_default_value_syntax_1():
    assert eval("""
fn foo(int a= 1, int b) int:
    return a + b
foo(1, 3)
""") == 4


def test_function_default_value_syntax_2():
    assert eval("""
fn foo(int a =1, int b) int:
    return a + b
foo(1, 3)
""") == 4


def test_function_default_value_syntax_3():
    assert eval("""
fn foo(int a=1, int b) int:
    return a + b
foo(1, 3)
""") == 4


def test_function_default_value_syntax_4():
    assert eval("""
fn foo(int a=1 , int b) int:
    return a + b
foo(1, 3)
""") == 4


def test_function_default_value_syntax_5():
    assert eval("""
fn foo(int a= 1) int:
    return a
foo(1)
""") == 1


def test_function_default_value_syntax_6():
    assert eval("""
fn foo(int a =1) int:
    return a
foo(1)
""") == 1


def test_function_default_value_syntax_7():
    assert eval("""
fn foo(int a=1) int:
    return a
foo(1)
""") == 1


def test_function_default_value_syntax_8():
    assert eval("""
fn foo(int a=1 ) int:
    return a
foo(1)
""") == 1


def test_function_default_value_with_expression_1():
    assert eval("""
fn foo(int a = 2**8) int:
    return a
foo()
""") == 256


def test_function_default_value_with_expression_2():
    # ok, cool, but ... is this a good idea? Python allows this
    # but may be problematic to translate into C later.
    # keep the test in for now. when it never breaks good, else
    # it has to be explicitly forbiddden in the interpreter.
    assert eval("""
fn bar() int:
    return 42
fn foo(int a = bar()) int:
    return a
foo()
""") == 42


def test_function_default_value_with_expression_3():
    # ok, cool, but ... is this a good idea? Python allows this
    # but may be problematic to translate into C later.
    # keep the test in for now. when it never breaks good, else
    # it has to be explicitly forbiddden in the interpreter.

    # if this is to keep, bar must run before foo is ever called
    # because that might create issues when foo() evaluates its stuff
    # every time it has ran
    assert eval("""
let mut int bar_ran = 0
fn bar() int:
    bar_ran = 1
    return 42
fn foo(int a = bar()) int:
    return a
bar_ran
""") == 1


def test_continue_expression():
    with pytest.raises(Exception):
        eval("continue #not allowed because this is not a loop")
    with pytest.raises(Exception):
        eval("continue")


def test_break_expression():
    with pytest.raises(Exception):
        eval("break #not allowed because this is not a loop")
    with pytest.raises(Exception):
        eval("break")


def test_return_expression_1():
    with pytest.raises(Exception):
        eval("return #not allowed because this is not a function")
    with pytest.raises(Exception):
        eval("return")


def test_return_expression_2():
    assert eval("""
fn foo(int n) int:
    if n == 1:
        return n
    else:
        return n
foo(7)

""") == 7


def test_break_not_allowed_in_function_1():
    with pytest.raises(Exception):
        eval("""
fn foo(int n) int:
    break # not allowed in function
foo(7)
""") == 7


def test_break_not_allowed_in_function_2():
    with pytest.raises(Exception):
        eval("""
fn foo(int n) int:
    if True:
        break # not allowed in function or if
foo(7)
""") == 7


def test_function_is_executed_after_program_variable_declarations_normal():
    assert eval("""
fn ret(int x) int:
    return x
ret(714)
6
""") == 714


def test_function_is_executed_after_program_variable_declarations_native():
    assert eval("""
sin(pi/2)
8
""") == 1.0


def test_unreachable():
    with pytest.raises(error.CompileException):
        eval("unreachable")


def test_delete_1():
    eval("""
let int i = 0
delete i
""")


@pytest.mark.skip("static is not working")
def test_delete_2a():
    # delete is not allowed in normal mode without the script shebang.
    # that is passed by default in the tests, so the code is shorter
    # and requires no main function
    with pytest.raises(error.CompileException):
        eval("""
static int i = 0
delete i
""", shebang=None)


def test_delete_2b():
    # delete is not allowed in normal mode without the script shebang.
    # that is passed by default in the tests, so the code is shorter
    # and requires no main function
    with pytest.raises(error.CompileException):
        eval("""
int i = 0
delete i
""", shebang=None)


def test_delete_3():
    eval("""
let int i = 0
delete i
let int i = 0
""")


def test_delete_4():
    with pytest.raises(error.CompileException):
        eval("""
let int i = 0
let int i = 0
""")


@pytest.mark.skip(reason="type checking not yet implemented")
def test_template():
    with pytest.raises(error.CompileException):
        eval("""
class Animal<T>:
    let T: appendage
""")


@pytest.mark.skip(reason="currently it does not work")
def test_alloc_expression():
    # the test is mainly here because of the '@'
    # which makes this keyword special
    eval("@alloc pi")


def test_no_eval():
    # there must be no eval
    with pytest.raises(error.CompileException):
        eval("eval('')")


@pytest.mark.skip(reason="template not implemented")
def test_parse_template_type_1():
    assert eval("let mut foo<T> bar = 1") == 1
    assert eval("let mut foo<T<J>> bar = 1") == 1
    assert eval("let mut foo<T<J>>[] bar = 1") == 1
    assert eval("let mut foo<T<J>[]>[] bar = 1") == 1


@pytest.mark.skip(reason="template not implemented")
def test_parse_template_type_2():
    assert eval("let mut foo<100> bar = 1") == 1
    assert eval("let mut foo<T<100>> bar = 1") == 1
    assert eval("let mut foo<T<100>>[] bar = 1") == 1
    assert eval("let mut foo<T<100>[]>[] bar = 1") == 1


@pytest.mark.skip(reason="template not implemented")
def test_parse_template_type_3():
    assert eval("let mut foo<100+10> bar = 1") == 1
    assert eval("let mut foo<T<100+10>> bar = 1") == 1
    assert eval("let mut foo<T<100+10>>[] bar = 1") == 1
    assert eval("let mut foo<T<100+10>[]>[] bar = 1") == 1


@pytest.mark.skip(reason="template not implemented")
def test_parse_template_type_4():
    assert eval("let mut foo<T<J> > bar = 1") == 1
    assert eval("let mut foo<T<J> >[] bar = 1") == 1
    assert eval("let mut foo<T<100> > bar = 1") == 1
    assert eval("let mut foo<T<100> >[] bar = 1") == 1
    assert eval("let mut foo<T<100+10> > bar = 1") == 1
    assert eval("let mut foo<T<100+10> >[] bar = 1") == 1


@pytest.mark.skip(reason="template not implemented")
def test_parse_template_type_5():
    eval("let mut foo<'asdf'> bar = 1")


def test_type_1():
    assert eval("1+1") == 2
    assert eval("1+-1") == 0
    assert str(eval("1.0+1")) == "2.0"
    assert str(eval("1.0+-1")) == "0.0"
    assert str(eval("1+1.0")) == "2.0"
    assert str(eval("1+-1.0")) == "0.0"
    assert str(eval("1.0+1.0")) == "2.0"
    assert str(eval("1.0+-1.0")) == "0.0"


def test_type_2aa():
    assert eval("let int a = 10         let int b = 20          a-b") == -10
    assert eval("let int a = 10         let float b = 20        a-b") == -10
    assert eval("let float a = 10       let int b = 20          a-b") == -10


def test_type_2ab():
    assert str(eval("let int a = 10         let float b = 20        a-b")) == "-10.0"
    assert str(eval("let float a = 10       let int b = 20          a-b")) == "-10.0"


def test_type_2ac():
    assert str(eval("let int a = 10         let int b = 20        a-b")) == "-10"


def test_type_2b():
    assert eval("let int a = 10         let int b = 20          a-b") == -10
    assert eval("let float a = 10       let float b = 20        a-b") == -10
    assert eval("let int a = 10         let float b = 20        a-b") == -10
    assert eval("let float a = 10       let int b = 20          a-b") == -10


def test_type_2c():
    assert eval("let int a = 10         let int b = 20          let int c = a-b") == -10
    assert eval("let float a = 10       let float b = 20        let int c = a-b") == -10
    assert eval("let int a = 10         let float b = 20        let int c = a-b") == -10
    assert eval("let float a = 10       let int b = 20          let int c = a-b") == -10


def test_type_2d():
    assert eval("let int a = 10         let int b = 20          let float c = a-b") == -10
    assert eval("let float a = 10       let float b = 20        let float c = a-b") == -10
    assert eval("let int a = 10         let float b = 20        let float c = a-b") == -10
    assert eval("let float a = 10       let int b = 20          let float c = a-b") == -10


def test_type_3a():
    assert eval("let int a = 10         let bool b = True       a-b") == 9
    assert eval("let bool a = 10        let bool b = True       a-b") == 0
    assert eval("let bool a = 10        let int b = True        a-b") == 0


def test_type_3b():
    assert eval("let int a = True         let bool b = 10       a-b") == 0
    assert eval("let bool a = True        let bool b = 10       a-b") == 0
    assert eval("let bool a = True        let int b = 10        a-b") == -9


def test_type_4a():
    with pytest.raises(Exception):
        eval("let mut int a = 1        a = 'hello'")


def test_type_4b():
    with pytest.raises(error.CompileException):
        eval("let mut int a = 1        a = 1.0")


def test_type_4c():
    # need typecast
    eval("let mut int a = 1        a = int(1.0)")
