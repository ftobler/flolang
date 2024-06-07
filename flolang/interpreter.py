import flolang.abstract_source_tree as ast
import flolang.lexer as lexer
import itertools

class RuntimeValue:
    variant: str
    def __init__(self):
        self.variant = type(self).__name__
    def __repr__(self):
        return str(self.json())
    def json(self):
        return vars(self)

class NoneValue(RuntimeValue):
    def __init__(self):
        super().__init__()
        self.value = None

class BooleanValue(RuntimeValue):
    def __init__(self, value: bool):
        super().__init__()
        self.value = value

class NumberValue(RuntimeValue):
    def __init__(self, value: int):
        super().__init__()
        self.value = value

class StringValue(RuntimeValue):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

class ObjectValue(RuntimeValue):
    def __init__(self, value: object):
        super().__init__()
        self.value = value

class ArrayValue(RuntimeValue):
    def __init__(self, value: list[any]):
        super().__init__()
        self.value = value

class NativeFunction(RuntimeValue):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

class RuntimeFunction(RuntimeValue):
    def __init__(self, function: ast.FunctionDeclaration):
        super().__init__()
        self.function = function


class Environment:
    def __init__(self, parent=None):
        self.scope = {}
        self.constants = []
        self.parent = parent

    def declare(self, name: str, value: RuntimeValue, is_constant: bool) -> RuntimeValue:
        if self.scope.get(name):
            raise Exception("variable '%s' already defined" % name)
        self.scope[name] = value
        if is_constant:
            self.constants.append(name)
        return value

    def assign(self, name: str, value: RuntimeValue) -> RuntimeValue:
        env = self._resolve(name)
        if env:
            if name in env.constants:
                raise Exception("variable '%s' is constant" % name)
            env.scope[name] = value
            return value
        raise Exception("variable '%s' undefined" % name)

    def lookup(self, name: str):
        env = self._resolve(name)
        if env:
            return env.scope[name]
        raise Exception("variable '%s' undefined" % name)

    def _resolve(self, name: str):
        if name in self.scope:
            return self
        if self.parent:
            return self.parent._resolve(name)
        return None


def interpret(stmt: ast.Statement, env: Environment) -> RuntimeValue:
    if isinstance(stmt, ast.VarDeclaration):
        return interpret_var_declaration(stmt, env)
    if isinstance(stmt, ast.BinaryExpression):
        return interpret_binary_expression(stmt, env)
    if isinstance(stmt, ast.UnaryBeforeExpression):
        return interpret_unary_before_expression(stmt, env)
    if isinstance(stmt, ast.UnaryIdentifierBeforeExpression):
        return interpret_unary_identifier_before_expression(stmt, env)
    if isinstance(stmt, ast.UnaryIdentifierAfterExpression):
        return interpret_unary_identifier_after_expression(stmt, env)
    if isinstance(stmt, ast.AssignmentExpression):
        return interpret_assignment_expression(stmt, env)

    if isinstance(stmt, ast.NumericLiteral):
        return NumberValue(stmt.value)
    if isinstance(stmt, ast.FloatLiteral):
        return NumberValue(stmt.value)
    if isinstance(stmt, ast.StringLiteral):
        return StringValue(stmt.value)
    if isinstance(stmt, ast.Identifier):
        return env.lookup(stmt.symbol)

    if isinstance(stmt, ast.Program):
        return interpret_program(stmt, env)
    if isinstance(stmt, ast.FunctionDeclaration):
        return interpret_function_declare(stmt, env)
    if isinstance(stmt, ast.CallExpression):
        return interpret_call_expression(stmt, env)
    if isinstance(stmt, ast.IfExpression):
        return interpret_if_expression(stmt, env)
    if isinstance(stmt, ast.WhileExpression):
        return interpret_while_expression(stmt, env)
    if isinstance(stmt, ast.ForExpression):
        return interpret_for_expression(stmt, env)
    if isinstance(stmt, ast.BlockExpression):
        return interpret_block_expression(stmt, env)
    if isinstance(stmt, ast.ReturnExpression):
        return interpret_return_expression(stmt, env)
    if isinstance(stmt, ast.BreakExpression):
        return interpret_break_expression(stmt, env)
    if isinstance(stmt, ast.UnreachableExpression):
        raise Exception("Reached unreachable expression.")

    raise Exception("unable to interpret '%s'" % stmt.kind)

def interpret_var_declaration(stmt: ast.VarDeclaration, env: Environment) -> RuntimeValue:
    if stmt.type.type is lexer.INT:
        if stmt.value:
            value = interpret(stmt.value, env)
        else:
            value = NumberValue(0)
        return env.declare(stmt.identifier, value, stmt.constant)
    raise Exception("variable type to declare not implemented '%s'" % stmt.type)

