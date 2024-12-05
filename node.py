sym_tab = []

NOD_ROOT = 0
NOD_INT = 1
NOD_FLOAT = 2
NOD_VAR = 3
NOD_FUNC = 4
NOD_CALL = 5
NOD_ASSIGN = 6
NOD_RET = 7
NOD_NOP = 8
NOD_STR = 9
NOD_C = 10
NOD_LIST = 11
NOD_SUBSCR = 12

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
    elif type == NOD_STR:
        return "String"
    elif type == NOD_C:
        return "<C code>"
    elif type == NOD_LIST:
        return "List"
    elif type == NOD_SUBSCR:
        return "Array subscript"
    else:
        return "<Undefined>"

class Node:
    def __init__(self, type: int, scope_def: str, func_def: str, ln: int, col: int) -> None:
        self.type = type
        self.scope_def = scope_def
        self.func_def = func_def
        self.ln = ln
        self.col = col
        self.index = 0 if len(sym_tab) < 1 else len(sym_tab) - 1 # Just for re-updating functions