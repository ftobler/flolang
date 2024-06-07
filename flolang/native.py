import flolang.interpreter as inter
import time
import math
import random

from flolang.lexer import tokenize
from flolang.abstract_source_tree import Parser
from flolang.interpreter import interpret

def to_native(val : inter.RuntimeValue):
    if hasattr(val, "value"):
        return val.value
    return "<" + val.variant + ">"

def create_default_environment():
    env = inter.Environment()

    def native_print(arguments: list[inter.RuntimeValue]):
        args = [runtime_var.value for runtime_var in arguments]
        print(*args)
    env.declare("print", inter.NativeFunction(native_print), True)

    def native_time(arguments: list[inter.RuntimeValue]):
        return inter.NumberValue(time.time())
    env.declare("time", inter.NativeFunction(native_time), True)

    def native_sin(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.sin(x)
        return inter.NumberValue(y)
    env.declare("sin", inter.NativeFunction(native_sin), True)

    def native_cos(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.cos(x)
        return inter.NumberValue(y)
    env.declare("cos", inter.NativeFunction(native_cos), True)

    def native_tan(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.tan(x)
        return inter.NumberValue(y)
    env.declare("tan", inter.NativeFunction(native_tan), True)

    def native_asin(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.asin(x)
        return inter.NumberValue(y)
    env.declare("asin", inter.NativeFunction(native_asin), True)

    def native_acos(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.acos(x)
        return inter.NumberValue(y)
    env.declare("acos", inter.NativeFunction(native_acos), True)

    def native_atan(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.atan(x)
        return inter.NumberValue(y)
    env.declare("atan", inter.NativeFunction(native_atan), True)

    def native_atan2(arguments: list[inter.RuntimeValue]):
        x1 = arguments[0].value
        x2 = arguments[1].value
        y = math.atan2(x1, x2)
        return inter.NumberValue(y)
    env.declare("atan2", inter.NativeFunction(native_atan2), True)

    env.rng = random.Random(0)

    def native_rand_seed(arguments: list[inter.RuntimeValue]):
        seed = arguments[0].value
        env.rng = random.Random(seed)
    env.declare("__rand_seed__", inter.NativeFunction(native_rand_seed), True)

    def native_rand_seed(arguments: list[inter.RuntimeValue]):
        output = env.rng.random()
        return inter.NumberValue(output)
    env.declare("__rand_value__", inter.NativeFunction(native_rand_seed), True)

    def native_round(arguments: list[inter.RuntimeValue]):
        input = arguments[0].value
        output = round(input)
        return inter.NumberValue(output)
    env.declare("round", inter.NativeFunction(native_round), True)

    def native_isnan(arguments: list[inter.RuntimeValue]):
        input = arguments[0].value
        output = math.isnan(input)
        return inter.NumberValue(output)
    env.declare("isnan", inter.NativeFunction(native_isnan), True)

    def native_isinf(arguments: list[inter.RuntimeValue]):
        input = arguments[0].value
        output = math.isinf(input)
        return inter.NumberValue(output)
    env.declare("isinf", inter.NativeFunction(native_isinf), True)

    def native_sleep(arguments: list[inter.RuntimeValue]):
        milliseconds = arguments[0].value
        time.sleep(milliseconds / 1000)
        return inter.NoneValue()
    env.declare("sleep", inter.NativeFunction(native_sleep), True)

    def native_input(_arguments: list[inter.RuntimeValue]):
        return inter.StringValue(input())
    env.declare("input", inter.NativeFunction(native_input), True)

    env.declare("None", inter.NoneValue(), True)
    env.declare("inf", inter.NumberValue(float("inf")), True)
    env.declare("nan", inter.NumberValue(float("nan")), True)

    _run_builtin_code(env)

    return env

def _run_builtin_code(env: inter.Environment):
    tok = tokenize(builtin)
    ast = Parser().parse(tok)
    interpret(ast, env)

builtin = """

const int True = 1
const int False = 0

const int pi = 3.141592653589793238462643
const int euler = 2.718281828459045
const int tau = 6.283185307179586

fn floor(int x) int:
    return x // 1

# random (RNG) stuff
const int RAND_MAX = 2**32 - 1 # 0xFFFFFFFF

fn rand() int:
    return (RAND_MAX * __rand_value__()) // 1

fn srand(int seed) int:
    __rand_seed__(seed)

fn sqrt(int x) int:
    return x ** 0.5

fn degrees(int x) int:
    return x / pi * 180

fn radians(int x) int:
    return x * pi / 180

# fn abs(int value) int:
#     if value >= 0:
#         return value
#     return -value

fn pow(int base, int exponent) int:
    return base**exponent

# fn max(int in1, int in2) int:
#     if in1 > in2:
#         return in1
#     return in2

# fn min(int in1, int in2) int:
#     if in1 < in2:
#         return in1
#     return in2


"""