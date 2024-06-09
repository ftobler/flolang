
import flolang.lexer as lexer
from .lexer import Token
from .error import error_token, parser_error

class Location:
    def __init__(self, start: Token, end: Token):
        self.start = start
        self.end = end
    def __repr__(self):
        #
        line = self.start.symbols[3]
        start = self.start.symbols[2]
        end = self.end.symbols[2]
        if start < end:
            snippet = line[start:end+1]
            return '"' + snippet + '"'
        return str(self.start) + ".." + str(self.end)

class NoLocation(Location):
    def __init__(self):
        super().__init__(None, None)
    def __repr__(self):
        return "?"

class Statement:
    def __init__(self):
        self.kind = type(self).__name__
        self.loc = NoLocation()
    def __repr__(self):
        return str(self.json())
    def json(self):
        return vars(self)
    def location(self, start: Token, end: Token):
        self.loc = Location(start, end)
        return self

class Expression(Statement):
    pass

class Program(Statement):
    def __init__(self):
        super().__init__()
        self.body = []

class Type(Statement):
    def __init__(self, type: str, is_builtin: bool):
        super().__init__()
        self.type = type
        self.builtin = is_builtin

class VariableDeclaration(Statement):
    def __init__(self, mutable: bool, type: Type, identifier: str, value: Expression):
        super().__init__()
        self.mutable = mutable
        self.type = type
        self.identifier = identifier
        self.value = value

class LocalVariableDeclaration(VariableDeclaration):
    pass

class GlobalVariableDeclaration(VariableDeclaration):
    pass

class DynamicVariableDeclaration(VariableDeclaration):
    pass

class ClassMemberVariableDeclaration(VariableDeclaration):
    pass

class ParameterStatement(Statement):
    def __init__(self, mutable: bool, type: Type, identifier: str, default: Expression = None):
        super().__init__()
        self.mutable = mutable
        self.type = type
        self.identifier = identifier
        self.default = default

class BlockStatement(Statement):
    def __init__(self, body: list[Statement]):
        super().__init__()
        self.body = body

class FunctionDeclaration(Statement):
    def __init__(self, parameters: list[ParameterStatement], result: Type, identifier: str, body: BlockStatement):
        super().__init__()
        self.parameters = parameters
        self.result = result
        self.identifier = identifier
        self.body = body

class ClassMemberFunctionDeclaration(FunctionDeclaration):
    pass

class ClassDeclaration(Statement):
    def __init__(self, classname: str,
                functions: list[ClassMemberFunctionDeclaration],
                dynamics: list[ClassMemberVariableDeclaration],
                mutables: list[ClassMemberVariableDeclaration],
                constants: list[ClassMemberVariableDeclaration]
                ):
        super().__init__()
        self.classname = classname
        self.functions = functions
        self.dynamics = dynamics
        self.mutables = mutables
        self.constants = constants

class EnumFieldDeclaration(Statement):
    def __init__(self, identifier: str, value: Expression = None):
        super().__init__()
        self.identifier = identifier
        self.value = value

class EnumDeclaration(Statement):
    def __init__(self, enumname: str, fields: list[EnumFieldDeclaration]):
        super().__init__()
        self.enumname = enumname
        self.fields = fields

class AllocatorSwitch(Statement):
    def __init__(self, identifier: str):
        super().__init__()
        self.identifier = identifier

class IfExpression(Statement):
    def __init__(self, condition: Expression, consequent: BlockStatement, alternate: BlockStatement = None):
        super().__init__()
        self.test = condition
        self.consequent = consequent
        self.alternate = alternate

class ForExpression(Statement):
    def __init__(self, type: Type, identifier: str, body: BlockStatement, quantity_min: Expression, quantity_max: Expression):
        super().__init__()
        self.type = type
        self.identifier = identifier
        self.body = body
        self.quantity_min = quantity_min
        self.quantity_max = quantity_max

class WhileExpression(Statement):
    def __init__(self, condition: Expression, body: BlockStatement):
        super().__init__()
        self.condition = condition
        self.body = body

class ReturnExpression(Statement):
    value: Expression
    def __init__(self, value: Expression = None):
        super().__init__()
        self.value = value

class BreakExpression(Statement):
    def __init__(self):
        super().__init__()

class ContinueExpression(Statement):
    def __init__(self):
        super().__init__()

class UnreachableExpression(Statement):
    def __init__(self):
        super().__init__()

class AssignmentExpression(Expression):
    def __init__(self, assignee: Expression, value: Expression, operator: str):
        super().__init__()
        self.assignee = assignee
        self.value = value
        self.operator = operator

class BinaryExpression(Expression):
    def __init__(self, left: Expression, right: Expression, operator: str):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = operator

class UnaryBeforeExpression(Expression):
    def __init__(self, expr: Expression, operator: str):
        super().__init__()
        self.expr = expr
        self.operator = operator

