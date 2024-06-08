import flolang.abstract_source_tree as ast
import flolang.lexer as lexer
import itertools
from flolang.error import runtime_error
import typing #Callable, Self

class RuntimeValue:
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
    def __init__(self, callback: typing.Callable):
        super().__init__()
        self.callback = callback

class RuntimeFunction(RuntimeValue):
    def __init__(self, function: ast.FunctionDeclaration):
        super().__init__()
        self.function = function


def statement_error(message, stmt: ast.Statement):
    runtime_error(message, stmt.loc)

# small name because its used as enumeration
class envstate:
    RUN = "env_run"
    BREAK = "env_break"
    RETURN = "env_return"
    CONTINUE = "env_continue"

class Environment:
    def __init__(self, parent : typing.Self = None):
        self.scope = {}
        self.mutables = []
        self.parent = parent
        self.state = envstate.RUN

    def declare(self, name: str, value: RuntimeValue, is_mutable: bool, stmt: ast.Statement) -> RuntimeValue:
        if self.scope.get(name):
            statement_error("Variable '%s' is already defined." % name, stmt)
        self.scope[name] = value
        if is_mutable:
            self.mutables.append(name)
        return value

    def assign(self, name: str, value: RuntimeValue, stmt: ast.Statement) -> RuntimeValue:
        env = self._resolve(name)
        if env:
            if not name in env.mutables:
                statement_error("Variable '%s' is not mutable. Use '%s' keyword on declaration to make it mutable." % (name, lexer.MUT), stmt)
            env.scope[name] = value
            return value
        statement_error("Variable '%s' is not defined." % name, stmt)

    def lookup(self, name: str, stmt: ast.Statement):
        env = self._resolve(name)
        if env:
            return env.scope[name]
        statement_error("Variable '%s' is not defined." % name, stmt)

    def _resolve(self, name: str):
        if name in self.scope:
            return self
        if self.parent:
            return self.parent._resolve(name)
        return None


def interpret(stmt: ast.Statement, env: Environment) -> RuntimeValue:
    if isinstance(stmt, ast.GlobalVariableDeclaration):
        return interpret_global_variable_declaration(stmt, env)
    if isinstance(stmt, ast.LocalVariableDeclaration):
        return interpret_local_variable_declaration(stmt, env)
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
        return env.lookup(stmt.symbol, stmt)

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
    if isinstance(stmt, ast.BlockStatement):
        return interpret_block_expression(stmt, env)
    if isinstance(stmt, ast.ReturnExpression):
        return interpret_return_expression(stmt, env)
    if isinstance(stmt, ast.BreakExpression):
        return interpret_break_expression(stmt, env)
    if isinstance(stmt, ast.ContinueExpression):
        return interpret_continue_expression(stmt, env)
    if isinstance(stmt, ast.UnreachableExpression):
        statement_error("Reached unreachable expression.", stmt)

    statement_error("Unable to interpret AST node '%s'." % stmt.kind, stmt)

def interpret_local_variable_declaration(stmt: ast.LocalVariableDeclaration, env: Environment) -> RuntimeValue:
    if stmt.type.type is lexer.INT:
        if stmt.value:
            value = interpret(stmt.value, env)
        else:
            value = NumberValue(0)
        return env.declare(stmt.identifier, value, stmt.mutable, stmt)
    statement_error("Variable type to declare not implemented '%s'." % stmt.type, stmt)

def interpret_global_variable_declaration(stmt: ast.GlobalVariableDeclaration, env: Environment) -> RuntimeValue:
    if stmt.type.type is lexer.INT:
        if stmt.value:
            value = interpret(stmt.value, env)
        else:
            value = NumberValue(0)
        return env.declare(stmt.identifier, value, stmt.mutable, stmt)
    statement_error("Variable type to declare not implemented '%s'." % stmt.type, stmt)

def interpret_binary_expression(stmt: ast.BinaryExpression, env: Environment) -> RuntimeValue:
    left = interpret(stmt.left, env)
    right = interpret(stmt.right, env)
    try:
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
    except TypeError as te:
        statement_error("Interpreter type error '%s'. Unable to resolve operation with given types." % str(te), stmt)
    statement_error("Statement operator invalid '%s'." % stmt.operator, stmt)


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
    statement_error("Statement operator invalid '%s'." % stmt.operator, stmt)


