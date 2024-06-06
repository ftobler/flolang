
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
        try:
            print("# ", end="")
            t = tokenize(input())
            print(t)
            ast = parse(t)
            print(ast.json())
            value = interpret(ast, env)
            print(value)
        except Exception as e:
            print(e)



def main_func():
    """
    entry case for python package entry_points console_scripts
    """
    main()


# entry case for standalone run
if __name__ == "__main__":
    main()