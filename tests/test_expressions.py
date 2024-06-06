import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.context import resolve_path
from flolang import tokenize, default_environment, parse, interpret, to_native

def eval(expression: str, env=None):
    tok = tokenize(expression)
    ast = parse(tok)
    if not env:
        env = default_environment()
    val = interpret(ast, env)
    return to_native(val)

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
    assert eval("0.5") == .5     # this here is an interesting one
    # assert eval(".5") == .5    # this here is an interesting one
    assert eval("0.E5") == 0.E5
    assert eval("20.2") == 20.2
    assert eval("+1") == +1

def test_literal_string_expressions():
    assert eval('""') == ""
    assert eval('"1"') == "1"
    assert eval('"1asdfasdfasd"') == "1asdfasdfasd"
    assert eval('"+*ç%&/()="') == "+*ç%&/()="
    assert eval('"\\\""') == '\\"' # this here is an interesting one

def test_nesting():
    assert eval("1") == 1
    assert eval("(1)") == 1
    assert eval("(((1)))") == 1
    assert eval("( ((1) ))") == 1
    assert eval("( ((1)     ))") == 1

def test_math_expression():
    assert eval("1+1") == 2
    assert eval("1 + 1") == 2
    assert eval("1+ 1") == 2
    assert eval("2*0+3") == 3
    assert eval("2*(0+3)") == 6
    assert eval("(2*0)+3") == 3

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

def test_logic_expressions():
    # asked chatgpt for some random logic expressions
    assert eval("5 > 3 and 2 < 4") == True
    assert eval("10 == 10") == True
    assert eval("10 != 10") == False
    assert eval("7 == 8 or 10 != 10") == False
    assert eval("not False") == True
    assert eval("3 < 2") == False
    assert eval("not (3 < 2)") == True
    assert eval("5 & 3") == 1
    assert eval("6 | 2") == 6
    assert eval("4 ^ 1") == 5
    assert eval("~5") == -6
    assert eval("8 >> 2") == 2
    assert eval("3 << 1") == 6
    assert eval("True and False") == False
    assert eval("False or True") == True
    assert eval("not (True and False)") == True
    assert eval("10 & 7 | 3") == 3
    assert eval("8 | 1 ^ 2") == 11
    assert eval("7 & 3 << 2") == 4
    assert eval("12 >> 2 ^ 1") == 2
    assert eval("not (6 > 2 and 4 <= 4)") == False
    assert eval("(5 | 3) & (7 ^ 2)") == 5
    assert eval("3 & ~2 | 1") == 1
    assert eval("(8 >> 1) << 2") == 16

def test_logic_math_expressions():
    # asked chatgpt for some random logic expressions
    assert eval("(3 + 4 * 2) > 10 and 5 < 7") == True
    assert eval("10 / 2 == 5 or 6 - 1 != 5") == True
    assert eval("not (3 * 2 > 10)") == True
    assert eval("(5 & 3) + 2 == 3") == True
    assert eval("6 | (2 > 4)") == 6
    assert eval("(6 | 2) > 4") == True
    assert eval("6 | True") == 7
    assert eval("6 | False") == 6
    assert eval("~5 + 6 == 0") == True
    assert eval("8 >> 2 == 2 and 3 < 5") == True
    assert eval("3 << 1 == 6 or 2 > 4") == True
    assert eval("True and 5 * 2 == 10") == True
    assert eval("False or 7 - 4 == 3") == True
    assert eval("(10 & 7 | 3) > 0") == True
    assert eval("8 | (1 ^ 2)") == 11
    assert eval("(12 >> 2 ^ 1) < 4") == True
    assert eval("not (6 > 2 and 4 <= 4 - 1)") == True
    assert eval("5 + (3 | 1) > 7") == True
    assert eval("3 & ~2 | (1 + 1) == 3") == True
    assert eval("(8 >> 1) << 2 == 16 and 4 > 2") == True
    assert eval("not (True and 10 / 2 != 5)") == True

    # differs from python because == has more precidence
    # assert eval("8 | (1 ^ 2) == 11") == True
    assert eval("(8 | (1 ^ 2)) == 11") == True
    assert eval("8 | (1 ^ 2) == 11") == 8

    # differs from python because == has more precidence
    # assert eval("7 & (3 << 2) == 4") == True
    assert eval("(7 & (3 << 2)) == 4") == True
    assert eval("7 & (3 << 2) == 4") == 0

    # this one is interesing because it differs from python.
    # 2>4 is evaluated first, then bitwise OR yields 6.
    # assert eval("6 | 2 > 4") == True
    assert eval("6 | 2 > 4") == 6
    # assert eval("4 ^ 1 < 6") == True

def test_variables():
    assert eval("const int i = 0") == 0
    assert eval("const int i = 1") == 1
    assert eval("var int i") == 0 #it is an integer and therefore a number
    assert eval("var int i = 0") == 0
    assert eval("var int i = 1") == 1

def test_builtin_native_functions():
    import time, math

    #these are pure native functions
    assert eval("print(1)") == None
    assert abs(eval("time()") - time.time()) < 0.01 #might break if interpreter is suuuper slow
    assert eval("sin(1)") == math.sin(1)
    assert eval("cos(1)") == math.cos(1)
    assert eval("tan(1)") == math.tan(1)
    assert eval("atan2(1, 1)") == math.pi / 4
    assert eval("atan2(1, 2)") == math.atan2(1, 2)
    assert eval("round(0.49)") == 0
    assert eval("round(0.51)") == 1

def test_builtin_functions():
    import time, math, statistics

    # these are pure native functions
    assert eval("pi") == math.pi
    assert eval("euler") == math.e

    assert eval("floor(0.49)") == 0
    assert eval("floor(0.51)") == 0

    randmax = 2**32 - 1
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
    #mean must be about
    assert mean_value > randmax * 0.4 and mean_value < randmax * 0.6
    assert variance_value > randmax



def test_comments():
    assert eval("") == None
    assert eval("#") == None
    assert eval(" #") == None
    assert eval(" # ") == None
    assert eval("# ") == None
    assert eval("# comment") == None
    assert eval(" # comment") == None
    assert eval("1 # comment") == 1
    assert eval("1     #           comment") == 1

def test_math_epressions():
    assert eval("1 + 2") == 3