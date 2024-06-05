from lexer import tokenize
from abstract_source_tree import Parser


def run1():
    print(tokenize("+-*===hello"))
    print(tokenize("a10 + a2"))
    print(tokenize("10 + 20.2"))

def run2():
    print("flolang v0.1 by ftobler")
    while True:
        # try:
            p = Parser()
            print("# ", end="")
            t = tokenize(input())
            print(t)
            ast = p.parse(t)
            print(ast.json())
        # except Exception as e:
        #     print(e)

def run3():
    with open("code.txt", "r") as f:
        code = f.read()
        p = Parser()
        t = tokenize(code)
        print(t)
        ast = p.parse(t)
        import json
        print(ast.json())
        # print(json.dumps(json.loads(str(ast.json()).replace("'", '"')), indent=4))


if __name__ == "__main__":
    run2()