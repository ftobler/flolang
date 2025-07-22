import itertools
from flolang.error import runtime_error
import typing  # Callable, Self
from decimal import Decimal
from typing import Any
import flolang.abstract_source_tree as ast
import flolang.lexer as lexer


class RuntimeValue:
    value: Any = None

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

    def __repr__(self):
        return "None"


# instead of instantiating a class with the
# same content over and over again,
# reuse this instance
noneValueInstance = NoneValue()


class BooleanValue(RuntimeValue):
    def __init__(self, value: bool):
        super().__init__()
        self.value = bool(value)

    def __repr__(self):
        return str(self.value)


class _NumberValue(RuntimeValue):
    def __repr__(self):
        return str(self.value)


class IntValue(_NumberValue):
    def __init__(self, value: int):
        super().__init__()
        v = int(value) & 0xFFFFFFFF
        if v >= 0x80000000:
            self.value = v - 0xFFFFFFFF - 1
        else:
            self.value = v


class FloatValue(_NumberValue):
    def __init__(self, value: int | float):
        super().__init__()
        self.value = float(value)


# ---- #


class StringValue(RuntimeValue):
    def __init__(self, value: str):
        super().__init__()
        self.value = str(value)

    def __repr__(self):
        return '"' + str(self.value) + '"'


class ListValue(RuntimeValue):
    def __init__(self, value: list[Any]):
        super().__init__()
        self.value = list(value)

    def __repr__(self):
        return str(self.value)
        # return '"' + ",".join([str(s) for s in self.value]) + '"'


class ObjectValue(RuntimeValue):
    def __init__(self, value: object):
        super().__init__()
        self.value = value
        if not isinstance(value, dict):
            raise Exception("Reqire value to be a object.")

    def __repr__(self):
        return str(self.value)


# class TupleValue(RuntimeValue):
#     def __init__(self, value: tuple):
#         super().__init__()
#         self.value = value

#     def __repr__(self):
#         return str(self.value)


class NativeFunction(RuntimeValue):
    def __init__(self, callback: typing.Callable):
        super().__init__()
        self.callback = callback
        if not callable(callback):
            raise Exception("Reqire value to be a function.")

    def __repr__(self):
        return "<native_function>"


class RuntimeFunctionParameter:
    def __init__(self, mutable: bool, type: ast.Type, identifier: str, default: RuntimeValue | None = None):
        self.mutable = mutable
        self.type = type
        self.identifier = identifier
        self.default = default


class RuntimeFunction(RuntimeValue):
    def __init__(self, parameters: list[RuntimeFunctionParameter], result: ast.Type, body: ast.BlockStatement):
        super().__init__()
        self.parameters = parameters
        self.result = result
        self.body = body
        self.env: Environment

    def __repr__(self):
        return "<runtime_function>"


def statement_error(message, stmt: ast.Statement):
    mesg = message + " In '%s' statement." % stmt.kind
    runtime_error(mesg, stmt.loc)


# small name because its used as enumeration
class envstate:
    RUN = "env_run"
    BREAK = "env_break"
    RETURN = "env_return"
    CONTINUE = "env_continue"


