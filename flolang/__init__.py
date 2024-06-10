from .lexer import tokenize
from .abstract_source_tree import Parser
from .interpreter import interpret
from .native import create_default_environment as default_environment, to_native
from .debugtools import print_ast

def parse(tok):
    return Parser().parse(tok)


def eval(expression: str, env=None, filename="__runtime__", shebang="#!script"):
    if shebang:
        full_expression = shebang + "\n" + expression
    else:
        full_expression = expression
    tok = tokenize(full_expression, filename)
    ast = parse(tok)
    print_ast(ast)  # TODO: remove this
    if not env:
        env = default_environment()
    val = interpret(ast, env)
    return to_native(val)


def eval_parse(expression: str, filename="__runtime__", shebang="#!script"):
    if shebang:
        full_expression = shebang + "\n" + expression
    else:
        full_expression = expression
    tok = tokenize(full_expression, filename)
    ast = parse(tok)
    print_ast(ast)  # TODO: remove this
    return ast
