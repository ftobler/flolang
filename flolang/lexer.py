from enum import auto
import re
from .error import error

ignores = [" ", "\t", "\n", "\r"]

# special tokens requiring custom code
EOF = 0
IDENTIFIER = 1
NUMBER = 2
FLOAT = 3
STRING = 4
BUILTINTYPE = 5
# use idents "    " like python to denote blocks. But the lexer translates this to
# a block start and end token, which do not exist in the source code itself.
# Could easyly be replace by "{" and "}".
# The colong denoting the start of a block is a independent token.
BLOCKSTART = 6
BLOCKEND = 7

# long string tokens requiring direct string compare
# these must be handled before the smaller tokens as duplicated characters can lead
# to wrong matching
# IDENT = "    "
COMPARE = "=="
NOTCOMPARE = "!="
INTDIV = "//"
BIGGEREQ = ">="
SMALLEREQ = "<="
POW = "**"
INCREMENT = "++"
DECREMENT = "--"
ASSIGNADD = "+="
ASSIGNSUB = "-="
ASSIGNMUL = "*="
ASSIGNDIV = "/="
ASSIGNREM = "%="
ASSIGNBITAND = "&="
ASSIGNBITXOR = "^="
ASSIGNBITOR = "|="
string_tokens = [
    COMPARE, INTDIV, BIGGEREQ, SMALLEREQ, POW, INCREMENT, DECREMENT,
    ASSIGNADD, ASSIGNSUB, ASSIGNMUL, ASSIGNDIV, ASSIGNREM, ASSIGNBITAND,
    ASSIGNBITXOR, ASSIGNBITOR
]

# smaller string tokens consisting only of 1 character.
# Must match them after long string tokens as wrong matching
# could occur
DOT = "."
COLON = ":"
COMMA = ","
COURVE_L = "("
COURVE_R = ")"
SQUARE_L = "["
SQUARE_R = "]"
WIGGLE_L = "{"
WIGGLE_R = "}"
PLUS = "+"
MINUS = "-"
MUL = "*"
DIV = "/"
MOD = "%"
ASSIGN = "="
BIGGER = ">"
SMALLER = "<"
SHIFTRIGHT = ">>"
SHIFTLEFT = "<<"
BITOR = "|"
BITAND = "&"
BITNOT = "~"
XOR = "^"
ELVIS = "?"
small_tokens = [
    DOT, COLON, COMMA, COURVE_L, COURVE_R, SQUARE_L, SQUARE_R, WIGGLE_L,
    WIGGLE_R, PLUS, MINUS, MUL, DIV, MOD, POW, ASSIGN, BIGGER, SMALLER,
    SHIFTRIGHT, SHIFTLEFT, BITOR, BITAND, BITNOT, XOR, ELVIS
]

# keyword string tokens
# as these are alphanumeric they could be matches with names
AND = "and"
OR = "or"
NOT = "not"
FUNCTION = "fn"
CLASS = "class"
ENUM = "enum"
IMPORT = "import"
FROM = "from"
IF = "if"
ELSE = "else"
WHILE = "while"
FOR = "for"
RETURN = "return"
NONE = "None"
VAR = "var"
CONST = "const"
PASS = "pass"
IN = "in"
IS = "is"
keyword_tokens = [
    AND, OR, NOT, FUNCTION, CLASS, ENUM, IMPORT, FROM, IF, ELSE, WHILE,
    FOR, RETURN, NONE, VAR, CONST, PASS, IN, IS
]

# keywords for types
INT = "int"
OBJ = "obj"
STR = "str"
BOOL = "bool"
I8 = "i8"
U8 = "u8"
I16 = "i16"
U16 = "u16"
I32 = "i32"
U32 = "u32"
I64 = "i64"
U64 = "u64"
F32 = "f32"
F64 = "f64"
CHAR = "char"
variable_tokens = [
    INT, OBJ, STR, BOOL, I8, U8, I16, U16, I32, U32, I64, U64, F32, F64, CHAR
]

# Counts the number of leading spaces in a string.
def count_leading_spaces(string: str) -> int:
    count = 0
    for char in string:
        if char != ' ':
            break
        count += 1
    return count

def count_idents(string: str, symbols: tuple) -> int:
    spaces = count_leading_spaces(string)
    if spaces % 4 == 0:
        return spaces // 4
    error("indentation is not a multiple of 4 (its %d)." % spaces, symbols)

def consume_idents(line: str, ident: int) -> str:
    return line[(ident*4):]

class Token:
    def __init__(self, symbols: tuple, type: any, value: any=None):
        self.type = type
        self.value = value
        #debug symbols. If anything goes wrong, want to have the information which line is affected
        # self.filename, self.line_nr, self.line_pos, self.line = symbols
        self.symbols = symbols
    def __repr__(self):
        type_str = ""
        if isinstance(self.type, str):
            type_str = "'%s'" % self.type
        elif self.type == EOF:
            type_str = "EOF"
        elif self.type == IDENTIFIER:
            type_str = "IDENTIFIER"
        elif self.type == NUMBER:
            type_str = "NUMBER"
        elif self.type == FLOAT:
            type_str = "FLOAT"
        elif self.type == STRING:
            type_str = "STRING"
        elif self.type == BUILTINTYPE:
            type_str = "BUILTINTYPE"
        elif self.type == BLOCKSTART:
            type_str = "BLOCKSTART"
        elif self.type == BLOCKEND:
            type_str = "BLOCKEND"
        else:
            raise Exception("self.type is something unknown %s. Type not added to Token representation." % str(self.type))
        if self.value:
            return "{%s, '%s'}" % (type_str, self.value)
        return "{%s}" % (type_str)

