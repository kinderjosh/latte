from node import *

types = {
    "Void": "void",
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
    elif node.type == NOD_CALL:
        return gen_call(node)
    else:
        assert(False)

def gen_func(node: Node) -> str:
    code = types[node.func_type] + " " + node.func_name + "_("
    if len(node.func_params) > 0:
        for i, param in enumerate(node.func_params):
            code += types[param.assign_type] + " " + param.assign_name

            if i != len(node.func_params) - 1:
                code += ", "

    code += ") {\n"

    for stmt in node.func_body:
        code += "    " + gen_node(stmt)

    return code + "}\n"

def gen_call(node: Node) -> str:
    code = node.call_name + "_("

    for i, arg in enumerate(node.call_args):
        code += node_to_value(arg)

        if i != len(node.call_args) - 1:
            code += ", "

    return code + ")"

def gen_assign(node: Node) -> str:
    code = ""

    if node.assign_type is not None:
        code = types[node.assign_type] + " "

    code += node.assign_name + " = "

    if node.assign_value is None:
        return code + ";\n"
    
    return code + node_to_value(node.assign_value) + ";\n"

def gen_ret(node: Node) -> str:
    code = "return"
    
    if node.ret_value is not None:
        code += " " + node_to_value(node.ret_value)

    return code + ";\n"

def gen_root(root: Node) -> str:
    main = "\nint main(int argc, char **argv) {\n"
    other = "#include <stdio.h>\n#include <stdlib.h>\n#include <stdint.h>\n\n"

    for node in root.root_nodes:
        stmt = gen_node(node)

        if node.type != NOD_FUNC:
            main += "    " + stmt
        else:
            other += stmt

    return other + main + "    return 0;\n}"

def gen_node(node: Node) -> str:
    if node.type == NOD_ROOT:
        return gen_root(node)
    elif node.type == NOD_FUNC:
        return gen_func(node)
    elif node.type == NOD_CALL:
        return gen_call(node)
    elif node.type == NOD_ASSIGN:
        return gen_assign(node)
    elif node.type == NOD_RET:
        return gen_ret(node)
    elif node.type == NOD_NOP:
        return ""
    else:
        print(f"latte: Error: No backend for '{node_type_to_str(node.type)}'.")
        exit()