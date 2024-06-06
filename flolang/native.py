import flolang.interpreter as inter
import time
import math
import random

from flolang.lexer import tokenize
from flolang.abstract_source_tree import Parser
from flolang.interpreter import interpret

def to_native(val : inter.RuntimeValue):
    return val.value

def create_default_environment():
    env = inter.Environment()

    _run_builtin_code(env)

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

    env.declare("None", inter.NoneValue(), True)

    return env

def _run_builtin_code(env: inter.Environment):

    tok = tokenize(builtin)
    ast = Parser().parse(tok)
    interpret(ast, env)

builtin = """

const int pi = 3.141592653589793238462643
const int euler = 2.718281828459045

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

const int True = 1
const int False = 0

"""