from node import *

types = {
    "Char": "char",
    "Int": "int32_t",
    "Float": "float"
}

def node_to_value(node: Node) -> str:
    if node.type == NOD_INT:
        return str(int(node.data_digit))
    elif node.type == NOD_FLOAT:
        return str(float(node.data_digit))
    elif node.type == NOD_VAR:
        return node.var_name
    else:
        assert(False)

def gen_assign(node: Node) -> str:
    code = ""

    if node.assign_type is not None:
        code = types[node.assign_type] + " "

    code += node.assign_name + " = "

    if node.assign_value is None:
        return code + ";\n"
    
    return code + node_to_value(node.assign_value) + ";\n"

def gen_root(root: Node) -> str:
    main = "\nint main(int argc, char **argv) {\n"
    other = "#include <stdio.h>\n#include <stdlib.h>\n#include <stdint.h>\n"

    for node in root.root_nodes:
        code = "    " + gen_node(node)

        if node.scope_def == "<global>":
            main += code
        else:
            other += code

    return other + main + "    return 0;\n}"

def gen_node(node: Node) -> str:
    if node.type == NOD_ROOT:
        return gen_root(node)
    elif node.type == NOD_ASSIGN:
        return gen_assign(node)
    else:
        print(f"latte: Error: No backend for '{node_type_to_str(node.type)}'.")
        exit()