class Environment:
    def __init__(self, parent_environment_self=None, runtime_function: RuntimeFunction | None = None):
        self.scope: dict[str, RuntimeValue] = {}
        self.mutables: list[str] = []
        self.parent = parent_environment_self  # cannot use typing.Self on older python versions
        self.state = envstate.RUN
        self.runtime_function = runtime_function
        self.is_script = False

    def declare_local(self, name: str, value: RuntimeValue, is_mutable: bool, stmt: ast.Statement) -> RuntimeValue:
        if self.parent:
            self._declare(name, value, is_mutable, stmt)
            return value
        # if we are script, then we allow this.
        if self.get_root_env().is_script:
            return self._declare(name, value, is_mutable, stmt)
        statement_error("Cannot declare local variable '%s'in global environment." % name, stmt)
        return noneValueInstance

    def declare_global(self, name: str, value: RuntimeValue, is_mutable: bool, stmt: ast.Statement):
        # declare variable on current scope. A function does have its own global scope.

        # check if this is a function scope.
        # if not propagate to parent, which should be a function scope at some point.
        # if no parent is found, this is the global scope. Declare it here.
        if self.runtime_function:
            self.runtime_function.env._declare(name, value, is_mutable, stmt)
        elif self.parent:
            self.parent.declare_global(name, value, is_mutable, stmt)
        else:
            self._declare(name, value, is_mutable, stmt)
        return value

    def _declare(self, name: str, value: RuntimeValue, is_mutable: bool, stmt: ast.Statement) -> RuntimeValue:
        if self.scope.get(name):
            statement_error("Variable '%s' is already defined." % name, stmt)
        self.scope[name] = value
        if is_mutable:
            self.mutables.append(name)
        return value

    def assign(self, name: str, value: RuntimeValue, stmt: ast.Statement, force=False) -> RuntimeValue:
        env = self._resolve(name)
        if env:
            if name not in env.mutables:
                statement_error("Variable '%s' is not mutable. Use '%s' keyword on declaration to make it mutable." % (name, lexer.MUT), stmt)
            if not force:
                # check assignment type
                old = env.scope[name]
                if type(old) is not type(value):
                    statement_error("Variable assigned to '%s' must be of same type." % (name), stmt)
            env.scope[name] = value
            return value
        statement_error("Variable '%s' is not defined." % name, stmt)
        return noneValueInstance

    def lookup(self, name: str, stmt: ast.Statement):
        env = self._resolve(name)
        if env:
            return env.scope[name]
        statement_error("Variable '%s' is not defined." % name, stmt)

    def delete(self, name: str, stmt: ast.Statement):
        if not self.get_root_env().is_script:
            statement_error("Delete Expression '%s' is only allowed in script mode. Did you forgot '#!script' shebang?" % (lexer.DELETE), stmt)
        env = self._resolve(name)
        if env:
            del env.scope[name]
            return noneValueInstance
        statement_error("Variable '%s' is not defined." % name, stmt)

    def has(self, name: str):
        return self._resolve(name)

    def get_root_env(self):
        if self.parent:
            return self.parent.get_root_env()
        return self

    def _resolve(self, name: str):
        if name in self.scope:
            return self
        if self.parent:
            return self.parent._resolve(name)
        return None


def interpret(stmt: ast.Statement, env: Environment) -> RuntimeValue:

    if isinstance(stmt, ast.DynamicVariableDeclaration):
        return interpret_dynamic_variable_declaration(stmt, env)
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

    if isinstance(stmt, ast.NumericLiteral):  # always integer
        return IntValue(stmt.value)
    if isinstance(stmt, ast.FloatLiteral):
        return FloatValue(stmt.value)
    if isinstance(stmt, ast.StringLiteral):
        return StringValue(stmt.value)
    if isinstance(stmt, ast.Identifier):
        return env.lookup(stmt.symbol, stmt)

    if isinstance(stmt, ast.GlobalVariableDeclaration):
        return interpret_global_variable_declaration(stmt, env)
    if isinstance(stmt, ast.LocalVariableDeclaration):
        return interpret_local_variable_declaration(stmt, env)

    if isinstance(stmt, ast.Program):
        return interpret_program(stmt, env)
    if isinstance(stmt, ast.FunctionDeclaration):
        return interpret_function_declare(stmt, env)
    if isinstance(stmt, ast.CallExpression):
        return interpret_call_expression(stmt, env)
    if isinstance(stmt, ast.MemberExpression):
        return interpret_member_expression(stmt, env)
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
    if isinstance(stmt, ast.ElvisExpression):
        return interpret_elvis_expression(stmt, env)

    if isinstance(stmt, ast.ListLiteral):
        return interpret_list_literal(stmt, env)
    if isinstance(stmt, ast.ObjectLiteral):
        return interpret_object_literal(stmt, env)
    # if isinstance(stmt, ast.TupleLiteral):
    #     return interpret_tuple_literal(stmt, env)

    if isinstance(stmt, ast.ShebangExpression):
        return interpret_shebang_expression(stmt, env)
    if isinstance(stmt, ast.DeleteExpression):
        return interpret_delete_expression(stmt, env)
    if isinstance(stmt, ast.UnreachableExpression):
        statement_error("Reached unreachable expression.", stmt)

    statement_error("Unable to interpret AST node '%s'." % stmt.kind, stmt)
    return noneValueInstance


