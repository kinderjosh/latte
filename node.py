NOD_ROOT = 0
NOD_INT = 1
NOD_FLOAT = 2
NOD_VAR = 3
NOD_FUNC = 4
NOD_CALL = 5
NOD_ASSIGN = 6
NOD_RET = 7
NOD_NOP = 8

def node_type_to_str(type: int) -> str:
    if type == NOD_ROOT:
        return "<Root>"
    elif type == NOD_INT:
        return "Int"
    elif type == NOD_FLOAT:
        return "Float"
    elif type == NOD_VAR:
        return "Variable"
    elif type == NOD_FUNC:
        return "Function"
    elif type == NOD_CALL:
        return "Function call"
    elif type == NOD_ASSIGN:
        return "Assignment"
    elif type == NOD_RET:
        return "Return"
    elif type == NOD_NOP:
        return "<Nop>"
    else:
        return "<Undefined>"

class Node:
    def __init__(self, type: int, scope_def: str, func_def: str, ln: int, col: int) -> None:
        self.type = type
        self.scope_def = scope_def
        self.func_def = func_def
        self.ln = ln
        self.col = col