def interpret_unary_identifier_before_expression(stmt: ast.UnaryIdentifierBeforeExpression, env: Environment) -> RuntimeValue:
    variable = env.lookup(stmt.identifier, stmt)
    if stmt.operator is lexer.INCREMENT:
        variable = NumberValue(variable.value + 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable
    if stmt.operator is lexer.DECREMENT:
        variable = NumberValue(variable.value - 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable

def interpret_unary_identifier_after_expression(stmt: ast.UnaryIdentifierAfterExpression, env: Environment) -> RuntimeValue:
    variable_original = env.lookup(stmt.identifier, stmt)
    if stmt.operator is lexer.INCREMENT:
        variable = NumberValue(variable_original.value + 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable_original
    if stmt.operator is lexer.DECREMENT:
        variable = NumberValue(variable_original.value - 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable_original
    statement_error("Interpret_unary_after_expression unimplemented.", stmt)

def interpret_assignment_expression(stmt: ast.AssignmentExpression, env: Environment) -> RuntimeValue:
    if not isinstance(stmt.assignee, ast.Identifier):
        statement_error("Can only assign to indentifier. Got '%s' instead. Maybe you meant '%s' instead of '%s'?" % (stmt.assignee.kind, lexer.COMPARE, lexer.ASSIGN), stmt.assignee)
    identifier = stmt.assignee.symbol
    right = interpret(stmt.value, env)
    if stmt.operator is lexer.ASSIGN:
        return env.assign(identifier, right, stmt)
    left = env.lookup(identifier, stmt)
    if stmt.operator is lexer.ASSIGNADD:
        return env.assign(identifier, NumberValue(left.value + right.value), stmt)
    if stmt.operator is lexer.ASSIGNSUB:
        return env.assign(identifier, NumberValue(left.value - right.value), stmt)
    if stmt.operator is lexer.ASSIGNMUL:
        return env.assign(identifier, NumberValue(left.value * right.value), stmt)
    if stmt.operator is lexer.ASSIGNDIV:
        return env.assign(identifier, NumberValue(left.value / right.value), stmt)
    if stmt.operator is lexer.ASSIGNREM:
        return env.assign(identifier, NumberValue(left.value % right.value), stmt)
    if stmt.operator is lexer.ASSIGNBITAND:
        return env.assign(identifier, NumberValue(left.value & right.value), stmt)
    if stmt.operator is lexer.ASSIGNBITXOR:
        return env.assign(identifier, NumberValue(left.value ^ right.value), stmt)
    if stmt.operator is lexer.ASSIGNBITOR:
        return env.assign(identifier, NumberValue(left.value | right.value), stmt)
    if stmt.operator is lexer.ASSIGNBITSHIFTR:
        return env.assign(identifier, NumberValue(left.value >> right.value), stmt)
    if stmt.operator is lexer.ASSIGNBITSHIFTL:
        return env.assign(identifier, NumberValue(left.value << right.value), stmt)
    statement_error("Statement operator invalid '%s'." % stmt.operator, stmt)



def interpret_program(stmt: ast.Program, env: Environment) -> RuntimeValue:
    last = NoneValue()
    # defer all direct function calls in first pass
    defer = []
    for statement in stmt.body:
        if isinstance(statement, ast.CallExpression):
            defer.append(statement)
        else:
            last = interpret(statement, env)
            if env.state is envstate.BREAK:
                statement_error("Expression '%s' is not allowed outside loop." % lexer.BREAK, stmt)
            if env.state is envstate.CONTINUE:
                statement_error("Expression '%s' is not allowed outside loop." % lexer.CONTINUE, stmt)
            if env.state is envstate.RETURN:
                statement_error("Expression '%s' is not allowed outside function." % lexer.RETURN, stmt)
            if last == None:
                statement_error("Must return a runtime value.", stmt) # this is a development check mainly

    # then interpret everything else
    for statement in defer:
        last = interpret(statement, env)
        if env.state is envstate.BREAK:
            statement_error("Expression '%s' is not allowed outside loop." % lexer.BREAK, stmt)
        if env.state is envstate.CONTINUE:
            statement_error("Expression '%s' is not allowed outside loop." % lexer.CONTINUE, stmt)
        if env.state is envstate.RETURN:
            statement_error("Expression '%s' is not allowed outside function." % lexer.RETURN, stmt)
        if last == None:
            statement_error("Must return a runtime value.", stmt) # this is a development check mainly
    return last

def interpret_function_declare(stmt: ast.FunctionDeclaration, env: Environment) -> RuntimeValue:
    return env.declare(stmt.identifier, RuntimeFunction(stmt), True, stmt) # function declarations are always constant

def interpret_call_expression(stmt: ast.CallExpression, env: Environment) -> RuntimeValue:
    # need the function identifier name. interpret the caller expression
    function = interpret(stmt.caller, env)

    if isinstance(function, NativeFunction):
        argument_list = [interpret(s, env) for s in stmt.arguments]
        result = function.callback(argument_list)
        if result == None: # native function might not return anything, fix this here.
            result = NoneValue()
        if not isinstance(result, RuntimeValue):
            statement_error("Result of native function call is not of a runtime type.", stmt)
        return result

    if isinstance(function, RuntimeFunction):
        # create new function scope
        # optionally this scope could be passed from function runtime variable, but that is a script
        # thing to do and not how C works. To keep compatibility with C, need to do it the boring way.
        scope = Environment(env)
        for param, argument in itertools.zip_longest(function.function.parameters, stmt.arguments):
            # make sure the function has enough parameters if not, that is fatal
            if param == None:
                statement_error("function does not have enough parameters.", stmt)

            if param.type.type is lexer.INT:

                # evaluate value of provided argument (if provided)
                # evaluate value per provided function default (if provided)
                if argument != None:
                    value = interpret(argument, env)
                elif param.default != None:
                    value = interpret(param.default, env)
                else:
                    statement_error("Either argument default or a value for argument must be provided", stmt)

                scope.declare(param.identifier.value, value, param.mutable, stmt)
            else:
                statement_error("(Function) variable type to declare not implemented '%s'" % param.type.type, stmt)

        # go through all statements and execute
        last = interpret_block_expression(function.function.body, scope)
        env.state = scope.state # propagate state outwards
        # check for any flow interrupt conditions condition on environment
        if env.state is envstate.BREAK:
            statement_error("Expression '%s' is not allowed outside loop." % lexer.BREAK, stmt)
        if env.state is envstate.CONTINUE:
            statement_error("Expression '%s' is not allowed outside loop." % lexer.CONTINUE, stmt)
        if env.state is envstate.RETURN:
            # must reset the state because we catched the case and it does not propagate outward
            env.state = envstate.RUN
            return last
        return NoneValue() # block has ran to end

    statement_error("Function type not implemented.", stmt)

def interpret_if_expression(stmt: ast.IfExpression, env: Environment) -> RuntimeValue:
    condition = interpret(stmt.test, env)
    # make the conditional check
    if condition.value:
        last = interpret_block_expression(stmt.consequent, env)
        if env.state is envstate.BREAK:
            return NoneValue() #not allowed here, but might be a loop somewhere on the callstack
        if env.state is envstate.CONTINUE:
            return NoneValue() #not allowed here, but might be a loop somewhere on the callstack
        if env.state is envstate.RETURN:
            return last
    else:
        if stmt.alternate:
            last = interpret(stmt.alternate, env)
            if env.state is envstate.BREAK:
                return NoneValue() #not allowed here, but might be a loop somewhere on the callstack
            if env.state is envstate.CONTINUE:
                return NoneValue() #not allowed here, but might be a loop somewhere on the callstack
            if env.state is envstate.RETURN:
                return last
    return NoneValue()

def interpret_while_expression(stmt: ast.WhileExpression, env: Environment) -> RuntimeValue:
    # make the conditional check and loop.
    # must do this every time
    while interpret(stmt.condition, env).value:
        last = interpret_block_expression(stmt.body, env)
        if env.state is envstate.BREAK:
            # must reset the state because we catched the case and it does not propagate outward
            env.state = envstate.RUN
            break
        if env.state is envstate.CONTINUE:
            # must reset the state because we catched the case and it does not propagate outward
            env.state = envstate.RUN
            continue
        if env.state is envstate.RETURN:
            return last
    return NoneValue()

def interpret_for_expression(stmt: ast.ForExpression, env: Environment) -> RuntimeValue:
    min = interpret(stmt.quantity_min, env).value
    max = interpret(stmt.quantity_max, env).value

    # for loop has the limited scope iteration variable. Make a new Environment for it.
    scope = Environment(env)
    loopvarname = stmt.identifier.value
    scope.declare(loopvarname, NumberValue(0), True, stmt)

    # do the loop
    for i in range(min, max):
        scope.assign(loopvarname, NumberValue(i), stmt)
        last = interpret_block_expression(stmt.body, scope)
        env.state = scope.state # propagate state outwards
        # check for any flow interrupt conditions condition on environment
        if env.state is envstate.BREAK:
            # must reset the state because we catched the case and it does not propagate outward
            env.state = envstate.RUN
            break
        if env.state is envstate.CONTINUE:
            # must reset the state because we catched the case and it does not propagate outward
            env.state = envstate.RUN
            continue
        if env.state is envstate.RETURN:
            return last
    return NoneValue()

def interpret_block_expression(stmt: ast.BlockStatement, env: Environment) -> RuntimeValue:
    # create a new local environment. C has this, so we need too.
    scope = Environment(env)
    # go through all statements and execute
    last = NoneValue()
    for statement in stmt.body:
        last = interpret(statement, scope)
        env.state = scope.state # propagate state outwards
        # check for any flow interrupt conditions condition on environment
        if env.state is envstate.BREAK:
            return NoneValue()
        if env.state is envstate.CONTINUE:
            return NoneValue()
        if env.state is envstate.RETURN:
            return last
    return NoneValue()

def interpret_return_expression(stmt: ast.ReturnExpression, env: Environment) -> RuntimeValue:
    if stmt.value:
        # interpret it
        last = interpret(stmt.value, env)
        # set state to return AFTER interpretation, because interpretation might overwrite state.
        env.state = envstate.RETURN
        return last
    # set state to return
    env.state = envstate.RETURN
    return NoneValue()

def interpret_break_expression(stmt: ast.ReturnExpression, env: Environment) -> RuntimeValue:
    env.state = envstate.BREAK
    return NoneValue()

def interpret_continue_expression(stmt: ast.ContinueExpression, env: Environment) -> RuntimeValue:
    env.state = envstate.CONTINUE
    return NoneValue()

