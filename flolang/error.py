
def runtime_error(comment: str, loc=None):
    if loc:
        file = loc.start.symbols[0]
        line_nr = loc.start.symbols[1]
        full_line = loc.start.symbols[3]
        start = loc.start.symbols[2]
        end = loc.end.symbols[2]
        length = end - start
        if length <= 0:
            length = 1
    else:
        file = None,
        line_nr = 0
        start = 0
        length = 0
    message = error_text(comment, full_line, file, line_nr, start, length)
    raise Exception(message)


def error(comment: str, symbols: tuple):
    file, line_nr, line_pos, full_line = symbols
    message = error_text(comment, full_line, file, line_nr, line_pos)
    raise Exception(message)

def warning(comment: str, symbols: tuple):
    file, line_nr, line_pos, full_line = symbols
    message = error_text(comment, full_line, file, line_nr, line_pos)
    print(message)


def error_text(comment, full_line, file=None, line_nr=0, line_pos=0, length=1):
    indicator = " " * line_pos + "^" * length
    filename = "None"
    if file != None:
        filename = '"' + file + '"'
    msg = "File %s, line %d.\n%s\n%s\n%s" % (filename, line_nr, full_line, indicator, comment)
    return msg


