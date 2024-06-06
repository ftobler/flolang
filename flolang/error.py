


def error(comment: str, symbols: tuple):
    file, line_nr, line_pos, full_line = symbols
    message = error_text(comment, full_line, file, line_nr, line_pos)
    raise Exception(message)

def warning(comment: str, symbols: tuple):
    file, line_nr, line_pos, full_line = symbols
    message = error_text(comment, full_line, file, line_nr, line_pos)
    print(message)


def error_text(comment, full_line, file=None, line_nr=0, line_pos=0):
    indicator = " " * line_pos + "^"
    filename = "None"
    if file != None:
        filename = '"' + file + '"'
    msg = "File %s, line %d.\n%s\n%s\n%s" % (filename, line_nr, full_line, indicator, comment)
    return msg


