
import time
import math
import random

from flolang.lexer import tokenize
from flolang.abstract_source_tree import Parser
import flolang.interpreter as inter


def to_native(val: inter.RuntimeValue):
    if isinstance(val, inter.NoneValue):
        return None
    if isinstance(val, inter.RuntimeFunction):
        return "<" + val.variant + ">"
    if hasattr(val, "value"):
        return val.value
    return "<" + val.variant + ">"


def create_default_environment():
    env = inter.Environment()

    def native_print(arguments: list[inter.RuntimeValue]):
        args = [runtime_var.value for runtime_var in arguments]
        print(*args)
    env.declare_global("print", inter.NativeFunction(native_print), True, None)

    def native_time(arguments: list[inter.RuntimeValue]):
        return inter.FloatValue(time.time())
    env.declare_global("time", inter.NativeFunction(native_time), True, None)

    def native_sin(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.sin(x)
        return inter.FloatValue(y)
    env.declare_global("sin", inter.NativeFunction(native_sin), True, None)

    def native_cos(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.cos(x)
        return inter.FloatValue(y)
    env.declare_global("cos", inter.NativeFunction(native_cos), True, None)

    def native_tan(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.tan(x)
        return inter.FloatValue(y)
    env.declare_global("tan", inter.NativeFunction(native_tan), True, None)

    def native_asin(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.asin(x)
        return inter.FloatValue(y)
    env.declare_global("asin", inter.NativeFunction(native_asin), True, None)

    def native_acos(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.acos(x)
        return inter.FloatValue(y)
    env.declare_global("acos", inter.NativeFunction(native_acos), True, None)

    def native_atan(arguments: list[inter.RuntimeValue]):
        x = arguments[0].value
        y = math.atan(x)
        return inter.FloatValue(y)
    env.declare_global("atan", inter.NativeFunction(native_atan), True, None)

    def native_atan2(arguments: list[inter.RuntimeValue]):
        x1 = arguments[0].value
        x2 = arguments[1].value
        y = math.atan2(x1, x2)
        return inter.FloatValue(y)
    env.declare_global("atan2", inter.NativeFunction(native_atan2), True, None)

    env.rng = random.Random(0)

    def native_rand_seed(arguments: list[inter.RuntimeValue]):
        seed = arguments[0].value
        env.rng = random.Random(seed)
        return inter.NoneValue()
    env.declare_global("__rand_seed__", inter.NativeFunction(native_rand_seed), True, None)

    def native_rand_value(arguments: list[inter.RuntimeValue]):
        output = env.rng.random()
        return inter.FloatValue(output)
    env.declare_global("__rand_value__", inter.NativeFunction(native_rand_value), True, None)

    def native_round(arguments: list[inter.RuntimeValue]):
        input = arguments[0].value
        output = round(input)
        return inter.IntValue(output)
    env.declare_global("round", inter.NativeFunction(native_round), True, None)

    def native_isnan(arguments: list[inter.RuntimeValue]):
        input = arguments[0].value
        output = math.isnan(input)
        return inter.BooleanValue(output)
    env.declare_global("isnan", inter.NativeFunction(native_isnan), True, None)

    def native_isinf(arguments: list[inter.RuntimeValue]):
        input = arguments[0].value
        output = math.isinf(input)
        return inter.BooleanValue(output)
    env.declare_global("isinf", inter.NativeFunction(native_isinf), True, None)

    def native_sleep(arguments: list[inter.RuntimeValue]):
        milliseconds = arguments[0].value
        time.sleep(milliseconds / 1000)
        return inter.NoneValue()
    env.declare_global("sleep", inter.NativeFunction(native_sleep), True, None)

    def native_input(_arguments: list[inter.RuntimeValue]):
        return inter.StringValue(input())
    env.declare_global("input", inter.NativeFunction(native_input), True, None)

    env.declare_global("None", inter.NoneValue(), True, None)
    env.declare_global("inf", inter.FloatValue(float("inf")), True, None)
    env.declare_global("nan", inter.FloatValue(float("nan")), True, None)

    _run_builtin_code(env)

    return env


def _run_builtin_code(env: inter.Environment):
    tok = tokenize(builtin)
    ast = Parser().parse(tok)
    inter.interpret(ast, env)


builtin = """
#!script

static bool True = 1
static bool False = 0

static float pi = 3.141592653589793238462643
static float euler = 2.718281828459045
static float tau = 6.283185307179586

fn floor(float x) int:
    return x // 1

fn int(float x) int:
    return x // 1

# random (RNG) stuff
static int RAND_MAX = 2**31 - 1 # 0xFFFFFFFF

fn rand() int:
    return (RAND_MAX * __rand_value__()) // 1

fn srand(int seed) int:
    __rand_seed__(seed)

fn sqrt(float x) float:
    return x ** 0.5

fn degrees(float x) float:
    return x / pi * 180

fn radians(float x) float:
    return x * pi / 180

fn abs(float value) float:
    if value >= 0:
        return value
    return -value

fn pow(float base, float exponent) float:
    return base**exponent

fn max(float in1, float in2) float:
    if in1 > in2:
        return in1
    return in2

fn min(float in1, float in2) float:
    if in1 < in2:
        return in1
    return in2


"""
