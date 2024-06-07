
# if you want to execute this standalone
# then you could not have installed the package
# and therefore import flolang does not work because that would
# be the same directory. Need to add it to path so the "normal" import works.
if __name__ == "__main__":
    import sys
    import os

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(SCRIPT_DIR))


from flolang import tokenize, default_environment, parse, interpret


def main():
    print("flolang v0.1 by ftobler")
    env = default_environment()
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
        except Exception as e:
            if tok_copy: print(tok_copy)
            if ast: print(ast.json())
            if value: print(value)
            typename = type(e).__name__
            print(typename, ":", e)



def main_func():
    """
    entry case for python package entry_points console_scripts
    """
    main()


# entry case for standalone run
if __name__ == "__main__":
    main()