def interpret_binary_expression(stmt: ast.BinaryExpression, env: Environment) -> RuntimeValue:
    left = interpret(stmt.left, env)
    right = interpret(stmt.right, env)
    if stmt.operator is lexer.OR:
        return BooleanValue(left.value or right.value)
    if stmt.operator is lexer.AND:
        return BooleanValue(left.value and right.value)
    if stmt.operator is lexer.BITOR:
        return NumberValue(left.value | right.value)
    if stmt.operator is lexer.XOR:
        return NumberValue(left.value ^ right.value)
    if stmt.operator is lexer.BITAND:
        return NumberValue(left.value & right.value)
    if stmt.operator is lexer.COMPARE:
        return BooleanValue(left.value == right.value)
    if stmt.operator is lexer.NOTCOMPARE:
        return BooleanValue(left.value != right.value)
    if stmt.operator is lexer.BIGGEREQ:
        return BooleanValue(left.value >= right.value)
    if stmt.operator is lexer.SMALLEREQ:
        return BooleanValue(left.value <= right.value)
    if stmt.operator is lexer.BIGGER:
        return BooleanValue(left.value > right.value)
    if stmt.operator is lexer.SMALLER:
        return BooleanValue(left.value < right.value)
    if stmt.operator is lexer.SHIFTRIGHT:
        return NumberValue(left.value >> right.value)
    if stmt.operator is lexer.SHIFTLEFT:
        return NumberValue(left.value << right.value)
    if stmt.operator is lexer.PLUS:
        return NumberValue(left.value + right.value)
    if stmt.operator is lexer.MINUS:
        return NumberValue(left.value - right.value)
    if stmt.operator is lexer.MUL:
        return NumberValue(left.value * right.value)
    if stmt.operator is lexer.DIV:
        return NumberValue(left.value / right.value)
    if stmt.operator is lexer.MOD:
        return NumberValue(left.value % right.value)
    if stmt.operator is lexer.INTDIV:
        return NumberValue(int(left.value // right.value))
    if stmt.operator is lexer.POW:
        return NumberValue(left.value ** right.value)
    raise Exception("statement operator invalid '%s'" % stmt.operator)


def interpret_unary_before_expression(stmt: ast.UnaryBeforeExpression, env: Environment) -> RuntimeValue:
    expression = interpret(stmt.expr, env)
    if stmt.operator is lexer.NOT:
        return BooleanValue(not expression.value)
    if stmt.operator is lexer.BITNOT:
        return NumberValue(~expression.value)
    if stmt.operator is lexer.PLUS:
        return expression #does nothing
    if stmt.operator is lexer.MINUS:
        return NumberValue(-expression.value)
    raise Exception("statement operator invalid '%s'" % stmt.operator)


def interpret_unary_identifier_before_expression(stmt: ast.UnaryIdentifierBeforeExpression, env: Environment) -> RuntimeValue:
    variable = env.lookup(stmt.identifier)
    if stmt.operator is lexer.INCREMENT:
        variable = NumberValue(variable.value + 1)
        env.assign(stmt.identifier, variable)
        return variable
    if stmt.operator is lexer.DECREMENT:
        variable = NumberValue(variable.value - 1)
        env.assign(stmt.identifier, variable)
        return variable

def interpret_unary_identifier_after_expression(stmt: ast.UnaryIdentifierAfterExpression, env: Environment) -> RuntimeValue:
    variable_original = env.lookup(stmt.identifier)
    if stmt.operator is lexer.INCREMENT:
        variable = NumberValue(variable_original.value + 1)
        env.assign(stmt.identifier, variable)
        return variable_original
    if stmt.operator is lexer.DECREMENT:
        variable = NumberValue(variable_original.value - 1)
        env.assign(stmt.identifier, variable)
        return variable_original
    raise Exception("interpret_unary_after_expression unimplemented")

def interpret_assignment_expression(stmt: ast.AssignmentExpression, env: Environment) -> RuntimeValue:
    if not isinstance(stmt.assignee, ast.Identifier):
        raise Exception("can only assign to indentifier" + str(stmt.kind))
    identifier = stmt.assignee.symbol
    right = interpret(stmt.value, env)
    if stmt.operator is lexer.ASSIGN:
        return env.assign(identifier, right)
    left = env.lookup(identifier)
    if stmt.operator is lexer.ASSIGNADD:
        return env.assign(identifier, NumberValue(left.value + right.value))
    if stmt.operator is lexer.ASSIGNSUB:
        return env.assign(identifier, NumberValue(left.value - right.value))
    if stmt.operator is lexer.ASSIGNMUL:
        return env.assign(identifier, NumberValue(left.value * right.value))
    if stmt.operator is lexer.ASSIGNDIV:
        return env.assign(identifier, NumberValue(left.value / right.value))
    if stmt.operator is lexer.ASSIGNREM:
        return env.assign(identifier, NumberValue(left.value % right.value))
    if stmt.operator is lexer.ASSIGNBITAND:
        return env.assign(identifier, NumberValue(left.value & right.value))
    if stmt.operator is lexer.ASSIGNBITXOR:
        return env.assign(identifier, NumberValue(left.value ^ right.value))
    if stmt.operator is lexer.ASSIGNBITOR:
        return env.assign(identifier, NumberValue(left.value | right.value))
    raise Exception("statement operator invalid '%s'" % stmt.operator)



def interpret_program(stmt: ast.Program, env: Environment) -> RuntimeValue:
    last = NoneValue()
    # defer all direct function calls in first pass
    defer = []
    for statement in stmt.body:
        if isinstance(statement, ast.CallExpression):
            defer.append(statement)
        else:
            last = interpret(statement, env)
            if last == None:
                raise Exception("must return a runtime value") # this is a development check mainly

    # then interpret everything else
    for statement in defer:
        last = interpret(statement, env)
        if last == None:
            raise Exception("must return a runtime value") # this is a development check mainly
    return last

def interpret_function_declare(stmt: ast.FunctionDeclaration, env: Environment) -> RuntimeValue:
    return env.declare(stmt.identifier, RuntimeFunction(stmt), True) # function declarations are always constant

def interpret_call_expression(stmt: ast.CallExpression, env: Environment) -> RuntimeValue:
    # need the function identifier name. interpret the caller expression
    function = interpret(stmt.caller, env)

    if isinstance(function, NativeFunction):
        argument_list = [interpret(s, env) for s in stmt.arguments]
        result = function.callback(argument_list)
        if result == None: # native function might not return anything, fix this here.
            result = NoneValue()
        if not isinstance(result, RuntimeValue):
            raise Exception("result of native function call is not of a runtime type")
        return result

    if isinstance(function, RuntimeFunction):
        # create new function scope
        # optionally this scope could be passed from function runtime variable, but that is a script
        # thing to do and not how C works. To keep compatibility with C, need to do it the boring way.
        scope = Environment(env)
        for param, argument in itertools.zip_longest(function.function.parameters, stmt.arguments):
            # make sure the function has enough parameters if not, that is fatal
            if param == None:
                raise Exception("function does not have enough parameters.")

            if param.type.type is lexer.INT:

                # evaluate value of provided argument (if provided)
                # evaluate value per provided function default (if provided)
                if argument != None:
                    value = interpret(argument, env)
                elif param.default != None:
                    value = interpret(param.default, env)
                else:
                    raise Exception("Either argument default or a value for argument must be provided")

                scope.declare(param.identifier.value, value, False)
            else:
                raise Exception("(function) variable type to declare not implemented '%s'" % param.type.type)

        # go through all statements and execute
        for statement in function.function.body:
            if isinstance(statement, ast.ReturnExpression):
                return interpret_return_expression(statement, scope)
            if isinstance(statement, ast.BreakExpression):
                raise Exception("Break not allowed in fuction.")
            interpret(statement, scope)
        return NoneValue()

    raise Exception("function type not implemented")

def interpret_if_expression(stmt: ast.IfExpression, env: Environment) -> RuntimeValue:
    condition = interpret(stmt.condition, env)
    # make the conditional check
    if condition.value:
        ret, last = interpret_block_expression(stmt.positive_case, env)
        if ret == 1: #return
            return last
    else:
        if stmt.negative_case:
            interpret(stmt.negative_case, env)
    return NoneValue()

def interpret_while_expression(stmt: ast.WhileExpression, env: Environment) -> RuntimeValue:
    # make the conditional check and loop.
    # must do this every time
    while interpret(stmt.condition, env).value:
        ret, last = interpret_block_expression(stmt.body, env)
        if ret == 2: # break
            break
        elif ret == 1: # return
            return last
    return NoneValue()

def interpret_for_expression(stmt: ast.ForExpression, env: Environment) -> RuntimeValue:

    min = interpret(stmt.quantity_min, env).value
    max = interpret(stmt.quantity_max, env).value

    # for loop has the limited scope iteration variable. Make a new Environment for it.
    scope = Environment(env)
    loopvarname = stmt.identifier.value
    scope.declare(loopvarname, NumberValue(0), False)

    # do the loop
    for i in range(min, max):
        scope.assign(loopvarname, NumberValue(i))
        ret, last = interpret_block_expression(stmt.body, scope)
        if ret == 2: # break
            break
        elif ret == 1: # return
            return last
    return NoneValue()

def interpret_block_expression(stmt: ast.BlockExpression, env: Environment) -> RuntimeValue:
    # create a new local environment. C has this, so we need too.
    scope = Environment(env)
    # go through all statements and execute
    last = NoneValue()
    for statement in stmt.body:
        if isinstance(statement, ast.ReturnExpression):
            last = interpret_return_expression(statement, scope)
            return 1, last
        if isinstance(statement, ast.BreakExpression):
            return 2, None
        last = interpret(statement, scope)
    return 0, None

def interpret_return_expression(stmt: ast.ReturnExpression, env: Environment) -> RuntimeValue:
    if stmt.value:
        return interpret(stmt.value, env)
    return NoneValue()

def interpret_break_expression(stmt: ast.ReturnExpression, env: Environment) -> RuntimeValue:
    return NoneValue()




# if __name__ == "__main__":
#     print(RuntimeValue())
#     print(NoneValue())
#     print(BooleanValue(True))
#     print(NumberValue(10))
#     print(ObjectValue({'a': 10}))
#     print(ArrayValue([]))
#     print(ArrayValue([]))

if __name__ == "__main__":
    import main
    main.run4()