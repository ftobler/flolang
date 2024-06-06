
import flolang.lexer as lexer
from .lexer import Token
from .error import error
from .error import warning


class Statement:
    kind: str
    def __init__(self):
        self.kind = type(self).__name__.upper()
        self.kind = type(self).__name__
    def __repr__(self):
        return str(self.json())
    def json(self):
        return vars(self)

class Expression(Statement):
    pass

class Program(Statement):
    body: list[Statement]
    def __init__(self):
        super().__init__()
        self.body = []

class Type(Statement):
    type: str
    is_builtin: bool
    def __init__(self, type: str, is_builtin: bool):
        super().__init__()
        self.type = type
        self.builtin = is_builtin

class VarDeclaration(Statement):
    constant: bool
    type: Type
    is_builtin: bool
    identifier: str
    value: Expression
    def __init__(self, constant: bool, type: Type, identifier: str, value: Expression = None):
        super().__init__()
        self.constant = constant
        self.type = type
        self.identifier = identifier
        self.value = value

class Parameter(Statement):
    type: Type
    identifier: str
    default: Expression
    def __init__(self, type: Type, identifier: str, default: Expression = None):
        super().__init__()
        self.type = type
        self.identifier = identifier
        self.default = default

class FunctionDeclaration(Statement):
    parameters: list[Parameter]
    result: Type
    identifier: str
    body: list[Statement]
    def __init__(self, parameters: list[Parameter], result: Type, identifier: str, body: list[Statement]):
        super().__init__()
        self.parameters = parameters
        self.result = result
        self.identifier = identifier
        self.body = body

class ReturnExpression(Statement):
    value: Expression
    def __init__(self, value: Expression = None):
        super().__init__()
        self.value = value

class AssignmentExpression(Expression):
    assignee: Expression
    value: Expression
    operator: str
    def __init__(self, assignee: Expression, value: Expression, operator: str):
        super().__init__()
        self.assignee = assignee
        self.value = value
        self.operator = operator

class BinaryExpression(Expression):
    left: Expression
    right: Expression
    operator: str
    def __init__(self, left: Expression, right: Expression, operator: str):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = operator

class UnaryBeforeExpression(Expression):
    expr: Expression
    operator: str
    def __init__(self, expr: Expression, operator: str):
        super().__init__()
        self.expr = expr
        self.operator = operator

class UnaryIdentifierBeforeExpression(Expression):
    identifier: str
    operator: str
    def __init__(self, identifier: str, operator: str):
        super().__init__()
        self.identifier = identifier
        self.operator = operator

class UnaryIdentifierAfterExpression(Expression):
    identifier: str
    operator: str
    def __init__(self, identifier: str, operator: str):
        super().__init__()
        self.identifier = identifier
        self.operator = operator

class CallExpression(Expression):
    caller: Expression
    arguments: list[Expression]
    def __init__(self, caller: Expression, arguments: list[Expression]):
        super().__init__()
        self.caller = caller
        self.arguments = arguments

class MemberExpression(Expression):
    object: Expression
    property: Expression
    computed: bool #TODO unused?
    def __init__(self, object: Expression, property: Expression, computed: bool):
        super().__init__()
        self.object = object
        self.property = property
        self.computed = computed

class Identifier(Expression):
    symbol: str
    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

class NumericLiteral(Expression):
    value: int
    value_raw: str
    def __init__(self, value_raw: str):
        super().__init__()
        self.value_raw = value_raw
        if value_raw.startswith("0x"):
            self.value = int(value_raw, base=16)
        else:
            self.value = int(value_raw)

class FloatLiteral(Expression):
    value: float
    value_raw: str
    def __init__(self, value_raw: str):
        super().__init__()
        self.value_raw = value_raw
        self.value = float(value_raw)

class StringLiteral(Expression):
    value: str
    def __init__(self, value: str):
        super().__init__()
        self.value = value

class ObjectProperty(Expression):
    key: str
    value: Expression
    def __init__(self, key: str, value: Expression=None):
        super().__init__()
        self.key = key
        self.value = value

class ObjectLiteral(Expression):
    properties: list[ObjectProperty]
    def __init__(self, properties: list[ObjectProperty]):
        super().__init__()
        self.properties = properties

class ListLiteral(Expression):
    elements: list[Expression]
    def __init__(self, arguments: list[Expression]):
        super().__init__()
        self.arguments = arguments




