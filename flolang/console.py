from colorama import Fore, Style  # , Back
from flolang.debugtools import print_ast


def parse_arguments(argv):
    # note: arguments at this stage are
    # ['path/to/flolang']
    # ['path/to/flolang', 'arg']
    args = argv[1:]
    switches = []
    while len(args):
        arg = args[0]
        if arg.startswith("--"):
            switches.append(arg)
            args = args[1:]  # consume this arg
        elif arg.startswith("-"):
            switches += list(arg[1:])
            args = args[1:]  # consume this arg
        else:
            break
    return switches, args


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
