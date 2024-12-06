from node import *
from parser import sym_find

types = {
    "Void": "void",
    "Char": "char",
    "Int": "int32_t",
    "Float": "float",
    "String": "char*",
    "Char[]": "char*",
    "Int[]" : "int*",
    "Float[]": "float*",
    "String[]": "char**"
}

double_lists_to_free = []

def free_double_lists() -> str:
    global double_lists_to_free
    code = ""

    for lst in double_lists_to_free:
        code += f"for (size_t i = 0; i < {lst.list_size}; i++)\nfree({lst.assign_name}_[i]);\n"

    double_lists_to_free = []
    return code

def node_to_value(node: Node) -> str:
    if node.type == NOD_INT:
        return str(int(node.data_digit))
    elif node.type == NOD_FLOAT:
        return str(float(node.data_digit))
    elif node.type == NOD_STR:
        return f"newstr(\"{node.data_str}\")"
    elif node.type == NOD_VAR:
        return node.var_name + "_"
    elif node.type == NOD_CALL:
        code = gen_call(node)
        code = code[:-2] # Remove ';\n'
        return code
    elif node.type == NOD_SUBSCR:
        return f"{node.subscr_name}_[{node_to_value(node.subscr_index)}]"
    else:
        assert(False)

def gen_func(node: Node) -> str:
    code = types[node.func_type] + " " + node.func_name + "_("
    if len(node.func_params) > 0:
        for i, param in enumerate(node.func_params):
            code += types[param.assign_type] + " " + param.assign_name + "_"

            if i != len(node.func_params) - 1:
                code += ", "

    code += ") {\n"

    for stmt in node.func_body:
        code += gen_node(stmt)

    return code + free_double_lists() + "}\n"

def gen_call(node: Node) -> str:
    code = node.call_name + "_("

    for i, arg in enumerate(node.call_args):
        code += node_to_value(arg)

        if i != len(node.call_args) - 1:
            code += ", "

    return code + ");\n"

def gen_assign(node: Node) -> str:
    global double_lists_to_free
    code = ""

    if node.assign_type is not None:
        code = types[node.assign_type] + " "

    code += node.assign_name + "_ = "
    
    sym = sym_find(NOD_ASSIGN, node.scope_def, node.assign_name)
    
    #if node.assign_value.type == NOD_LIST:
    if "[]" in sym.assign_type:
        before_code = None

        if node.assign_type is None and types[sym.assign_type].count("*") > 1 and node.list_size > 0:
            before_code = f"for (size_t i = 0; i < {node.list_size}; i++)\nfree({node.assign_name}_[i]);\n"

        items = []
        size = 0

        if node.assign_value is not None:
            items = node.assign_value.list_items
            size = 1 if len(items) < 1 else len(items)

        basetype = types[sym.assign_type]
        if basetype.count("*") > 1:
            basetype = basetype[:-1]
        else:
            basetype = basetype.split("*")[0]
        
        if node.assign_type is not None:
            code += f"calloc({1 if size == 0 else size}, sizeof({basetype}));\ngc_add({node.assign_name}_, sizeof({types[node.assign_type]}));\n"

            if types[node.assign_type].count("*") > 1:
                double_lists_to_free.append(node)
        else:
            code += f"realloc({node.assign_name}_, {size} * sizeof({basetype}));\n"

        if len(items) > 0:
            for i, item in enumerate(items):
                code += f"{node.assign_name}_[{i}] = {node_to_value(item)};\n"

        sym.list_size = len(items)

        if before_code is not None:
            return before_code + code
        
        return code
    elif node.assign_value is None:
        return code + ";\n"
    
    return code + node_to_value(node.assign_value) + ";\n"

def gen_ret(node: Node) -> str:
    code = "return"
    
    if node.ret_value is not None:
        code += " " + node_to_value(node.ret_value)

    return code + ";\n"

def gen_root(root: Node) -> str:
    global double_lists_to_free
    main = "\nint main(int argc, char** argv) {\ngc_init();\n"
    other = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <stdint.h>\n\nvoid** gc;\nsize_t gc_cnt = 0, gc_size = 0;\n\nvoid gc_init() {\ngc = malloc(1);\n}\n\nvoid gc_add(void* ptr, size_t size) {\ngc_size += size;\ngc = realloc(gc, gc_size);\ngc[gc_cnt++] = ptr;\n}\n\nvoid gc_free() {\nfor (size_t i = 0; i < gc_cnt; i++)\nfree(gc[i]);\nfree(gc);\n}\n\nchar* newstr(char *str) {\nchar *new = calloc(strlen(str) + 1, sizeof(char));\nstrcpy(new, str);\nreturn new;\n}\n\n"

    for node in root.root_nodes:
        stmt = gen_node(node)

        if node.type != NOD_FUNC:
            main += stmt
        else:
            double_lists_cache = double_lists_to_free
            other += stmt
            double_lists_to_free = double_lists_cache

    return other + main + free_double_lists() + "gc_free();\nreturn 0;\n}"

def gen_subscr(node: Node) -> str:
    return f"{node.subscr_name}_[{node_to_value(node.subscr_index)}] = {node_to_value(node.subscr_assign)};\n"

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
    elif node.type == NOD_C:
        return node.c_code + "\n"
    elif node.type == NOD_SUBSCR:
        return gen_subscr(node)
    else:
        print(f"pwc: Error: No backend for '{node_type_to_str(node.type)}'.")
        exit()