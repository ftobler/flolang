from .lexer import tokenize
from .abstract_source_tree import Parser
from .interpreter import interpret
from .native import create_default_environment as default_environment, to_native

def parse(tok):
    return Parser().parse(tok)