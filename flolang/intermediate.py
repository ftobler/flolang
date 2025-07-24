from flolang import abstract_source_tree as ast
from flolang.error import compile_error


def intermediate_error(message, stmt: ast.Statement):
    mesg = message + " In '%s' statement." % stmt.kind
    compile_error(mesg, stmt.loc)


class NoStatement(ast.Statement):

    def __repr__(self):
        return "?"


class Instruction:
    "Intermediate Representation Instruction base class"
    def __init__(self, stmt: ast.Statement):
        self.kind = type(self).__name__
        self.stmt = stmt

    def __repr__(self):
        return str(self.json())

    def json(self):
        return vars(self)

    def statement(self, stmt: ast.Statement):
        self.stmt = stmt
        return self


class UnreachableInstruction(Instruction):
    ...


class ProgramStartInstruction(Instruction):
    ...


class ProgramEndInstruction(Instruction):
    ...


class Program:
    def __init__(self, stmt: ast.Program):
        self.list: list[Instruction] = []

        assert isinstance(stmt, ast.Program)

        self.dump_program(stmt)

    def dump_program(self, node: ast.Program):
        self.list.append(ProgramStartInstruction(node))
        for stmt in node.body:
            if isinstance(stmt, ast.ShebangExpression):
                pass  # shebang does not concern. It is ignored
            elif isinstance(stmt, ast.VariableDeclaration):
                self.dump_variable_declaration(stmt)
            elif isinstance(stmt, ast.FunctionDeclaration):
                self.dump_function_declaration(stmt)
            elif isinstance(stmt, ast.ClassDeclaration):
                self.dump_class_declaration(stmt)
            elif isinstance(stmt, ast.EnumDeclaration):
                self.dump_enum_declaration(stmt)
        self.list.append(ProgramEndInstruction(node))

    def dump_function_declaration(self, stmt: ast.Statement):
        pass

    def dump_variable_declaration(self, stmt: ast.Statement):
        pass

    def dump_class_declaration(self, stmt: ast.Statement):
        pass

    def dump_enum_declaration(self, stmt: ast.Statement):
        pass
