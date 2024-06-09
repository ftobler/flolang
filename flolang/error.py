
class RuntimeException(Exception):
    pass


class ParserError(Exception):
    pass


class TokenError(Exception):
    pass


def runtime_error(comment: str, loc=None):
    if loc:
        # file = loc.start.symbols[0]
        # line_nr = loc.start.symbols[1]
        # full_line = loc.start.symbols[3]
        # start = loc.start.symbols[2]
        # end = loc.end.symbols[2]
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
    raise RuntimeException(message)


def parser_error(comment: str, start_token, end_token):
    # file = start_token.symbols[0]
    # line_nr = start_token.symbols[1]
    # full_line = start_token.symbols[3]
    # start = start_token.symbols[2]
    # end = end_token.symbols[2]
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


def error_symbol(comment: str, symbols: tuple):
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