class UnaryIdentifierBeforeExpression(Expression):
    def __init__(self, identifier: str, operator: str):
        super().__init__()
        self.identifier = identifier
        self.operator = operator

class UnaryIdentifierAfterExpression(Expression):
    def __init__(self, identifier: str, operator: str):
        super().__init__()
        self.identifier = identifier
        self.operator = operator

class CallExpression(Expression):
    def __init__(self, caller: Expression, arguments: list[Expression]):
        super().__init__()
        self.caller = caller
        self.arguments = arguments

class MemberExpression(Expression):
    def __init__(self, object: Expression, key: Expression, computed: bool):
        super().__init__()
        self.object = object
        self.key = key
        self.computed = computed #TODO unused?

class ShebangExpression(Expression):
    def __init__(self, shebang: str):
        super().__init__()
        self.shebang = shebang

class Literal(Expression):
    pass

class SimpleLiteral(Literal):
    pass

class Identifier(SimpleLiteral):
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

class NumericLiteral(SimpleLiteral):
    def __init__(self, value_raw: str):
        super().__init__()
        self.value_raw = value_raw
        if value_raw.startswith("0x"):
            self.value = int(value_raw, base=16)
        else:
            self.value = int(value_raw)

class FloatLiteral(SimpleLiteral):
    def __init__(self, value_raw: str):
        super().__init__()
        self.value_raw = value_raw
        self.value = float(value_raw)

class StringLiteral(SimpleLiteral):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

#dont count them to simple literals, because They are dynamic

class ObjectProperty(Literal):
    def __init__(self, key: str, value: Expression=None):
        super().__init__()
        self.key = key
        self.value = value

class ObjectLiteral(Literal):
    def __init__(self, properties: list[ObjectProperty]):
        super().__init__()
        self.properties = properties

class ListLiteral(Literal):
    def __init__(self, values: list[Expression]):
        super().__init__()
        self.values = values

class SetLiteral(Literal):
    def __init__(self, values: list[Expression]):
        super().__init__()
        self.values = values

class TupleLiteral(Literal):
    def __init__(self, values: list[Expression]):
        super().__init__()
        self.values = values