def remove_comments(line):
    # removes the comments from the source line.
    # note that it is enforced that the '#' has a space before and after.
    # except the comment is at the start of the input.
    return re.sub("(?:^| * )#(?: .*|$)", "", line)

def starts_with_alphanumeric(string, prefix):
    if string.startswith(prefix):
        if len(string) > len(prefix):
            return not string[len(prefix)].isalnum()
    return False

def tokenize(sourcecode: str, filename: str=None) -> list[Token]:
    tokens = []
    tokenlist_symbolic = string_tokens + small_tokens
    tokenlist_symbolic.sort()
    tokenlist_symbolic.reverse()
    tokenlist_alphanumeric = keyword_tokens + variable_tokens
    tokenlist_alphanumeric.sort()
    tokenlist_alphanumeric.reverse()
    lines = sourcecode.splitlines()
    current_ident = 0 # everything starts out as not idented
    for line_nr, full_line in enumerate(lines):
        source = remove_comments(full_line)
        source_len = len(source)
        symbols = (filename, line_nr, 0, full_line)

        # evaluate indentation changes
        ident = count_idents(source, symbols)
        source = consume_idents(source, ident)
        while ident > current_ident:
            tokens.append(Token(symbols, BLOCKSTART))
            current_ident += 1
        while ident < current_ident:
            tokens.append(Token(symbols, BLOCKEND))
            current_ident -= 1

        while len(source):
            line_pos = source_len - len(source)
            found = False
            symbols = (filename, line_nr, line_pos, full_line)

            # search the basic symbolic tokens
            # this is combined to be able to distinguish '+' from '+='.
            # it is also the reason the tokenlist is sorted and reversed to first match '+'
            for s in tokenlist_symbolic:
                # if source.startswith(s):
                if source.startswith(s):
                    if s in variable_tokens:
                        tokens.append(Token(symbols, BUILTINTYPE, s))
                        source = source[len(s):]
                        found = True
                        break
                    else:
                        tokens.append(Token(symbols, s))
                        source = source[len(s):]
                        found = True
                        break

            # search for the basic alphanumeric tokens
            # also includes builtin type matches
            # this is combined to be able to distinguish 'in' from 'int'.
            # it is also the reason the tokenlist is sorted and reversed to first match 'in'
            # this uses starts_with_alphanumeric(..) to make sure a keyword is not mached in a
            # identifier: e.g keyword 'fn' must not match in identifier 'function'
            if not found:
                for s in tokenlist_alphanumeric:
                    if starts_with_alphanumeric(source, s):
                        if s in variable_tokens:
                            tokens.append(Token(symbols, BUILTINTYPE, s))
                            source = source[len(s):]
                            found = True
                            break
                        else:
                            tokens.append(Token(symbols, s))
                            source = source[len(s):]
                            found = True
                            break

            # search for names
            if not found:
                match = re.search("^[a-zA-Z_]+[a-zA-Z_0-9]*", source)
                if match:
                    identifier = match[0]
                    tokens.append(Token(symbols, IDENTIFIER, identifier))
                    source = source[len(identifier):]
                    found = True

            # search for hex integers
            if not found:
                match = re.search("^0x[0-9a-fA-F]+", source)
                if match:
                    number = match[0]
                    #it is a valid integer but given in hex format
                    tokens.append(Token(symbols, NUMBER, number))
                    source = source[len(number):]
                    found = True

            # search for floats or integers
            if not found:
                match = re.search("^[0-9\.]+(E[0-9]+|)", source)
                if match:
                    number = match[0]
                    match2 = re.search("E|\.", number)
                    if (match2):
                        # found a float
                        tokens.append(Token(symbols, FLOAT, number))
                        source = source[len(number):]
                        found = True
                    else:
                        # it is still a valid integer
                        tokens.append(Token(symbols, NUMBER, number))
                        source = source[len(number):]
                        found = True

            # search for a string literal with double quotes "
            if not found:
                match = re.search('^"((?:[^"\\\\]*(?:\\\\.[^"\\\\]*)*))"', source)
                if match:
                    string = match[1] #need group 1 containing the string without "
                    tokens.append(Token(symbols, STRING, string))
                    source = source[len(match[0]):]
                    found = True

            # ignore ignores if need be
            if not found:
                if source[0] in ignores:
                    source = source[1:]
                    found = True

            # assert any remaining problems
            if not found:
                error("Encountered unknown token in sourcecode.", symbols)

        if len(tokens):
            last_token = tokens[-1]
            if last_token.type is RETURN:
                last_token.value = 1


    # insert the needed amount of block endings according current operating ident.
    while current_ident > 0:
        tokens.append(Token(symbols, BLOCKEND))
        current_ident -= 1

    if len(lines):
        symbols = (filename, len(lines) - 1, len(lines[-1]) - 1, lines[-1])
    else:
        symbols = (filename, 0, 0, "")
    tokens.append(Token(symbols, EOF))
    return tokens


if __name__ == "__main__":
    print(tokenize("+-*===hello"))
    print(tokenize("a10 + a2"))
    print(tokenize("10 + 20.2"))
    print(tokenize('import <stdio-h>'))
    print(tokenize('import "stdio-h" #comment'))
    print(tokenize('import "stdi\\\"o-h"'))
    print(tokenize('let int a = 5    #comment'))
    print(tokenize('let int a = d    #comment'))
    print(tokenize("""
def main():
    pass
    """))