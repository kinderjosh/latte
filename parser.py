from lexer import *
from node import *

scope_def = "<global>"
func_def = "<global>"

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
    
    def prs_id(self) -> Node:
        ln = self.tok.ln
        col = self.tok.col
        id = self.tok.value
        self.eat(TOK_ID)

        print(f"{self.file}:{ln}:{col}: Error: Unknown identifier '{id}'.")
        exit()

    def prs_data(self) -> Node:
        node = Node(NOD_INT if self.tok.type == TOK_INT else NOD_FLOAT, scope_def, func_def, self.tok.ln, self.tok.col)
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
            if not node.type in [NOD_FUNC, NOD_CALL, NOD_ASSIGN]:
                print(f"{self.file}:{node.ln}:{node.col}: Error: Invalid statement '{node_type_to_str(node.type)}'.")
                exit()

            nodes.append(node)

        root = Node(NOD_ROOT, "<internal>", "<internal>", 0, 0)
        root.root_nodes = nodes
        return root