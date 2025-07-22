from flolang.lexer import tokenize
from flolang.abstract_source_tree import Parser
from flolang.interpreter import interpret
from flolang.native import create_default_environment as default_environment, to_native
from flolang.debugtools import print_ast
from flolang.intermediate import IntermediateEmitter


def parse(tok):
    return Parser().parse(tok)


def eval(expression: str, env=None, filename="__runtime__", shebang="#!script"):
    if shebang:
        full_expression = shebang + "\n" + expression
    else:
        full_expression = expression
    tok = tokenize(full_expression, filename)
    ast = parse(tok)
    print_ast(ast)  # TODO: remove this and make a test which does execute it
    if not env:
        env = default_environment()
    val = interpret(ast, env)
    # IntermediateEmitter(ast)
    return to_native(val)


def eval_parse(expression: str, filename="__runtime__", shebang="#!script"):
    if shebang:
        full_expression = shebang + "\n" + expression
    else:
        full_expression = expression
    tok = tokenize(full_expression, filename)
    ast = parse(tok)
    print_ast(ast)  # TODO: remove this and make a test which does execute it
    return ast
