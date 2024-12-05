from lexer import *
from node import *

cur_scope = "<global>"
cur_func = "<global>"
sym_tab = []

def sym_find(type: int, scope: str, name: str) -> Node:
    for sym in sym_tab:
        if sym.type != type or (sym.scope_def != scope and sym.scope_def != "<global>" and scope != "<global>"):
            continue
        elif (sym.type == NOD_FUNC and sym.func_name == name) or (sym.type == NOD_ASSIGN and sym.assign_name == name):
            return sym
    return None

def is_type(id: str) -> bool:
    return True if id in ["Void", "Char", "Int", "Float"] else False

class Prs:
    def __init__(self, file: str) -> None:
        self.file = file
        self.lex = Lex(file)
        self.tok = self.lex.next()

    def eat(self, type: int) -> int:
        if type != self.tok.type:
            print(f"{self.file}:{self.tok.ln}:{self.tok.col}: Error: Expected '{tok_type_to_str(type)}' but found '{tok_type_to_str(self.tok.type)}'.")
            exit()

        eaten = self.tok.type
        if eaten != TOK_EOF:
            self.tok = self.lex.next()
        return eaten
    
    def prs_type(self) -> str:
        if is_type(self.tok.value):
            id = self.tok.value
            self.eat(self.tok.type)
            return id
        
        print(f"{self.file}:{self.tok.ln}:{self.tok.col}: Error: Invalid datatype '{self.tok.value}'.")
        exit()

    def prs_value(self, type: str) -> Node:
        value = self.prs_stmt()
        if value.type == NOD_INT or value.type == NOD_FLOAT:
            if value.type == NOD_FLOAT and type != "Float":
                value.type = NOD_INT

            if type == "Char" and (value.data_digit > 128 or value.data_digit < -127):
                value.data_digit = 0
            elif (type == "Int" or type == "Float") and (value.data_digit > (2**32) - 1 or value.data_digit < -(2**32)):
                value.data_digit = 0
        elif value.type == NOD_VAR:
            pass
        elif value.type == NOD_CALL:
            sym = sym_find(NOD_FUNC, "<global>", value.call_name)
            if sym.func_type == "<None>":
                print(f"{self.file}:{value.ln}:{value.col}: Error: Function '{value.call_name}' doesn't return a value.")
                exit()
        else:
            print(f"{self.file}:{value.ln}:{value.col}: Error: Invalid value '{node_type_to_str(value.type)}'.")
            exit()

        return value
    
    def prs_body(self) -> list[Node]:
        body = []
        self.eat(TOK_LBRACE)

        while self.tok.type != TOK_RBRACE and self.tok.type != TOK_EOF:
            stmt = self.prs_stmt()
            if stmt.type not in [NOD_CALL, NOD_ASSIGN, NOD_RET, NOD_NOP]:
                print(f"{self.file}:{stmt.ln}:{stmt.col}: Error: Invalid statement '{node_type_to_str(stmt.type)}' in function '{cur_func}'.")
                exit()

            self.eat(TOK_SEMI)
            body.append(stmt)

        self.eat(TOK_RBRACE)
        return body
    
    def prs_id(self) -> Node:
        global cur_scope
        global cur_func
        ln = self.tok.ln
        col = self.tok.col
        id = self.tok.value
        self.eat(TOK_ID)

        if is_type(id):
            type = id
            name = self.tok.value
            self.eat(TOK_ID)

            sym = sym_find(NOD_FUNC, "<global>", name)
            if sym is not None and sym.func_body is not None:
                print(f"{self.file}:{ln}:{col}: Error: Redefinition of function '{name}'; first defined at {sym.ln}:{sym.col}.")
                exit()
            
            sym = sym_find(NOD_ASSIGN, cur_scope, id)
            if sym is not None:
                print(f"{self.file}:{ln}:{col}: Error: Redefinition of variable '{name}'; first defined at {sym.ln}:{sym.col}.")
                exit()

            if self.tok.type == TOK_LPAREN:
                node = Node(NOD_FUNC, "<global>", "<global>", ln, col)
                node.func_name = name
                node.func_type = type
                node.func_body = None
                
                params = []
                self.eat(TOK_LPAREN)

                cur_scope = name
                cur_func = name

                while self.tok.type != TOK_RPAREN and self.tok.type != TOK_EOF:
                    if len(params) > 0:
                        self.eat(TOK_COMMA)

                    param = self.prs_stmt()
                    if param.type != NOD_ASSIGN:
                        print(f"{self.file}:{param.ln}:{param.col}: Error: Expected parameter definition but found '{node_type_to_str(param.type)}'.")
                        exit()
                    elif param.assign_value is not None:
                        print(f"{self.file}:{param.ln}:{param.col}: Error: Assigning parameter '{param.assign_name}' outside of function body.")
                        exit()

                    params.append(param)

                self.eat(TOK_RPAREN)
                node.func_params = params

                sym = sym_find(NOD_FUNC, "<global>", name)
                if sym is None:
                    sym_tab.append(node)

                if self.tok.type == TOK_SEMI:
                    return Node(NOD_NOP, "<None", "<None", 0, 0)

                node.func_body = self.prs_body()
                ret = None

                if len(node.func_body) > 0 and node.func_body[-1].type == NOD_RET:
                    ret = node.func_body[-1]

                if node.func_type != "Void" and ret is None:
                    print(f"{self.file}:{ln}:{col}: Error: Missing return statement in function '{name}' of type '{node.func_type}'.")
                    exit()

                cur_scope = "<global>"
                cur_func = "<global>"
                return node
            
            node = Node(NOD_ASSIGN, cur_scope, cur_func, ln, col)
            node.assign_name = name
            node.assign_type = type

            if self.tok.type == TOK_EQUAL:
                self.eat(TOK_EQUAL)
                node.assign_value = self.prs_value(node.assign_type)
            else:
                node.assign_value = None

            sym_tab.append(node)
            return node
        elif id == "return":
            if cur_scope == "<global>":
                print(f"{self.file}:{ln}:{col}: Error: Invalid statement 'Return' outside of a function.")
                exit()

            sym = sym_find(NOD_FUNC, "<global>", cur_func)
            if sym.func_type == "<None>" and self.tok.type != TOK_SEMI:
                print(f"{self.file}:{ln}:{col}: Error: Unexpected return value in function '{cur_func}'.")
                exit()
            elif sym.func_type != "<None>" and self.tok.type == TOK_SEMI:
                print(f"{self.file}:{ln}:{col}: Error: Missing return value in function '{cur_func}' of type '{sym.func_type}'.")
                exit()

            node = Node(NOD_RET, cur_scope, cur_func, ln, col)

            if self.tok.type == TOK_SEMI:
                node.ret_value = None
            else:
                node.ret_value = self.prs_value(sym.func_type)

            return node
        elif self.tok.type == TOK_EQUAL:
            sym = sym_find(NOD_ASSIGN, cur_scope, id)
            if sym is None:
                print(f"{self.file}:{ln}:{col}: Error: Undefined variable '{id}'.")
                exit()

            node = Node(NOD_ASSIGN, cur_scope, cur_func, ln, col)
            node.assign_name = id
            node.assign_type = None
            self.eat(TOK_EQUAL)
            node.assign_value = self.prs_value(sym.assign_type)
            return node
        elif sym_find(NOD_ASSIGN, cur_scope, id) is not None:
            node = Node(NOD_VAR, cur_scope, cur_func, ln, col)
            node.var_name = id
            return node

        print(f"{self.file}:{ln}:{col}: Error: Unknown identifier '{id}'.")
        exit()

    def prs_data(self) -> Node:
        global cur_scope
        global cur_func
        node = Node(NOD_INT if self.tok.type == TOK_INT else NOD_FLOAT, cur_scope, cur_func, self.tok.ln, self.tok.col)
        node.data_digit = float(self.tok.value)
        self.eat(self.tok.type)
        return node
    
    def prs_stmt(self) -> Node:
        if self.tok.type == TOK_ID:
            return self.prs_id()
        elif self.tok.type == TOK_INT or self.tok.type == TOK_FLOAT:
            return self.prs_data()
        else:
            print(f"{self.file}:{self.tok.ln}:{self.tok.col}: Error: Invalid statement '{tok_type_to_str(self.tok.type)}'.")
            exit()
    
    def prs(self) -> list[Node]:
        nodes = []

        while self.tok.type != TOK_EOF:
            node = self.prs_stmt()
            if not node.type in [NOD_FUNC, NOD_CALL, NOD_ASSIGN, NOD_NOP]:
                print(f"{self.file}:{node.ln}:{node.col}: Error: Invalid statement '{node_type_to_str(node.type)}'.")
                exit()

            if node.type != NOD_FUNC:
                self.eat(TOK_SEMI)

            nodes.append(node)

        root = Node(NOD_ROOT, "<internal>", "<internal>", 0, 0)
        root.root_nodes = nodes
        return root