class Parser:
    def __init__(self):
        self.tokens: list[Token] # tokens from lexer

    def not_eof(self) -> bool:
        return self.tokens[0].type is not lexer.EOF

    def at(self) -> Token:
        return self.tokens[0]

    def eat(self) -> Token:
        return self.tokens.pop(0)

    def eat_expect(self, token_type: str, error_comment: any, loc_start: Token) -> Token:
        prev = self.eat()
        if prev.type is not token_type:
            parser_error(error_comment, loc_start, prev)
        return prev

    def at_expect(self, token_type: str, error_comment: any, loc_start: Token) -> Token:
        prev = self.at()
        if prev.type is not token_type:
            parser_error(error_comment, loc_start, prev)
        return prev

    def unimplemented(self):
        if self.not_eof():
            error_token("Unimplemented token encuntered in Source Code.", self.at())
        error_token("Unimplemented token encountered and End of File reached.", self.at())

    # make the AST (Abstract Syntax Tree)
    def parse(self, tokens: list[Token]) -> Program:
        self.tokens = tokens
        program = Program()
        self.program = program
        # parse until there is nothing left
        while self.not_eof():
            program.body.append(self.parse_statement())
        return program

    def parse_statement(self) -> Statement:
        type = self.at().type
        if type is lexer.LET or type is lexer.STATIC:
            return self.parse_var_declaration()
        if type is lexer.FUNCTION:
            return self.parse_function_declaration()
        if type is lexer.IF:
            return self.parse_if_declaration()
        if type is lexer.FOR:
            return self.parse_for_declaration()
        if type is lexer.WHILE:
            return self.parse_while_declatation()
        if type is lexer.RETURN:
            return self.parse_return_declaration()
        if type is lexer.BREAK:
            return self.parse_break_declaration()
        if type is lexer.CONTINUE:
            return self.parse_continue_declaration()
        if type is lexer.UNREACHABLE:
            return self.parse_unreachable_declaration()
        if type is lexer.SHEBANG:
            return self.parse_shebang()
        if type is lexer.CLASS:
            return self.parse_class()
        if type is lexer.ENUM:
            return self.parse_enum()
        if type is lexer.ALLOC:
            return self.parse_alloc()
        return self.parse_expression()

    # let a = (...)
    # static a = (...)
    # let mut a
    # let mut a = (...)
    # static mut a
    # static mut a = (...)
    def parse_var_declaration(self):
        loc_start = self.at()

        # let mut int a = (...)
        # ^^^
        # static mut int a = (...)
        # ^^^^^^
        # eat declaration keyword this is 'let' or 'static' for local and global scope$
        is_static = self.eat().type is lexer.STATIC

        # let mut int a = (...)
        #     ^^^
        # next up 'mut' might follow to declare it mutable
        is_mutable = False
        if self.at().type is lexer.MUT:
            is_mutable = True
            self.eat() # eat 'mut'

        # let mut int a = (...)
        #         ^^^
        type_start = self.at()
        if self.at().type is lexer.IDENTIFIER:
            type = Type(self.eat().value, False).location(type_start, self.at())
        elif self.at().type is lexer.BUILTINTYPE:
            type = Type(self.eat().value, True).location(type_start, self.at())
        else:
            parser_error("Expect identifier or builtin type for variable type declaration", loc_start, self.at())

        # let mut int indentifier = (...)
        #             ^^^^^^^^^^^
        identifier = self.eat_expect(lexer.IDENTIFIER, "Expect indentifier after type for variable declaration.", loc_start).value

        # let mut int a = (...)
        #               ^
        self.eat_expect(lexer.ASSIGN, "Expect '%s' following type and identifier for '%s' declaration." % (lexer.ASSIGN, loc_start.type), loc_start)

        # let mut int a = (...)
        #                 ^^^^^
        value = self.parse_expression()
        if is_static:
            return GlobalVariableDeclaration(is_mutable, type, identifier, value).location(loc_start, self.at())
        else:
            return LocalVariableDeclaration(is_mutable, type, identifier, value).location(loc_start, self.at())

    # fn foo():
    # fn foo(a, b, c) d:
    def parse_function_declaration(self, class_member_function=False):
        # fn foo():
        # ^^
        loc_start = self.eat() # eat 'fn' keyword

        # fn foo():
        #    ^^^
        identifier = self.eat_expect(lexer.IDENTIFIER, "Expect identifier after '%s' keyword." % lexer.FUNCTION, loc_start).value

        # fn foo(int a, int b):
        #       ^^^^^^^^^^^^^^
        args = self.parse_function_arguments()

        # fn foo(int a, int b) int:
        #                      ^^^
        # fn foo(int a, int b):
        #                    ~~   => None
        result = self.parse_next_type()

        # fn foo(int a, int b):
        #                     ^
        self.eat_expect(lexer.COLON, "Expect '%s' following function declaration." % lexer.COLON, loc_start)

        body = self.parse_block_declaration()

        if class_member_function:
            return ClassMemberFunctionDeclaration(args, result, identifier, body).location(loc_start, self.at())
        return FunctionDeclaration(args, result, identifier, body).location(loc_start, self.at())

    # (int a)
    # (int a, int b)
    # (int a, int b = 5)
    def parse_function_arguments(self) -> list[ParameterStatement]:
        loc_start = self.at()
        args: list[Type] = []

        # (int a, int b)
        # ^
        self.eat_expect(lexer.COURVE_L, "Expect function argument list beginning with '%s'." % lexer.COURVE_L, loc_start)

        while self.not_eof() and self.at().type is not lexer.COURVE_R:
            loop_loc_start = self.at()

            # (mut int a, int b)
            #  ^^^
            mutable = False
            if self.at().type is lexer.MUT:
                mutable = True
                self.eat()

            # (int a, int b)
            #  ^^^
            type = self.parse_next_type()
            if not type:
                parser_error("Unable to determine argument type", loop_loc_start, self.at())

            # (int name, int b)
            #      ^^^^
            identifier = self.eat_expect(lexer.IDENTIFIER, "Expect identifier in argument list.", loop_loc_start)

            # (int a = 5, int b)
            #        ^
            default = None #assume no default available
            if self.at().type is lexer.ASSIGN:
                #have a '=' sign here 'int b = 5'
                self.eat()
                default = self.parse_expression()

            # (int a, int b)
            #       ^
            # (int a, int b)
            #              ^
            # expect close ")" or if not expect a ","
            if self.at().type is not lexer.COURVE_R:
                # expect a ","
                self.eat_expect(lexer.COMMA, "Expected '%s' or '%s' following argument." % (lexer.COMMA, lexer.COURVE_R), loop_loc_start)

            args.append(ParameterStatement(mutable, type, identifier, default).location(loop_loc_start, self.at()))

        # (int a, int b)
        #              ^
        self.eat_expect(lexer.COURVE_R, "Expect function argument list ending with '%s'." % lexer.COURVE_R, loc_start)
        return args

    def parse_next_type(self) -> Type:
        loc_start = self.at()
        if self.at().type is lexer.IDENTIFIER:
            return Type(self.eat().value, False).location(loc_start, self.at())
        elif self.at().type is lexer.BUILTINTYPE:
            return Type(self.eat().value, True).location(loc_start, self.at())
        return None

    def parse_if_declaration(self):
        loc_start = self.at()
        # eat the 'if' or 'elif' keyword
        self.eat()
        # parse the expressional condition
        # if ...... :
        #    ^^^^^^
        test = self.parse_expression()
        self.eat_expect(lexer.COLON, "Expect '%s' after expression in '%s' statement." % (lexer.COLON, lexer.IF), loc_start)
        consequent_case = self.parse_block_declaration()

        at_type = self.at().type
        if at_type is lexer.ELSE:
            self.eat() # eat 'ELSE'
            self.eat_expect(lexer.COLON, "Expect '%s' after '%s' | '%s' keywords in '%s' condition." % (lexer.COLON, lexer.ELSE, lexer.ELIF, lexer.IF), loc_start)
            return IfExpression(test, consequent_case, self.parse_block_declaration()).location(loc_start, self.at())
        elif at_type is lexer.ELIF:
            return IfExpression(test, consequent_case, self.parse_if_declaration()).location(loc_start, self.at())

        # just a plain if without else
        return IfExpression(test, consequent_case, None).location(loc_start, self.at())

    def parse_block_declaration(self):
        # consutme ':'
        loc_start = self.at()

        # check if there is a ident change. This will create a BLOCKSTART token
        if self.at().type is lexer.BLOCKSTART:
            self.eat() # eat BLOCKSTART
            # self.eat_expect(lexer.BLOCKSTART, "Expect indented block body after function declaration.", loc_start)

            body = []
            pass_encountered = False
            while self.not_eof() and self.at().type is not lexer.BLOCKEND:
                if self.at().type is lexer.PASS:
                    self.eat()
                    pass_encountered = True
                    break
                body.append(self.parse_statement())

            if len(body) == 0 and not pass_encountered:
                parser_error(lexer.PASS, "Expect '%s' when block is empty." % lexer.PASS, loc_start, self.at())

            # lexer should create the blockend(s) already, so this message will probably never be seen
            self.eat_expect(lexer.BLOCKEND, "Expect indented block body to end before End of File.", loc_start)

        else:
            # if no separate indentation block is encountered, then that should be valid to make
            # inline if cases.
            # but only one item in body is allowed.
            body = [self.parse_statement()]


        return BlockStatement(body).location(loc_start, self.at())

    # for int n in 50:
    # for int n in {...}:
    # for int n in 0..50:
    # for int n in {...}..{...}:
    def parse_for_declaration(self):
        loc_start = self.at()
        # eat the 'for' keyword
        self.eat()

        # parse the type
        type = self.parse_next_type()
        if not type:
            parser_error("Unable to determine argument type", loc_start, self.at())

        # parse the variable identifier
        identifier = self.eat_expect(lexer.IDENTIFIER, "Expect identifier in argument list.", loc_start)

        # eat in keyword^
        # for int n in 0..50:
        #           ^^
        self.eat_expect(lexer.IN, "expect '%s' after identifier in '%s' declaration." % (lexer.IN, lexer.FOR), loc_start)

        # parse the (first) quantifier
        quantity_max = self.parse_expression()
        quantity_min = NumericLiteral("0")

        # check if a double dot is present
        # for int n in 0..50:
        #               ^^
        if self.at().type is lexer.DOTDOT:
            self.eat() # consume '..'
            quantity_min = quantity_max
            quantity_max = self.parse_expression() #parse the second quantifier

        # consume colon ':'
        self.eat_expect(lexer.COLON, "Expect '%s' after quantifier(s) in '%s' declaration." % (lexer.COLON, lexer.FOR), loc_start)

        # parse rest of body
        body = self.parse_block_declaration()

        return ForExpression(type, identifier, body, quantity_min, quantity_max).location(loc_start, self.at())

    # while (...):
    def parse_while_declatation(self):
        loc_start = self.at()
        # eat the 'while' keyword
        self.eat()
        # parse the expressional condition
        # while ...... :
        #       ^^^^^^
        expr = self.parse_expression()
        self.eat_expect(lexer.COLON, "Expect '%s' after expression in '%s' statement." % (lexer.COLON, lexer.WHILE), loc_start)
        body = self.parse_block_declaration()
        return WhileExpression(expr, body).location(loc_start, self.at())

    def parse_return_declaration(self):
        loc_start = self.at()

        # return (...)
        # ^^^^^^
        # eat the 'return' keyword
        value = self.eat().value

        # the current token might be on the next line or not. There is no way
        # the token system has this information because a new line is not a thing
        # that exists for that. Instead the value of the return keyword has been
        # annotated and is 1 for end of line and default None if there are more
        # tokens on the same line.
        if value == None:
            # return (...)
            #        ^^^^^
            right = self.parse_expression()
            self.skip_until_end_of_code_block(loc_start)
            return ReturnExpression(right).location(loc_start, self.at())
        return ReturnExpression().location(loc_start, self.at())

    def parse_break_declaration(self):
        loc_start = self.at()
        # eat the 'break' keyword
        self.eat()
        self.skip_until_end_of_code_block(loc_start)
        return BreakExpression().location(loc_start, self.at())

    def parse_continue_declaration(self):
        loc_start = self.at()
        # eat the 'continue' keyword
        self.eat()
        self.skip_until_end_of_code_block(loc_start)
        return ContinueExpression().location(loc_start, self.at())

    def parse_unreachable_declaration(self):
        loc_start = self.at()
        # eat the 'unreachable' keyword
        self.eat()
        # unreachable expression is put in to assert that control flow will never reach
        # this expression and when it does at runtime the program can abort or trap
        # Can stop parsing at this point until EOF or end of current code block.
        self.skip_until_end_of_code_block(loc_start)
        return UnreachableExpression().location(loc_start, self.at())

    # #:flolang
    def parse_shebang(self):
        # eat the shebang '#:' keyword
        # #:flolang
        # ^^^^^^^^^
        loc_start = self.eat()

        # this is the value at this point
        # #:flolang
        #   ^^^^^^^
        shebang_value = loc_start.value

        return ShebangExpression(shebang_value).location(loc_start, loc_start)

    def parse_class(self):
        # eat then 'class' keyword
        # class foo:
        # ^^^^^
        loc_start = self.eat()

        # class foo:
        #       ^^^
        classname = self.eat_expect(lexer.IDENTIFIER, "Identifier expected after '%s' keyword." % lexer.CLASS, loc_start).value
        self.eat_expect(lexer.COLON, "Expect '%s' after identifier in '%s'." % (lexer.COLON, lexer.CLASS), loc_start)
        self.eat_expect(lexer.BLOCKSTART, "Expect block statement after '%s' identifier in '%s'." % (lexer.COLON, lexer.CLASS), loc_start)

        # class body
        functions = []
        dynamics = []
        mutables = []
        constants = []
        while self.not_eof() and self.at().type is lexer.BLOCKEND:
            if self.at().type is lexer.FUNCTION:
                # fn foo():
                # ^^
                functions.append(self.parse_function_declaration(class_member_function=True))
            elif self.at().type is lexer.DYN:
                # dyn list i = []
                # ^^^
                dynamics.append(self.parse_class_member_variable_declaration())
            elif self.at().type is lexer.MUT:
                # mut int i
                # ^^^
                mutables.append(self.parse_class_member_variable_declaration())
            else:
                # int i = 0
                # ^^^
                constants.append(self.parse_class_member_variable_declaration())

        self.eat_expect(lexer.BLOCKEND, "Expect block statement to end for '%s'." % (lexer.CLASS), loc_start)

        return ClassDeclaration(classname, functions, dynamics, mutables, constants).location(loc_start, self.at())

    # a = (...)
    # mut a
    # mut a = (...)
    # dyn a = (...)
    def parse_class_member_variable_declaration(self):
        loc_start = self.at()

        # dyn int a = (...)
        # mut int a = (...)
        # ^^^
        # next up 'mut'|dyn might follow to declare it mutable or dynamic
        is_mutable = False
        if self.at().type is lexer.MUT:
            is_mutable = True
            self.eat() # eat 'mut'
        is_dynamic = False
        if self.at().type is lexer.DYN:
            is_dynamic = True
            self.eat() # eat 'dyn'

        # mut int a = (...)
        #     ^^^
        type_start = self.at()
        if self.at().type is lexer.IDENTIFIER:
            type = Type(self.eat().value, False).location(type_start, self.at())
        elif self.at().type is lexer.BUILTINTYPE:
            type = Type(self.eat().value, True).location(type_start, self.at())
        else:
            parser_error("Expect identifier or builtin type for variable type declaration", loc_start, self.at())

        # mut int indentifier = (...)
        #         ^^^^^^^^^^^
        identifier = self.eat_expect(lexer.IDENTIFIER, "Expect indentifier after type for variable declaration.", loc_start).value

        # mut int a = (...)
        #           ^
        self.eat_expect(lexer.ASSIGN, "Expect '%s' following type and identifier for '%s' declaration." % (lexer.ASSIGN, loc_start.type), loc_start)

        # mut int a = (...)
        #             ^^^^^
        value = self.parse_expression()
        return ClassMemberVariableDeclaration(is_mutable, type, identifier, value).location(loc_start, self.at())

    def parse_enum(self):
        # eat then 'enum' keyword
        # enum foo:
        # ^^^^
        loc_start = self.eat()

        # enum foo:
        #      ^^^
        enumname = self.eat_expect(lexer.IDENTIFIER, "Identifier expected after '%s' keyword." % lexer.CLASS, loc_start).value
        self.eat_expect(lexer.COLON, "Expect '%s' after identifier in '%s'." % (lexer.COLON, lexer.CLASS), loc_start)
        self.eat_expect(lexer.BLOCKSTART, "Expect block statement after '%s' identifier in '%s'." % (lexer.COLON, lexer.CLASS), loc_start)

        # enum body
        fields = []
        while self.not_eof() and self.at().type is lexer.BLOCKEND:
            # i = 0
            # ^^^^^
            fields.append(self.parse_enum_field_declaration())

        self.eat_expect(lexer.BLOCKEND, "Expect block statement to end for '%s'." % (lexer.ENUM), loc_start)

        return EnumDeclaration(enumname, fields).location(loc_start, self.at())

    def parse_enum_field_declaration(self):
        # a = 0
        # ^^^^^
        loc_start = self.eat_expect(lexer.IDENTIFIER, "Identifier expected after '%s' in '%s'." % (lexer.COLON, lexer.ENUM))
        identifier = identifier.value

        # a = 0
        #   ^
        self.eat_expect(lexer.ASSIGN, "Expect '%s' after identifier in '%s'." % (lexer.ASSIGN, lexer.ENUM))

        # a = (...)
        #     ^^^^^
        value = self.parse_expression()

        return EnumFieldDeclaration(identifier, value).location(loc_start, self.at())

    def parse_alloc(self):
        # @alloc allocator_name
        # ^^^^^^
        loc_start = self.eat() # eat keyword

        identifier = self.eat_expect(lexer.IDENTIFIER, "Identifier expected after '%s' keyword." % (lexer.ALLOC), loc_start)

        return AllocatorSwitch(identifier.value).location(loc_start, self.at())

    def skip_until_end_of_code_block(self, loc_start: Token):
        # straight up refuse dead code
        if self.not_eof() and self.at().type is not lexer.BLOCKEND:
            parser_error("Expect block statement to end here. Dead code is not allowed. Possible indentation error.", loc_start, self.at())

        # alternative the statments can be consumed. They are syntax checked this way.
        # while self.not_eof() and self.at().type is not lexer.BLOCKEND:
        #     self.parse_statement() #throw it away

    # (...)
    def parse_expression(self):
        return self.parse_assignment_expression()

    # i = 5
    # i = (...)
    def parse_assignment_expression(self):
        loc_start = self.at()
        # foo = bar
        # ^^^
        assignee = self.parse_object_expression()
        expressions = [lexer.ASSIGN, lexer.ASSIGNADD, lexer.ASSIGNSUB, lexer.ASSIGNMUL, lexer.ASSIGNDIV,
                       lexer.ASSIGNREM, lexer.ASSIGNBITAND, lexer.ASSIGNBITXOR, lexer.ASSIGNBITOR,
                       lexer.ASSIGNBITSHIFTL, lexer.ASSIGNBITSHIFTR]
        if self.at().type in expressions:
            operator = self.eat().type
            value = self.parse_assignment_expression()
            # foo = bar
            #       ^^^
            return AssignmentExpression(assignee, value, operator).location(loc_start, self.at())

        return assignee

    # (...)
    # { (...) }
    # { foo: bar }
    # { foo1: bar1, foo2: bar2 }
    def parse_object_expression(self):
        loc_start = self.at()
        # check if it is an object. if not just continue down the tree
        if self.at().type is not lexer.WIGGLE_L:
            return self.parse_array_expression()

        self.eat() # eat wiggle "{"
        properties = []
        while self.not_eof() and self.at().type is not lexer.WIGGLE_R:
            loc_start_loop = self.at()
            key = self.eat_expect(lexer.IDENTIFIER, "identifier key expected", loc_start_loop).value

            # handle shorthand key: pair -> { key, }
            if self.at().type is lexer.COMMA:
                self.eat() #advance comma
                properties.append(ObjectProperty(key).location(loc_start_loop, self.at()))
                continue
            # handle shorthand key: pair -> { key }
            if self.at().type is lexer.WIGGLE_R:
                properties.append(ObjectProperty(key).location(loc_start_loop, self.at()))
                continue

            # handle {key: val}
            self.eat_expect(lexer.COLON, "Missing '%s' following identifier in ObjectExpr" % lexer.COLON, loc_start_loop)
            value = self.parse_expression()
            properties.append(ObjectProperty(key, value).location(loc_start_loop, self.at()))

            # expect close "}" or if not expect a ","
            if self.at().type is not lexer.WIGGLE_R:
                # expect a ","
                self.eat_expect(lexer.COMMA, "Expected '%s' or '%s' following property" % (lexer.COMMA, lexer.WIGGLE_R), loc_start_loop)

        self.eat_expect(lexer.WIGGLE_R, "Expect closing '%s' after '%s' object" % (lexer.WIGGLE_R, lexer.WIGGLE_L), loc_start)
        return ObjectLiteral(properties).location(loc_start, self.at())

    def parse_array_expression(self):
        loc_start = self.at()
        # check if it is an array. If not just continue down the tree
        if self.at().type is not lexer.SQUARE_L:
            return self.parse_logic_or_expr()

        self.eat() # eat square "["
        list = []
        while self.not_eof() and self.at().type is not lexer.SQUARE_R:
            loop_loc_start = self.at()
            list.append(self.parse_expression())

            # expect close "}" or if not expect a ","
            if self.at().type is not lexer.SQUARE_R:
                # expect a ","
                self.eat_expect(lexer.COMMA, "Expected '%s' or '%s' following expression" % (lexer.COMMA, lexer.SQUARE_R), loop_loc_start)

        self.eat_expect(lexer.SQUARE_R, "Expect closing '%s' after '%s' list" % (lexer.SQUARE_R, lexer.SQUARE_L), loc_start)
        return ListLiteral(list).location(loc_start, self.at())

    # (...) or (...)
    def parse_logic_or_expr(self):
        loc_start = self.at()
        left = self.parse_logic_and_expr()
        while self.at().type is lexer.OR:
            operator = self.eat().type
            right = self.parse_logic_and_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) and (...)
    def parse_logic_and_expr(self):
        loc_start = self.at()
        left = self.parse_bit_logic_or_expr()
        while self.at().type is lexer.AND:
            operator = self.eat().type
            right = self.parse_bit_logic_or_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) | (...)
    def parse_bit_logic_or_expr(self):
        loc_start = self.at()
        left = self.parse_bit_logic_xor_expr()
        while self.at().type is lexer.BITOR:
            operator = self.eat().type
            right = self.parse_bit_logic_xor_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) ^ (...)
    def parse_bit_logic_xor_expr(self):
        loc_start = self.at()
        left = self.parse_bit_logic_and_expr()
        while self.at().type is lexer.XOR:
            operator = self.eat().type
            right = self.parse_bit_logic_and_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) & (...)
    def parse_bit_logic_and_expr(self):
        loc_start = self.at()
        left = self.parse_logic_equality_expr()
        while self.at().type is lexer.BITAND:
            operator = self.eat().type
            right = self.parse_logic_equality_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) == (...)
    # (...) != (...)
    def parse_logic_equality_expr(self):
        loc_start = self.at()
        left = self.parse_logic_compare_expr()
        expressions = [lexer.COMPARE, lexer.NOTCOMPARE]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_logic_compare_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) <= (...)
    # (...) >= (...)
    # (...) > (...)
    # (...) < (...)
    def parse_logic_compare_expr(self):
        loc_start = self.at()
        left = self.parse_bit_shift_expr()
        expressions = [lexer.BIGGEREQ, lexer.SMALLEREQ, lexer.BIGGER, lexer.SMALLER]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_bit_shift_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) << (...)
    # (...) >> (...)
    def parse_bit_shift_expr(self):
        loc_start = self.at()
        left = self.parse_additive_expr()
        expressions = [lexer.SHIFTRIGHT, lexer.SHIFTLEFT]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_additive_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression


    # (...) + (...)
    # (...) - (...)
    def parse_additive_expr(self):
        loc_start = self.at()
        left = self.parse_multiplicative_expr()
        expressions = [lexer.PLUS, lexer.MINUS]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_multiplicative_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left # no more things to do, return last expression

    # (...) * (...)
    # (...) / (...)
    # (...) // (...)
    # (...) % (...)
    def parse_multiplicative_expr(self):
        loc_start = self.at()
        left = self.parse_exponential_expr()
        expressions = [lexer.MUL, lexer.DIV, lexer.MOD, lexer.INTDIV]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_exponential_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left #no more things to do, return last expression

    # (...) ^ (...)
    def parse_exponential_expr(self):
        loc_start = self.at()
        left = self.parse_single_operator_before_expr()
        expressions = [lexer.POW]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_single_operator_before_expr()
            left = BinaryExpression(left, right, operator).location(loc_start, self.at())
        return left #no more things to do, return last expression

    # not i
    # ~i
    # +i
    # -i
    # ++i
    # --i
    def parse_single_operator_before_expr(self):
        loc_start = self.at()
        expressions = [lexer.NOT, lexer.BITNOT, lexer.PLUS, lexer.MINUS]
        if self.at().type in expressions:
            operator = self.eat().type
            expr = self.parse_single_operator_after_expr()
            return UnaryBeforeExpression(expr, operator).location(loc_start, self.at())
        identifier_expressions = [lexer.INCREMENT, lexer.DECREMENT]
        if self.at().type in identifier_expressions:
            operator = self.eat().type
            expr = self.parse_single_operator_after_expr()
            if not isinstance(expr, Identifier):
                parser_error("Operators '%s' and '%s' are only allowed on Identifiers." % (lexer.INCREMENT, lexer.DECREMENT), loc_start, self.at())
            return UnaryIdentifierBeforeExpression(expr.symbol, operator).location(loc_start, self.at())
        return self.parse_single_operator_after_expr()

    # i++
    # i--
    def parse_single_operator_after_expr(self):
        loc_start = self.at()
        expr = self.parse_call_member_expr()
        expressions = [lexer.INCREMENT, lexer.DECREMENT]
        if self.at().type in expressions:
            if not isinstance(expr, Identifier):
                parser_error("Operators '%s' and '%s' are only allowed on Identifiers." % (lexer.INCREMENT, lexer.DECREMENT), loc_start, self.at())
            operator = self.eat().type
            return UnaryIdentifierAfterExpression(expr.symbol, operator).location(loc_start, self.at())
        return expr

    # (...)
    # (...)()
    # (...)()()
    # (...).(...)()
    # foo.bar()
    # foo.bar()()
    # foo().bar()()
    def parse_call_member_expr(self):
        loc_start = self.at()
        # (...)()
        # ^^^^^
        # foo.bar.a.b.c()()()()()
        # ^^^^^^^^^^^^^ = member
        member = self.parse_member_expr()

        # check if there is a call coming up
        # (...)()
        #      ^
        if self.at().type is lexer.COURVE_L:
            # member((...))
            return self.parse_call_expr(member, loc_start)

        return member

    # caller()
    # caller()()
    # caller()()()
    # caller(...)
    def parse_call_expr(self, caller, loc_start):
        args = self.parse_call_arguments()
        call_expr = CallExpression(caller, args).location(loc_start, self.at())

        if self.at().type == lexer.COURVE_L:
            call_expr = self.parse_call_expr(call_expr, loc_start)

        return call_expr

    # ()
    # (...)
    # (1, 2, 3)
    def parse_call_arguments(self):
        loc_start = self.at()
        self.eat_expect(lexer.COURVE_L, "Call is denoted with its list and must begin with '%s' even when empty." % lexer.COURVE_L, loc_start)
        if self.at().type is lexer.COURVE_R:
            #call argument list is empy
            args = []
        else:
            #call argument list is not empty
            args = self.parse_call_argument_list()
        self.eat_expect(lexer.COURVE_R, "Expect '%s' to close argument list." % lexer.COURVE_R, loc_start)
        return args

    # (...)
    # (...), (...)
    # 1, 2, 3
    def parse_call_argument_list(self):
        args = []
        args.append(self.parse_assignment_expression())

        while self.at().type is lexer.COMMA:
            self.eat() #eat the comma
            args.append(self.parse_assignment_expression())

        return args

    # foo
    # foo.bar
    # foo.bar.a.b
    # foo[]
    # foo[].bar
    # foo.bar[][][].a.b
    def parse_member_expr(self):
        #the first expression is expected to be here and is a primary
        obj = self.parse_primary_expr()

        while self.at().type is lexer.DOT or self.at().type is lexer.SQUARE_L:
            loc_start = self.at()
            operator = self.eat() # either '.' or '[

            if operator.type is lexer.DOT:
                # the . expressions are non comptable, so they must be a primary_expr
                child = self.parse_primary_expr()
                computed = False
                if not isinstance(child, Identifier):
                    parser_error("Cannot use '%s' operator without right hand side being a identifier." % lexer.DOT, loc_start, self.at())
            else:
                # operator is '['
                # this value could be any other expression
                child = self.parse_expression()
                self.eat_expect(lexer.SQUARE_R, "Expect closing '%s' after a member call." % lexer.SQUARE_R, loc_start)
                computed = True

            obj = MemberExpression(obj, child, computed).location(loc_start, self.at())

        return obj

    # foo
    # 1.0
    # 123
    # (...)
    def parse_primary_expr(self):
        loc_start = self.at()
        type = self.at().type
        if type is lexer.IDENTIFIER:
            return Identifier(self.eat().value).location(loc_start, self.at())
        if type is lexer.NUMBER:
            return NumericLiteral(self.eat().value).location(loc_start, self.at())
        if type is lexer.FLOAT:
            return FloatLiteral(self.eat().value).location(loc_start, self.at())
        if type is lexer.STRING:
            return StringLiteral(self.eat().value).location(loc_start, self.at())
        if type is lexer.COURVE_L:
            self.eat() # eat "("
            value = self.parse_expression() # evaluate (...)
            self.eat_expect(lexer.COURVE_R, "Expected '%s' after '%s'." % (lexer.COURVE_R, lexer.COURVE_L), loc_start) # eat ")"
            return value
        #invalid token reached
        parser_error("Unexpected or unimplemented token reached. Token is %s." % str(self.at()), loc_start, self.at())


