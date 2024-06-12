import sys

# if you want to execute this standalone
# then you could not have installed the package
# and therefore import flolang does not work because that would
# be the same directory. Need to add it to path so the "normal" import works.
if __name__ == "__main__":
    import os

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))


from flolang import tokenize, default_environment, parse, interpret, to_native, eval
from colorama import Fore, Style  # , Back
from flolang.debugtools import print_ast


pretty_print = False

def set_pretty_print(value: bool):
    global pretty_print
    pretty_print = value


def print_exception(e, tok_copy, ast, value):
    if pretty_print:
        print(Fore.LIGHTBLACK_EX, end="")
        if tok_copy:
            print(tok_copy)
        if ast:
            print_ast(ast)
        if value:
            print(value)
        print(Fore.YELLOW, end="")
        typename = type(e).__name__
        print(Fore.RED, end="")
        print(typename, ":", e)
        print(Style.RESET_ALL, end="")
    else:
        if tok_copy:
            print(tok_copy)
        if ast:
            print_ast(ast)
        if value:
            print(value)
        typename = type(e).__name__
        print(typename, ":", e)


def main_console(arguments=None):
    print("flolang v0.1 by ftobler")
    env = default_environment()
    env.declare_global("_", interpret(parse(tokenize("None")), env), True, None)
    interpret(parse(tokenize("#!script")), env)
    if arguments:
        declare_arguments(env, arguments)
    while True:
        tok_copy = None
        ast = None
        value = None
        try:
            print("# ", end="")
            tok = tokenize(input(), filename="__interpreter__")
            tok_copy = tok.copy()
            ast = parse(tok)
            value = interpret(ast, env)
            env.assign("_", value, None)
            print(to_native(value))
        except Exception as e:
            print_exception(e, tok_copy, ast, value)


def declare_arguments(env, arguments):
    # declare argument array in environment
    command = "static int __argv = " + str(arguments).replace("'", '"')
    eval(command, env=env, shebang=None)


def main_execute(script_file, arguments):
    with open(script_file, "r") as f:
        tok_copy = None
        ast = None
        value = None
        try:
            code = f.read()
            tok = tokenize(code)
            tok_copy = tok.copy()
            ast = parse(tok)
            env = default_environment()
            declare_arguments(env, arguments)
            value = interpret(ast, env)
            # print(value)
        except Exception as e:
            print_exception(e, tok_copy, ast, value)


def parse_arguments(argv):
    # note: arguments at this stage are
    # ['path/to/flolang']
    # ['path/to/flolang', 'arg']
    args = argv[1:]
    switches = []
    while len(args):
        arg = args[0]
        if arg.startswith("-"):
            switches.append(arg[1:])
            args = args[1:]  # consume this arg
        else:
            break
    return switches, args


def get_help():
    return """run script:
usage: flolang [script] [arg] [arg]...

run interpreter:
usage: flolnang -i [arg] [arg]...

run interpreter (default)
usage: flolang

additional switches:
    -p       disable pretty print
    -c       compile script
    -help    prints help (this text)
"""


def print_help():
    print(get_help(), end="")


def main():
    switches, args = parse_arguments(sys.argv)
    if "p" in switches:
        set_pretty_print(False)
    if "help" in switches:
        print_help()
        return
    if "c" in switches:
        raise Exception("compiling is unimplemented")
    if "i" in switches:
        main_console(args)
        return
    if len(args):
        script_file = args[0]
        arguments = args[1:]
        main_execute(script_file, arguments)
    else:
        main_console()


def main_func():
    """
    entry case for python package entry_points console_scripts
    """
    main()


# entry case for standalone run
if __name__ == "__main__":
    main()