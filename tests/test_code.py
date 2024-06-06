from context import resolve_path
from flolang import tokenize, default_environment, parse, interpret


def run1():
    print(tokenize("+-*===hello"))
    print(tokenize("a10 + a2"))
    print(tokenize("10 + 20.2"))

def run2():
    print("flolang v0.1 by ftobler")
    env = default_environment()
    while True:
        # try:
            print("# ", end="")
            t = tokenize(input())
            print(t)
            ast = parse(t)
            print(ast.json())
            value = interpret(ast, env)
            print(value)
        # except Exception as e:
        #     print(e)

def run3():
    with open(resolve_path("test_code.txt"), "r") as f:
        code = f.read()
        t = tokenize(code)
        print(t)
        ast = parse(t)
        print(ast.json())
        # print(json.dumps(json.loads(str(ast.json()).replace("'", '"')), indent=4))


def run4():
    with open(resolve_path("test_code.txt"), "r") as f:
        code = f.read()
        tok = tokenize(code)
        ast = parse(tok)
        env = default_environment()
        value = interpret(ast, env)
        # print(value)

if __name__ == "__main__":
    run4()