from lexer import *
from node import *

cur_scope = "<global>"
cur_func = "<global>"

def sym_find(type: int, scope: str, name: str) -> Node:
    for sym in sym_tab:
        if sym.type != type or (sym.scope_def != scope and sym.scope_def != "<global>" and scope != "<global>"):
            continue
        elif (sym.type == NOD_FUNC and sym.func_name == name) or (sym.type == NOD_ASSIGN and sym.assign_name == name):
            return sym
    return None

def is_type(id: str) -> bool:
    return True if id in ["Void", "Char", "Int", "Float", "String"] else False

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

            if self.tok.type == TOK_LSQUARE:
                self.eat(TOK_LSQUARE)
                self.eat(TOK_RSQUARE)
                id += "[]"

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
        elif value.type == NOD_VAR or value.type == NOD_STR or value.type == NOD_LIST or value.type == NOD_SUBSCR:
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
            if stmt.type not in [NOD_CALL, NOD_ASSIGN, NOD_RET, NOD_NOP, NOD_C, NOD_SUBSCR]:
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

        is_global = False
        if id == "Global":
            is_global = True

        if is_type(id) or id == "Global":
            if id == "Global":
                id = self.prs_type()

            if self.tok.type == TOK_LSQUARE:
                if type == "Void":
                    print(f"{self.file}:{ln}:{col}: Error: Illegal list type 'Void'.")
                    exit()

                self.eat(TOK_LSQUARE)
                self.eat(TOK_RSQUARE)
                id += "[]"

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
                node.is_global = is_global
                
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

                sym = sym_find(NOD_FUNC, "<global>", name)
                if sym is None:
                    node.func_params = params
                    sym_tab.append(node)
                elif len(params) != len(sym.func_params):
                    print(f"{self.file}:{ln}:{col}: Error: Function '{name}' was originally defined with {len(sym.func_params)} parameters at {sym.ln}:{sym.col}, but found {len(params)}.")
                    exit()

                if self.tok.type == TOK_SEMI:
                    node.func_params = params
                    return Node(NOD_NOP, "<None", "<None", 0, 0)

                node.func_params = params
                node.func_body = self.prs_body()
                ret = None

                if len(node.func_body) > 0 and node.func_body[-1].type == NOD_RET:
                    ret = node.func_body[-1]

                if node.func_type != "Void" and ret is None:
                    print(f"{self.file}:{ln}:{col}: Error: Missing return statement in function '{name}' of type '{node.func_type}'.")
                    exit()

                sym_tab[node.index] = node
                cur_scope = "<global>"
                cur_func = "<global>"
                return node
            
            if type == "Void":
                print(f"{self.file}:{ln}:{col}: Error: Illegal variable type 'Void'.")
                exit()
            
            node = Node(NOD_ASSIGN, cur_scope, cur_func, ln, col)
            node.assign_name = name
            node.assign_type = type
            node.is_global = is_global

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
        elif id == "__C__":
            self.eat(TOK_LPAREN)
            code = self.tok.value
            self.eat(TOK_STR)
            self.eat(TOK_RPAREN)

            node = Node(NOD_C, cur_scope, cur_func, ln, col)
            node.c_code = code
            return node
        elif id == "import":
            name = self.tok.value
            self.eat(TOK_ID)

            if ".pw" in name:
                print(f"{self.file}:{ln}:{col}: Error: Redundant file extension in import name {name}.")
                exit()

            if not os.path.exists(name + ".pw"):
                if "\\" in self.file:
                    path = self.file.rpartition('\\')[0] + "\\" + name
                    if not os.path.exists(path + ".pw"):
                        print(f"{self.file}:{ln}:{col}: Error: No such file '{name}.pw' to import.")
                        exit()

            node = Node(NOD_IMPORT, cur_scope, cur_func, ln, col)
            node.import_nodes = Prs(path + ".pw").prs().root_nodes
            return node
        elif self.tok.type == TOK_LSQUARE:
            sym = sym_find(NOD_ASSIGN, cur_scope, id)
            if sym is None:
                print(f"{self.file}:{ln}:{col}: Error: Undefined variable '{id}'.")
                exit()

            self.eat(TOK_LSQUARE)
            index = self.prs_value("<None>")
            self.eat(TOK_RSQUARE)

            node = Node(NOD_SUBSCR, cur_scope, cur_func, ln, col)
            node.subscr_name = id
            node.subscr_index = index

            if self.tok.type == TOK_EQUAL:
                self.eat(TOK_EQUAL)
                node.subscr_assign = self.prs_value(sym.assign_type)
            else:
                node.subscr_assign = None

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
        elif self.tok.type == TOK_LPAREN:
            sym = sym_find(NOD_FUNC, "<global>", id)
            if sym is None:
                print(f"{self.file}:{ln}:{col}: Error: Undefined function '{id}'.")
                exit()

            args = []
            self.eat(TOK_LPAREN)

            while self.tok.type != TOK_RPAREN and self.tok.type != TOK_EOF:
                if len(args) >= len(sym.func_params):
                    print(f"{self.file}:{ln}:{col}: Error: Excessive argument in call to function '{id}'; expected {len(sym.func_params)} but found {len(args)}.")
                    exit()
                elif len(args) > 0:
                    self.eat(TOK_COMMA)

                args.append(self.prs_value(sym.func_params[len(args)].assign_type))

            if len(args) < len(sym.func_params):
                print(f"{self.file}:{ln}:{col}: Error: Missing argument in call to function '{id}'; expected {len(sym.func_params)} but found {len(args)}.")
                exit()

            self.eat(TOK_RPAREN)

            node = Node(NOD_CALL, cur_scope, cur_func, ln, col)
            node.call_name = id
            node.call_args = args
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
        node = None

        if self.tok.type == TOK_STR:
            node = Node(NOD_STR, cur_scope, cur_func, self.tok.ln, self.tok.col)
            node.data_str = self.tok.value
        else:
            node = Node(NOD_INT if self.tok.type == TOK_INT else NOD_FLOAT, cur_scope, cur_func, self.tok.ln, self.tok.col)
            node.data_digit = float(self.tok.value)

        self.eat(self.tok.type)
        return node
    
    def prs_list(self) -> None:
        ln = self.tok.ln
        col = self.tok.col
        self.eat(TOK_LSQUARE)
        items = []

        while self.tok.type != TOK_RSQUARE and self.tok.type != TOK_EOF:
            if len(items) > 0:
                self.eat(TOK_COMMA)

            items.append(self.prs_value("<None>"))

        self.eat(TOK_RSQUARE)

        node = Node(NOD_LIST, cur_scope, cur_func, ln, col)
        node.list_items = items
        return node
    
    def prs_stmt(self) -> Node:
        if self.tok.type == TOK_ID:
            return self.prs_id()
        elif self.tok.type == TOK_INT or self.tok.type == TOK_FLOAT or self.tok.type == TOK_STR:
            return self.prs_data()
        elif self.tok.type == TOK_LSQUARE:
            return self.prs_list()
        else:
            print(f"{self.file}:{self.tok.ln}:{self.tok.col}: Error: Invalid statement '{tok_type_to_str(self.tok.type)}'.")
            exit()
    
    def prs(self) -> list[Node]:
        nodes = []

        while self.tok.type != TOK_EOF:
            node = self.prs_stmt()
            if not node.type in [NOD_FUNC, NOD_CALL, NOD_ASSIGN, NOD_NOP, NOD_C, NOD_SUBSCR, NOD_IMPORT]:
                print(f"{self.file}:{node.ln}:{node.col}: Error: Invalid statement '{node_type_to_str(node.type)}'.")
                exit()

            if node.type != NOD_FUNC:
                self.eat(TOK_SEMI)

            if node.type == NOD_IMPORT:
                for i in node.import_nodes:
                    nodes.append(i)
                continue

            nodes.append(node)

        for sym in sym_tab:
            if sym.type == NOD_FUNC and sym.func_body is None:
                print(f"{self.file}:{sym.ln}:{sym.col}: Error: Function '{sym.func_name}' was predefined but the body was never declared.")
                exit()

        root = Node(NOD_ROOT, "<internal>", "<internal>", 0, 0)
        root.root_nodes = nodes
        return root