def _assign_Type(value: Any, type: ast.Type):
    type_id = type.type
    if type_id == lexer.Pimitives.BOOL:
        return BooleanValue(value)
    elif type_id == lexer.Pimitives.INT:
        return IntValue(value)
    elif type_id == lexer.Pimitives.FLOAT:
        return FloatValue(value)
    elif type_id == lexer.Pimitives.STR:
        return StringValue(value)
    else:
        raise statement_error("Variable type to declare not implemented '%s'." % type_id, type)


def _interpreted_value_assign_type(stmt: ast.Statement, type: ast.Type, env: Environment) -> RuntimeValue:
    # check if type is declared
    if type:
        value = interpret(stmt, env).value
        return _assign_Type(value, type)
    else:
        # no type given. need to infer type.
        return interpret(stmt, env)


def interpret_local_variable_declaration(stmt: ast.LocalVariableDeclaration, env: Environment) -> RuntimeValue:
    value = _interpreted_value_assign_type(stmt.value, stmt.type, env)
    return env.declare_local(stmt.identifier, value, stmt.mutable, stmt)


def interpret_global_variable_declaration(stmt: ast.GlobalVariableDeclaration, env: Environment) -> RuntimeValue:
    value = _interpreted_value_assign_type(stmt.value, stmt.type, env)
    return env.declare_global(stmt.identifier, value, stmt.mutable, stmt)


def interpret_dynamic_variable_declaration(stmt: ast.DynamicVariableDeclaration, env: Environment) -> RuntimeValue:
    value = _interpreted_value_assign_type(stmt.value, stmt.type, env)
    return env.declare_global(stmt.identifier, value, stmt.mutable, stmt)


def _expression_find_type(left: RuntimeValue, right: RuntimeValue, value: Any):
    # Type promotion rules similar to C
    if isinstance(left, FloatValue) or isinstance(right, FloatValue):
        # Floating-point promotion
        return FloatValue(value)
    # Ensure integer promotion
    return IntValue(value)


def _expression_find_type_everything(left: RuntimeValue, right: RuntimeValue, value: Any):
    if isinstance(left, FloatValue) or isinstance(right, FloatValue):
        # Floating-point promotion
        return FloatValue(value)
    if isinstance(left, IntValue) or isinstance(right, IntValue):
        # Floating-point promotion
        return IntValue(value)
    if isinstance(left, StringValue) or isinstance(right, StringValue):
        # Floating-point promotion
        return StringValue(value)
    raise Exception("cannot assign this")


