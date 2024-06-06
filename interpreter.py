import abstract_source_tree as ast
import lexer

class RuntimeValue:
    variant: str
    def __init__(self):
        self.variant = type(self).__name__.upper()
    def __repr__(self):
        return str(self.json())
    def json(self):
        return vars(self)

class NoneValue(RuntimeValue):
    pass

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
            return self.parent.resolve()
        return None


def interpret(stmt: ast.Statement, env: Environment) -> RuntimeValue:
    if isinstance(stmt, ast.VarDeclaration):
        return interpret_var_declaration(stmt, env)
    if isinstance(stmt, ast.BinaryExpression):
        return interpret_binary_expression(stmt, env)
    if isinstance(stmt, ast.UnaryBeforeExpression):
        return interpret_unary_before_expression(stmt, env)
    if isinstance(stmt, ast.UnaryAfterExpression):
        return interpret_unary_after_expression(stmt, env)
    if isinstance(stmt, ast.AssignmentExpression):
        return interpret_assignment_expression(stmt, env)
    
    if isinstance(stmt, ast.NumericLiteral):
        return NumberValue(stmt.value)
    if isinstance(stmt, ast.FloatLiteral):
        return NumberValue(stmt.value)
    if isinstance(stmt, ast.Identifier):
        return env.lookup(stmt.symbol)

    if isinstance(stmt, ast.Program):
        return interpret_program(stmt, env)
    if isinstance(stmt, ast.FunctionDeclaration):
        return interpret_functiondeclare(stmt, env)
    if isinstance(stmt, ast.CallExpression):
        return interpret_call_expression(stmt, env)
    raise Exception("unable to interpret '%s'" % stmt.kind)

def interpret_var_declaration(stmt: ast.VarDeclaration, env: Environment) -> RuntimeValue:
    if stmt.type.type is lexer.INT:
        value = 0
        if stmt.value:
            value = interpret(stmt.value, env)
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
        return NumberValue(left.value // right.value)
    if stmt.operator is lexer.POW:
        return NumberValue(left.value ** right.value)
    raise Exception("statement operator invalid '%s'" % stmt.operator)


def interpret_unary_before_expression(stmt: ast.UnaryBeforeExpression, env: Environment) -> RuntimeValue:
    expression = interpret(stmt.left, env)
    if stmt.operator is lexer.NOT:
        return BooleanValue(not expression)
    if stmt.operator is lexer.BITNOT:
        return NumberValue(~expression.value)
    if stmt.operator is lexer.PLUS:
        return expression #does nothing
    if stmt.operator is lexer.MINUS:
        return NumberValue(-expression.value)
    if stmt.operator is lexer.INCREMENT:
        return NumberValue(expression.value + 1)
    if stmt.operator is lexer.DECREMENT:
        return NumberValue(expression.value - 1)
    raise Exception("statement operator invalid '%s'" % stmt.operator)


def interpret_unary_after_expression(stmt: ast.UnaryAfterExpression, env: Environment) -> RuntimeValue:
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
    for statement in stmt.body:
        last = interpret(statement, env)
        if last == None:
            raise Exception("must return a runtime value")
    return last

def interpret_functiondeclare(stmt: ast.FunctionDeclaration, env: Environment) -> RuntimeValue:
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


    # # create new function scope
    # # optionally this scope could be passed from function runtime variable, but that is a script
    # # thing to do and not how C works. To keep compatibility with C, need to do it the boring way.
    # scope = Environment(env)
    # # put the passed arguments into the scope environment
    # for argument, parameter in zip(stmt.arguments, runtime_function.function.parameters):
    #     argument_value = interpret(argument, env)










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