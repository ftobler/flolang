
# if you want to execute this standalone
# then you could not have installed the package
# and therefore import flolang does not work because that would
# be the same directory. Need to add it to path so the "normal" import works.
if __name__ == "__main__":
    import sys
    import os

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))


from flolang import tokenize, default_environment, parse, interpret, to_native
from colorama import Fore, Back, Style

pretty_print = True

def main():
    print("flolang v0.1 by ftobler")
    env = default_environment()
    env.declare("_", interpret(parse(tokenize("None")), env), True, None)
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
            if pretty_print: print(Fore.LIGHTBLACK_EX, end="")
            if tok_copy: print(tok_copy)
            if ast: print(ast.json())
            if value: print(value)
            typename = type(e).__name__
            if pretty_print: print(Fore.RED, end="")
            print(typename, ":", e)
            if pretty_print: print(Style.RESET_ALL, end="")



def main_func():
    """
    entry case for python package entry_points console_scripts
    """
    main()


# entry case for standalone run
if __name__ == "__main__":
    main()