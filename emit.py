from node import *

def gen_root(root: Node) -> str:
    main = "int main(int argc, char **argv) {\n"
    other = "#include <stdio.h>\n"

    for node in root.root_nodes:
        code = gen_node(node)

        if node.scope_def == "<global>":
            main += code
        else:
            other += code

    return other + main + "    return 0;\n}"

def gen_node(node: Node) -> str:
    if node.type == NOD_ROOT:
        return gen_root(node)
    else:
        print(f"latte: Error: No backend for '{node_type_to_str(node.type)}'.")
        exit()