def interpret_binary_expression(stmt: ast.BinaryExpression, env: Environment) -> RuntimeValue:
    left = interpret(stmt.left, env)
    right = interpret(stmt.right, env)

    if stmt.operator is lexer.PLUS and isinstance(left, StringValue) and isinstance(right, StringValue):
        return StringValue(left.value + right.value)

    try:
        if stmt.operator is lexer.OR:
            return BooleanValue(left.value or right.value)
        if stmt.operator is lexer.AND:
            return BooleanValue(left.value and right.value)
        if stmt.operator is lexer.BITOR:
            return IntValue(left.value | right.value)
        if stmt.operator is lexer.XOR:
            return IntValue(left.value ^ right.value)
        if stmt.operator is lexer.BITAND:
            return IntValue(left.value & right.value)
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
            return IntValue(left.value >> right.value)
        if stmt.operator is lexer.SHIFTLEFT:
            return IntValue(left.value << right.value)
        if stmt.operator is lexer.PLUS:
            return _expression_find_type(left, right, left.value + right.value)
        if stmt.operator is lexer.MINUS:
            return _expression_find_type(left, right, left.value - right.value)
        if stmt.operator is lexer.MUL:
            return _expression_find_type(left, right, left.value * right.value)
        if stmt.operator is lexer.DIV:
            return FloatValue(left.value / right.value)
        if stmt.operator is lexer.MOD:
            return IntValue(left.value % right.value)
        if stmt.operator is lexer.INTDIV:
            return IntValue(int(left.value // right.value))
        if stmt.operator is lexer.POW:
            return _expression_find_type(left, right, left.value ** right.value)
    except TypeError as te:
        statement_error('Interpreter type error "%s". Unable to resolve operation with given types.' % str(te), stmt)

    statement_error('Did not found a operation for this expression.', stmt)
    return noneValueInstance


def _expression_unary_find_type(expression: RuntimeValue, value: Any):
    # Type promotion rules similar to C
    if isinstance(expression, FloatValue):
        # Floating-point promotion
        return FloatValue(value)
    # Ensure integer promotion
    return IntValue(value)


def interpret_unary_before_expression(stmt: ast.UnaryBeforeExpression, env: Environment) -> RuntimeValue:
    expression = interpret(stmt.expr, env)
    if stmt.operator is lexer.NOT:
        return BooleanValue(not expression.value)
    if stmt.operator is lexer.BITNOT:
        return IntValue(~expression.value)
    if stmt.operator is lexer.PLUS:
        return expression  # does nothing
    if stmt.operator is lexer.MINUS:
        return _expression_unary_find_type(expression, -expression.value)
    statement_error("Statement operator invalid '%s' for unary." % stmt.operator, stmt)
    return noneValueInstance


def interpret_unary_identifier_before_expression(stmt: ast.UnaryIdentifierBeforeExpression, env: Environment) -> RuntimeValue:
    variable = env.lookup(stmt.identifier, stmt)
    if stmt.operator is lexer.INCREMENT:
        variable = _expression_unary_find_type(variable, variable.value + 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable
    if stmt.operator is lexer.DECREMENT:
        variable = _expression_unary_find_type(variable, variable.value - 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable
    statement_error("Statement operator invalid '%s' for unary." % stmt.operator, stmt)
    return noneValueInstance


def interpret_unary_identifier_after_expression(stmt: ast.UnaryIdentifierAfterExpression, env: Environment) -> RuntimeValue:
    variable_original = env.lookup(stmt.identifier, stmt)
    if stmt.operator is lexer.INCREMENT:
        variable = _expression_unary_find_type(variable_original, variable_original.value + 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable_original
    if stmt.operator is lexer.DECREMENT:
        variable = _expression_unary_find_type(variable_original, variable_original.value - 1)
        env.assign(stmt.identifier, variable, stmt)
        return variable_original
    statement_error("Statement operator invalid '%s' for unary post expression." % stmt.operator, stmt)
    return noneValueInstance


def interpret_assignment_expression(stmt: ast.AssignmentExpression, env: Environment) -> RuntimeValue:
    if isinstance(stmt.assignee, ast.Identifier):
        identifier = stmt.assignee.symbol
        right = interpret(stmt.value, env)
        left = env.lookup(identifier, stmt)
        if stmt.operator is lexer.ASSIGN:
            return env.assign(identifier, _expression_find_type_everything(left, right, right.value), stmt)
        if stmt.operator is lexer.ASSIGNADD and isinstance(left, StringValue) and isinstance(right, StringValue):
            return env.assign(identifier, StringValue(left.value + right.value), stmt)
        if stmt.operator is lexer.ASSIGNADD:
            return env.assign(identifier, _expression_find_type(left, right, left.value + right.value), stmt)
        if stmt.operator is lexer.ASSIGNSUB:
            return env.assign(identifier, _expression_find_type(left, right, left.value - right.value), stmt)
        if stmt.operator is lexer.ASSIGNMUL:
            return env.assign(identifier, _expression_find_type(left, right, left.value * right.value), stmt)
        if stmt.operator is lexer.ASSIGNDIV:
            return env.assign(identifier, _expression_find_type(left, right, left.value / right.value), stmt)
        if stmt.operator is lexer.ASSIGNREM:
            return env.assign(identifier, IntValue(left.value % right.value), stmt)
        if stmt.operator is lexer.ASSIGNBITAND:
            return env.assign(identifier, IntValue(left.value & right.value), stmt)
        if stmt.operator is lexer.ASSIGNBITXOR:
            return env.assign(identifier, IntValue(left.value ^ right.value), stmt)
        if stmt.operator is lexer.ASSIGNBITOR:
            return env.assign(identifier, IntValue(left.value | right.value), stmt)
        if stmt.operator is lexer.ASSIGNBITSHIFTR:
            return env.assign(identifier, IntValue(left.value >> right.value), stmt)
        if stmt.operator is lexer.ASSIGNBITSHIFTL:
            return env.assign(identifier, IntValue(left.value << right.value), stmt)
        statement_error("Statement operator invalid '%s'." % stmt.operator, stmt)
    elif isinstance(stmt.assignee, ast.MemberExpression):
        object = interpret(stmt.assignee.object, env).value
        if isinstance(stmt.assignee.key, ast.Identifier):
            key = stmt.assignee.key.symbol
        else:
            key = interpret(stmt.assignee.key, env).value
        right = interpret(stmt.value, env)
        left = object[key]
        if stmt.operator is lexer.ASSIGN:
            object[key] = right
            return right
        if stmt.operator is lexer.ASSIGNADD:
            object[key] = left.value + right.value
            return right
        if stmt.operator is lexer.ASSIGNSUB:
            object[key] = left.value - right.value
            return right
        if stmt.operator is lexer.ASSIGNMUL:
            object[key] = left.value * right.value
            return right
        if stmt.operator is lexer.ASSIGNDIV:
            object[key] = left.value / right.value
            return right
        if stmt.operator is lexer.ASSIGNREM:
            object[key] = left.value % right.value
            return right
        if stmt.operator is lexer.ASSIGNBITAND:
            object[key] = left.value & right.value
            return right
        if stmt.operator is lexer.ASSIGNBITXOR:
            object[key] = left.value ^ right.value
            return right
        if stmt.operator is lexer.ASSIGNBITOR:
            object[key] = left.value | right.value
            return right
        if stmt.operator is lexer.ASSIGNBITSHIFTR:
            object[key] = left.value >> right.value
            return right
        if stmt.operator is lexer.ASSIGNBITSHIFTL:
            object[key] = left.value << right.value
            return right
        statement_error("Statement operator invalid '%s'." % stmt.operator, stmt)
    return noneValueInstance


def interpret_program(stmt: ast.Program, env: Environment) -> RuntimeValue:
    last: RuntimeValue = noneValueInstance

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
            if last is None:
                statement_error("Must return a runtime value.", stmt)  # this is a development check mainly

    if env.get_root_env().is_script:
        # in script mode interpret all function calls in order
        for statement in defer:
            last = interpret(statement, env)
            if env.state is envstate.BREAK:
                statement_error("Expression '%s' is not allowed outside loop." % lexer.BREAK, stmt)
            if env.state is envstate.CONTINUE:
                statement_error("Expression '%s' is not allowed outside loop." % lexer.CONTINUE, stmt)
            if env.state is envstate.RETURN:
                statement_error("Expression '%s' is not allowed outside function." % lexer.RETURN, stmt)
            if last is None:
                statement_error("Must return a runtime value.", stmt)  # this is a development check mainly
    else:
        # in normal or program mode just call main function only.
        # any calls to functions are forbidden (for now). Maybe later for something like 'constexpr'
        if len(defer):
            statement_error("In normal mode the main function gets automatically called. Did you forgot '#!script' shebang?", stmt)
        if env.has("main"):
            last = interpret(ast.CallExpression(ast.Identifier("main"), []), env)

    return last


def interpret_function_declare(stmt: ast.FunctionDeclaration, env: Environment) -> RuntimeValue:
    # must interpret the evaluation of the runtime parameters at compile time and not just
    # when the function is called. Or else the function parameter becomes a function call.
    runtime_parameters = []
    for param in stmt.parameters:

        # check if there is a default. If not None is the default.
        evaluated_default = None
        if param.default:
            evaluated_default = interpret(param.default, env)

        # build the function declaration and add to list
        runtime_parameters.append(RuntimeFunctionParameter(param.mutable, param.type, param.identifier, evaluated_default))

    # function declarations are always constant and globally declared
    return env.declare_global(stmt.identifier, RuntimeFunction(runtime_parameters, stmt.result, stmt.body), True, stmt)


def interpret_call_expression(stmt: ast.CallExpression, env: Environment) -> RuntimeValue:
    # need the function identifier name. interpret the caller expression
    function = interpret(stmt.caller, env)

    if isinstance(function, NativeFunction):
        argument_list = [interpret(s, env) for s in stmt.arguments]
        result = function.callback(argument_list)
        if result is None:  # native function might not return anything, fix this here.
            result = noneValueInstance
        if not isinstance(result, RuntimeValue):
            statement_error("Result of native function call is not of a runtime type.", stmt)
        return result

    if isinstance(function, RuntimeFunction):
        # create new function scope
        # optionally this scope could be passed from function runtime variable, but that is a script
        # thing to do and not how C works. To keep compatibility with C, need to do it the boring way.
        scope = Environment(env, runtime_function=function)
        for param, argument in itertools.zip_longest(function.parameters, stmt.arguments):
            # make sure the function has enough parameters if not, that is fatal
            if param is None:
                statement_error("function does not have enough parameters.", stmt)
                return noneValueInstance

            # TODO: use the type
            if True:
                # if param.type.type is lexer.INT:

                # evaluate value of provided argument (if provided)
                # evaluate value per provided function default (if provided)
                if argument is not None:
                    value = interpret(argument, env)
                elif param.default is not None:
                    # is pre interpreted at declaration time. so this is already a runtime variable
                    value = param.default
                else:
                    statement_error("Either argument default or a value for argument must be provided", stmt)

                scope.declare_local(param.identifier, value, param.mutable, stmt)

            # TODO: use the type
            # else:
                # statement_error("(Function) variable type to declare not implemented '%s'" % param.type.type, stmt)

        # go through all statements and execute
        last = interpret_block_expression(function.body, scope)
        env.state = scope.state  # propagate state outwards
        # check for any flow interrupt conditions condition on environment
        if env.state is envstate.BREAK:
            statement_error("Expression '%s' is not allowed outside loop." % lexer.BREAK, stmt)
        if env.state is envstate.CONTINUE:
            statement_error("Expression '%s' is not allowed outside loop." % lexer.CONTINUE, stmt)
        if env.state is envstate.RETURN:
            # must reset the state because we catched the case and it does not propagate outward
            env.state = envstate.RUN
            return last
        return noneValueInstance  # block has ran to end

    statement_error("Function type not implemented.", stmt)
    return noneValueInstance


def interpret_member_expression(stmt: ast.MemberExpression, env: Environment) -> RuntimeValue:
    object = interpret(stmt.object, env).value
    if isinstance(stmt.key, ast.Identifier):
        key = stmt.key.symbol
    else:
        key = interpret(stmt.key, env).value
    if isinstance(object, dict):
        if key in object:
            return object[key]
        return noneValueInstance
    if isinstance(object, list) and isinstance(key, int):
        return object[key]
    statement_error("Incompatible Datatype in expression: %s%s%s%s" % (object, lexer.SQUARE_L, key, lexer.SQUARE_R), stmt)
    return noneValueInstance


def interpret_if_expression(stmt: ast.IfExpression, env: Environment) -> RuntimeValue:
    condition = interpret(stmt.test, env)
    # make the conditional check
    if condition.value:
        last = interpret_block_expression(stmt.consequent, env)
        if env.state is envstate.BREAK:
            return noneValueInstance  # not allowed here, but might be a loop somewhere on the callstack
        if env.state is envstate.CONTINUE:
            return noneValueInstance  # not allowed here, but might be a loop somewhere on the callstack
        if env.state is envstate.RETURN:
            return last
    else:
        if stmt.alternate:
            last = interpret(stmt.alternate, env)
            if env.state is envstate.BREAK:
                return noneValueInstance  # not allowed here, but might be a loop somewhere on the callstack
            if env.state is envstate.CONTINUE:
                return noneValueInstance  # not allowed here, but might be a loop somewhere on the callstack
            if env.state is envstate.RETURN:
                return last
    return noneValueInstance


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
    return noneValueInstance


def interpret_for_expression(stmt: ast.ForExpression, env: Environment) -> RuntimeValue:
    is_range_iterator = False
    iterator: Any = 0
    if not stmt.quantity_min:
        max = interpret(stmt.quantity_max, env)
        if isinstance(max, _NumberValue):
            iterator = range(max.value)
            is_range_iterator = True
        elif isinstance(max, ListValue):
            iterator = max.value
        else:
            statement_error("For loop encountered incompatible type to iterate. Can only iterate Numbers and Lists.", stmt)
    else:
        i_min: int = interpret(stmt.quantity_min, env).value
        i_max: int = interpret(stmt.quantity_max, env).value
        iterator = range(i_min, i_max)
        is_range_iterator = True

    # fallback type
    if not stmt.type:
        stmt.type = ast.Type(lexer.Pimitives.INT)

    # for loop has the limited scope iteration variable. Make a new Environment for it.
    scope = Environment(env)
    loopvarname = stmt.identifier
    scope.declare_local(loopvarname, _assign_Type(0, stmt.type), True, stmt)

    # do the loop
    for i in iterator:
        if is_range_iterator:
            scope.assign(loopvarname, IntValue(i), stmt)
        else:
            scope.assign(loopvarname, i, stmt)

        if is_range_iterator:
            value = i  # it is of type numeric (python native)
        else:
            value = i.value  # it is of type RuntypeValue
        scope.assign(loopvarname, _assign_Type(value, stmt.type), stmt)

        last = interpret_block_expression(stmt.body, scope)
        env.state = scope.state  # propagate state outwards
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
    return noneValueInstance


def interpret_block_expression(stmt: ast.BlockStatement, env: Environment) -> RuntimeValue:
    # create a new local environment. C has this, so we need too.
    scope = Environment(env)
    # go through all statements and execute
    last: RuntimeValue = noneValueInstance
    for statement in stmt.body:
        last = interpret(statement, scope)
        env.state = scope.state  # propagate state outwards
        # check for any flow interrupt conditions condition on environment
        if env.state is envstate.BREAK:
            return noneValueInstance
        if env.state is envstate.CONTINUE:
            return noneValueInstance
        if env.state is envstate.RETURN:
            return last
    return noneValueInstance


def interpret_return_expression(stmt: ast.ReturnExpression, env: Environment) -> RuntimeValue:
    if stmt.value:
        # interpret it
        last = interpret(stmt.value, env)
        # set state to return AFTER interpretation, because interpretation might overwrite state.
        env.state = envstate.RETURN
        return last
    # set state to return
    env.state = envstate.RETURN
    return noneValueInstance


def interpret_break_expression(stmt: ast.BreakExpression, env: Environment) -> RuntimeValue:
    env.state = envstate.BREAK
    return noneValueInstance


def interpret_continue_expression(stmt: ast.ContinueExpression, env: Environment) -> RuntimeValue:
    env.state = envstate.CONTINUE
    return noneValueInstance


def interpret_elvis_expression(stmt: ast.ElvisExpression, env: Environment) -> RuntimeValue:
    condition = interpret(stmt.test, env)
    # make the conditional check
    if condition.value:
        return interpret(stmt.consequent, env)
    else:
        return interpret(stmt.alternate, env)


def interpret_list_literal(stmt: ast.ListLiteral, env: Environment) -> RuntimeValue:
    values = [interpret(value, env) for value in stmt.values]
    return ListValue(values)


def interpret_object_literal(stmt: ast.ObjectLiteral, env: Environment) -> RuntimeValue:
    obj = {}
    for property in stmt.properties:
        key: str = property.key
        if property.value:
            property_value: RuntimeValue = interpret(property.value, env)
            obj[key] = property_value
        else:
            environment_value: RuntimeValue = env.lookup(key, stmt)
            obj[key] = environment_value
    return ObjectValue(obj)


# def interpret_tuple_literal(stmt: ast.TupleLiteral, env: Environment) -> RuntimeValue:
#     values = [interpret(value, env) for value in stmt.values]
#     return TupleValue(values)


def interpret_shebang_expression(stmt: ast.ShebangExpression, env: Environment):
    # this is used to configure the interpreter. Conveniently, that is this module.
    # the expression is the entire line
    # #:flolang
    expression = stmt.shebang

    if expression == "#!script":
        env.get_root_env().is_script = True

    return noneValueInstance


def interpret_delete_expression(stmt: ast.DeleteExpression, env: Environment):
    identifier = stmt.identifier
    env.delete(identifier, stmt)
    return noneValueInstance