class Parser:
    tokens: list[Token] # tokens from lexer

    def not_eof(self) -> bool:
        return self.tokens[0].type is not lexer.EOF

    def at(self) -> Token:
        return self.tokens[0]

    def eat(self) -> Token:
        return self.tokens.pop(0)

    def eat_expect(self, token_type: str, error_comment: any) -> Token:
        prev = self.eat()
        if prev.type is not token_type:
            # message = "Parser Error:\n" + error_comment + "\nExpecting: " + token_type
            message = "%s\nExpecting: %s" % (error_comment, token_type)
            error(message, prev.symbols)
        return prev

    def unimplemented(self):
        if self.not_eof():
            warning("warning  unimplemented token", self.eat().symbols)
            return self.parse_expression()
        error("Unimplemented token encountered and End of File reached.", self.at().symbols)

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
        if type is lexer.VAR or type is lexer.CONST:
            return self.parse_var_declaration()
        if type is lexer.FUNCTION:
            return self.parse_function_declaration()
        if type is lexer.RETURN:
            return self.parse_return_declaration()
        return self.parse_expression()

    # var a
    # var a = (...)
    # const a
    # const a = (...)
    def parse_var_declaration(self):
        is_const = self.eat().type is lexer.CONST

        if self.at().type is lexer.IDENTIFIER:
            type = Type(self.eat().value, False)
        elif self.at().type is lexer.BUILTINTYPE:
            type = Type(self.eat().value, True)
        else:
            error("Expect identifier or builtin type for variable declaration", self.at().symbols)

        identifier = self.eat_expect(lexer.IDENTIFIER, "Expect type and indentifier after '%s' | '%s' keywords" % (lexer.VAR, lexer.CONST)).value

        if is_const:
            # handle const a = (...)
            self.eat_expect(lexer.ASSIGN, "Expect '%s' following type and identifier for '%s' declaration" % (lexer.ASSIGN, lexer.CONST))
            value = self.parse_expression()
            return VarDeclaration(True, type, identifier, value)
        else:
            # handle var a
            #        var a = (...)
            if self.at().type is lexer.ASSIGN:
                self.eat() # consume the assignment operator
                value = self.parse_expression() # eval (...)
                return VarDeclaration(is_const, type, identifier, value)
            else:
                # handle var a
                return VarDeclaration(is_const, type, identifier, None)

    # fn foo():
    # fn foo(a, b, c) d:
    def parse_function_declaration(self):
        self.eat() # eat 'fn' keyword
        identifier = self.eat_expect(lexer.IDENTIFIER, "Expect identifier after '%s' keyword" % lexer.FUNCTION).value

        args = self.parse_function_arguments()
        result = self.parse_next_type()

        self.eat_expect(lexer.COLON, "Expect '%s' following function declaration." % lexer.COLON)
        self.eat_expect(lexer.BLOCKSTART, "Expect indented function body after function declaration")

        body = []
        while self.not_eof() and self.at().type is not lexer.BLOCKEND:
            body.append(self.parse_statement())

        #lexer should create the blockend(s) already, so this message will probably never be seen
        self.eat_expect(lexer.BLOCKEND, "Expect indented function body to end before End of File")

        return FunctionDeclaration(args, result, identifier, body)

    # (int a)
    # (int a, int b)
    # (int a, int b = 5)
    def parse_function_arguments(self) -> list[Parameter]:
        args: list[Type] = []
        self.eat_expect(lexer.COURVE_L, "Expect function argument list beginning with '%s'." % lexer.COURVE_L)

        while self.not_eof() and self.at().type is not lexer.COURVE_R:
            type = self.parse_next_type()
            if not type:
                error("Unable to determine argument type", self.at().symbols)
            identifier = self.eat_expect(lexer.IDENTIFIER, "Expect identifier in argument list")

            default = None #assume no default available
            if self.at().type is lexer.ASSIGN:
                #have a '=' sign here 'int b = 5'
                self.eat()
                default = self.parse_expression()

            # expect close ")" or if not expect a ","
            if self.at().type is not lexer.COURVE_R:
                # expect a ","
                self.eat_expect(lexer.COMMA, "Expected '%s' or '%s' following argument" % (lexer.COMMA, lexer.COURVE_R))

            args.append(Parameter(type, identifier, default))

        self.eat_expect(lexer.COURVE_R, "Expect function argument list ending with '%s'." % lexer.COURVE_R)
        return args

    def parse_next_type(self) -> Type:
        if self.at().type is lexer.IDENTIFIER:
            return Type(self.eat().value, False)
        elif self.at().type is lexer.BUILTINTYPE:
            return Type(self.eat().value, True)
        return None

    def parse_return_declaration(self):
        # eat the 'return' keyword
        value = self.eat().value
        # the current token might be on the next line or not. There is no way
        # the token system has this information because a new line is not a thing
        # that exists for that. Instead the value of the return keyword has been
        # annotated and is 1 for end of line and default None if there are more
        # tokens on the same line.
        if value == None:
            right = self.parse_expression()
            return ReturnExpression(right)
        return ReturnExpression()


    # (...)
    def parse_expression(self):
        return self.parse_assignment_expression()

    # i = 5
    # i = (...)
    def parse_assignment_expression(self):
        # foo = bar
        # ^^^
        assignee = self.parse_object_expression()
        expressions = [lexer.ASSIGN, lexer.ASSIGNADD, lexer.ASSIGNSUB, lexer.ASSIGNMUL, lexer.ASSIGNDIV,
                       lexer.ASSIGNREM, lexer.ASSIGNBITAND, lexer.ASSIGNBITXOR, lexer.ASSIGNBITOR]
        if self.at().type in expressions:
            operator = self.eat().type
            value = self.parse_assignment_expression()
            # foo = bar
            #       ^^^
            return AssignmentExpression(assignee, value, operator)

        return assignee

    # (...)
    # { (...) }
    # { foo: bar }
    # { foo1: bar1, foo2: bar2 }
    def parse_object_expression(self):
        # check if it is an object. if not just continue down the tree
        if self.at().type is not lexer.WIGGLE_L:
            return self.parse_logic_or_expr()

        self.eat() # eat wiggle "{"
        properties = []
        while self.not_eof() and self.at().type is not lexer.WIGGLE_R:
            key = self.eat_expect(lexer.IDENTIFIER, "identifier key expected").value

            # handle shorthand key: pair -> { key, }
            if self.at().type is lexer.COMMA:
                self.eat() #advance comma
                properties.append(ObjectProperty(key))
                continue
            # handle shorthand key: pair -> { key }
            if self.at().type is lexer.WIGGLE_R:
                properties.append(ObjectProperty(key))
                continue

            # handle {key: val}
            self.eat_expect(lexer.COLON, "Missing '%s' following identifier in ObjectExpr" % lexer.COLON)
            value = self.parse_expression()
            properties.append(ObjectProperty(key, value))

            # expect close "}" or if not expect a ","
            if self.at().type is not lexer.WIGGLE_R:
                # expect a ","
                self.eat_expect(lexer.COMMA, "Expected '%s' or '%s' following property" % (lexer.COMMA, lexer.WIGGLE_R))


        self.eat_expect(lexer.WIGGLE_R, "Expect closing '%s' after '%s' object" % (lexer.WIGGLE_R, lexer.WIGGLE_L))
        return ObjectLiteral(properties)

    # (...) or (...)
    def parse_logic_or_expr(self):
        left = self.parse_logic_and_expr()
        while self.at().type is lexer.OR:
            operator = self.eat().type
            right = self.parse_logic_and_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) and (...)
    def parse_logic_and_expr(self):
        left = self.parse_bit_logic_or_expr()
        while self.at().type is lexer.AND:
            operator = self.eat().type
            right = self.parse_bit_logic_or_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) | (...)
    def parse_bit_logic_or_expr(self):
        left = self.parse_bit_logic_xor_expr()
        while self.at().type is lexer.BITOR:
            operator = self.eat().type
            right = self.parse_bit_logic_xor_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) ^ (...)
    def parse_bit_logic_xor_expr(self):
        left = self.parse_bit_logic_and_expr()
        while self.at().type is lexer.XOR:
            operator = self.eat().type
            right = self.parse_bit_logic_and_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) & (...)
    def parse_bit_logic_and_expr(self):
        left = self.parse_logic_equality_expr()
        while self.at().type is lexer.BITAND:
            operator = self.eat().type
            right = self.parse_logic_equality_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) == (...)
    # (...) != (...)
    def parse_logic_equality_expr(self):
        left = self.parse_logic_compare_expr()
        expressions = [lexer.COMPARE, lexer.NOTCOMPARE]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_logic_compare_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) <= (...)
    # (...) >= (...)
    # (...) > (...)
    # (...) < (...)
    def parse_logic_compare_expr(self):
        left = self.parse_bit_shift_expr()
        expressions = [lexer.BIGGEREQ, lexer.SMALLEREQ, lexer.BIGGER, lexer.SMALLER]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_bit_shift_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) << (...)
    # (...) >> (...)
    def parse_bit_shift_expr(self):
        left = self.parse_additive_expr()
        expressions = [lexer.SHIFTRIGHT, lexer.SHIFTLEFT]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_additive_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression


    # (...) + (...)
    # (...) - (...)
    def parse_additive_expr(self):
        left = self.parse_multiplicative_expr()
        expressions = [lexer.PLUS, lexer.MINUS]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_multiplicative_expr()
            left = BinaryExpression(left, right, operator)
        return left # no more things to do, return last expression

    # (...) * (...)
    # (...) / (...)
    # (...) // (...)
    # (...) % (...)
    def parse_multiplicative_expr(self):
        left = self.parse_exponential_expr()
        expressions = [lexer.MUL, lexer.DIV, lexer.MOD, lexer.INTDIV]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_exponential_expr()
            left = BinaryExpression(left, right, operator)
        return left #no more things to do, return last expression

    # (...) ^ (...)
    def parse_exponential_expr(self):
        left = self.parse_single_operator_before_expr()
        expressions = [lexer.POW]
        while self.at().type in expressions:
            operator = self.eat().type
            right = self.parse_single_operator_before_expr()
            left = BinaryExpression(left, right, operator)
        return left #no more things to do, return last expression

    # not i
    # ~i
    # +i
    # -i
    # ++i
    # --i
    def parse_single_operator_before_expr(self):
        expressions = [lexer.NOT, lexer.BITNOT, lexer.PLUS, lexer.MINUS]
        if self.at().type in expressions:
            operator = self.eat().type
            expr = self.parse_single_operator_after_expr()
            return UnaryBeforeExpression(expr, operator)
        identifier_expressions = [lexer.INCREMENT, lexer.DECREMENT]
        if self.at().type in identifier_expressions:
            operator = self.eat().type
            expr = self.parse_single_operator_after_expr()
            if not isinstance(expr, Identifier):
                error("Operators '%s' and '%s' are only allowed on Identifiers." % (lexer.INCREMENT, lexer.DECREMENT), self.at().symbols)
            return UnaryIdentifierBeforeExpression(expr.symbol, operator)
        return self.parse_single_operator_after_expr()

    # i++
    # i--
    def parse_single_operator_after_expr(self):
        expr = self.parse_call_member_expr()
        expressions = [lexer.INCREMENT, lexer.DECREMENT]
        if self.at().type in expressions:
            if not isinstance(expr, Identifier):
                error("Operators '%s' and '%s' are only allowed on Identifiers." % (lexer.INCREMENT, lexer.DECREMENT), self.at().symbols)
            operator = self.eat().type
            return UnaryIdentifierAfterExpression(expr.symbol, operator)
        return expr

    # (...)
    # (...)()
    # (...)()()
    # (...).(...)()
    # foo.bar()
    # foo.bar()()
    # foo().bar()()
    def parse_call_member_expr(self):
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
            return self.parse_call_expr(member)

        return member

    # caller()
    # caller()()
    # caller()()()
    # caller(...)
    def parse_call_expr(self, caller):
        args = self.parse_call_arguments()
        call_expr = CallExpression(caller, args)

        if self.at().type == lexer.COURVE_L:
            call_expr = self.parse_call_expr(call_expr)

        return call_expr

    # ()
    # (...)
    # (1, 2, 3)
    def parse_call_arguments(self):
        self.eat_expect(lexer.COURVE_L, "Call is denoted with its list and must begin with '%s' even when empty." % lexer.COURVE_L)
        if self.at().type is lexer.COURVE_R:
            #call argument list is empy
            args = []
        else:
            #call argument list is not empty
            args = self.parse_call_argument_list()
        self.eat_expect(lexer.COURVE_R, "Expect '%s' to close argument list." % lexer.COURVE_R)
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
            operator = self.eat() # either '.' or '[

            if operator.type is lexer.DOT:
                # the . expressions are non comptable, so they must be a primary_expr
                child = self.parse_primary_expr()
                computed = False
                if not isinstance(child, Identifier):
                    error("Cannot use '%s' operator without right hand side being a identifier." % lexer.DOT, self.at().symbols)
            else:
                # operator is '['
                # this value could be any other expression
                child = self.parse_expression()
                self.eat_expect(lexer.SQUARE_R, "Expect closing '%s' after a member call." % lexer.SQUARE_R)
                computed = True

            obj = MemberExpression(obj, child, computed)

        return obj

    # foo
    # 1.0
    # 123
    # (...)
    def parse_primary_expr(self):
        type = self.at().type
        if type is lexer.IDENTIFIER:
            return Identifier(self.eat().value)
        if type is lexer.NUMBER:
            return NumericLiteral(self.eat().value)
        if type is lexer.FLOAT:
            return FloatLiteral(self.eat().value)
        if type is lexer.STRING:
            return StringLiteral(self.eat().value)
        if type is lexer.COURVE_L:
            self.eat() # eat "("
            value = self.parse_expression() # evaluate (...)
            self.eat_expect(lexer.COURVE_R, "Expected '%s' after '%s'." % (lexer.COURVE_R, lexer.COURVE_L)) # eat ")"
            return value
        #invalid token reached
        error("Unexpected or unimplemented token reached. Token is %s." % str(self.at()), self.at().symbols)


if __name__ == "__main__":
    import main
    main.run4()

