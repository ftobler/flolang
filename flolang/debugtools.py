

import flolang.abstract_source_tree as ast

def print_ast_json(tree, indentation = ""):
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
            print(indentation + tree + " " + key + " ╕")
            whitespace = len(key) * " " + "  "
            if obj_terminated:
                tree = " "
            else:
                tree = "│"
            print_ast_json(value.json(), indentation + tree + whitespace)

        elif isinstance(value, list):
            if len(value) == 0:
                print(indentation + tree + " " + key + "[] = []")
            else:
                print(indentation + tree + " " + key + "[] ╕")
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
                    print(indentation + tree + whitespace_list + looptree + " %d " % j + "╕")
                    whitespace_index = len(str(j)) * " " + "  "
                    if list_terminated:
                        looptree = " "
                    else:
                        looptree = "│"
                    print_ast_json(element.json(), indentation + tree + whitespace_list + looptree + whitespace_index)

        else:
            if key != "loc":
                print(indentation + tree + " " + key + ": " + str(value))

def print_ast(ast):
    print_ast_json(ast.json())
    # print(ast)