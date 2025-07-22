
class Symbols:
    def __init__(self, filename: str, line_nr: int, line_pos: int, line: str):
        self.filename = filename
        self.line_nr = line_nr
        self.line_pos = line_pos
        self.line = line
        if line_pos < 0 or line_nr < 0:
            raise LocationError("line_nr or line_pos out of range")

    def unpack(self):
        return self.filename, self.line_nr, self.line_pos, self.line


class CompileException(Exception):
    pass


class ParserError(Exception):
    pass


class TokenError(Exception):
    pass


class LocationError(Exception):
    pass


class IntermediateError():
    pass


def compile_error(comment: str, loc=None):
    if loc:
        file = loc.start.symbols.filename
        line_nr = loc.start.symbols.line_nr
        full_line = loc.start.symbols.line
        start = loc.start.symbols.line_pos
        end = loc.end.symbols.line_pos
        length = end - start + loc.end.len()
        if length <= 0:
            length = 1
    else:
        file = None
        line_nr = 0
        start = 0
        length = 0
        full_line = ""
    message = error_text(comment, full_line, file, line_nr, start, length)
    raise CompileException(message)


def parser_error(comment: str, start_token, end_token):
    file = start_token.symbols.filename
    line_nr = start_token.symbols.line_nr
    full_line = start_token.symbols.line
    start = start_token.symbols.line_pos
    end = end_token.symbols.line_pos
    length = end - start + end_token.len()
    if length <= 0:
        length = 1
    message = error_text(comment, full_line, file, line_nr, start, length)
    raise ParserError(message)


def error_token(comment: str, token):
    error_symbol(comment, token.symbols)


def error_symbol(comment: str, symbols: Symbols):
    message = error_text(comment, symbols.line, symbols.filename, symbols.line_nr, symbols.line_pos)
    raise TokenError(message)


def error_text(comment, full_line, file=None, line_nr=0, line_pos=0, length=1):
    indicator = " " * line_pos + "^" * length
    filename = "None"
    if file is not None:
        filename = '"' + file + '"'
    msg = "File %s, line %d.\n%s\n%s\n%s" % (filename, line_nr, full_line,
                                             indicator, comment)
    return msg
