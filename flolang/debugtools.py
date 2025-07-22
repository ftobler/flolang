

import flolang.abstract_source_tree as ast


def print_ast_json(tree, indentation="", file=None):
    # ─ │ ┐ ┘ ┌ └ ├ ┤ ┬ ┴ ┼
    # ═ ║ ╒ ╓ ╔ ╕ ╖ ╗ ╘ ╙ ╚ ╛ ╜ ╝ ╞ ╟ ╠ ╡ ╢ ╣ ╤ ╥ ╦ ╧ ╨ ╩ ╪ ╫ ╬
    items = tree.items()
    itemlist = []
    for key, value in items:
        itemlist.append((key, value))
    for i, (key, value) in enumerate(itemlist):
        obj_terminated = False
        if i == len(itemlist) - 1:
            tree = "└"
            obj_terminated = True
        elif i == 0:
            tree = "├"
        else:
            tree = "├"
        if isinstance(value, ast.Statement):
            jsonvalue = value.json()
            print(indentation + tree + " " + key + ": ┬ " + jsonvalue["kind"], file=file)
            whitespace = len(key) * " " + "   "
            if obj_terminated:
                tree = " "
            else:
                tree = "│"
            print_ast_json(jsonvalue, indentation + tree + whitespace, file=file)

        elif isinstance(value, list):
            if len(value) == 0:
                print(indentation + tree + " " + key + "[] = []", file=file)
            else:
                print(indentation + tree + " " + key + "[] ┐", file=file)
                whitespace_list = len(key) * " " + "    "
                if obj_terminated:
                    tree = " "
                else:
                    tree = "│"
                for j, element in enumerate(value):
                    list_terminated = False
                    if j == len(value) - 1:
                        looptree = "└"
                        list_terminated = True
                    elif j == 0:
                        looptree = "├"
                    else:
                        looptree = "├"
                    jsonvalue = element.json()
                    print(indentation + tree + whitespace_list + looptree + " %d " % j + "┬ " + jsonvalue["kind"], file=file)
                    whitespace_index = len(str(j)) * " " + "  "
                    if list_terminated:
                        looptree = " "
                    else:
                        looptree = "│"
                    print_ast_json(jsonvalue, indentation + tree + whitespace_list + looptree + whitespace_index, file=file)

        else:
            if key != "ldoc" and key != "kind":
                if isinstance(value, str):
                    value = "'" + value + "'"
                print(indentation + tree + " " + key + ": " + str(value), file=file)


def print_ast(ast: ast.Statement, file=None):
    print_ast_json(ast.json(), file=file)
    # print(ast)
