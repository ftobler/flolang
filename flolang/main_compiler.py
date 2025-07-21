from flolang.console import parse_arguments, print_exception, set_pretty_print
import sys
from flolang import tokenize, default_environment, parse, interpret, to_native, eval
from flolang.debugtools import print_ast
from flolang.argument_parser import ArgumentParser
import os
from io import TextIOWrapper


def declare_arguments(env, arguments):
    # declare argument array in environment
    command = "static int __argv = " + str(arguments).replace("'", '"')
    eval(command, env=env, shebang=None)


def switch(switches, switch):
    return "--" + switch in switches or switch[0] in switches


def auto_filename(file_name, input_file):
    if file_name:
        return file_name
    name, ext = os.path.splitext(input_file)
    return name


def file_ending(file_name, ending):
    if not file_name.endswith(ending):
        return file_name + ending
    return file_name


def compile(code: str, f: TextIOWrapper, emit: str):
    if emit == "token":
        tok = tokenize(code)
        for t in tok:
            print(t, file=f)

    elif emit == "ast":
        tok = tokenize(code)
        ast = parse(tok)
        print_ast(ast, file=f)

    elif emit == "ir":
        raise NotImplementedError("emit ir is not supported")

    else:
        raise ValueError(f"Unknown emit type: {emit}")


def main_func_compiler():
    ap = ArgumentParser(
        sys.argv,
        ["pretty", "help", "token"],
        ["emit", "output"],)

    if ap.switch("pretty"):
        set_pretty_print(True)

    if ap.switch("help"):
        raise NotImplementedError()

    output = ap.key("output")
    if output:
        assert len(ap.args()) == 1, "only one file allowed when output specified"

    emit = ap.key("emit")

    for input_file in ap.args():
        with open(input_file, "r") as f:
            code = f.read()
            output_file = file_ending(auto_filename(output, input_file), "." + emit)
            with open(output_file, "w") as out:
                compile(code, out, emit)
