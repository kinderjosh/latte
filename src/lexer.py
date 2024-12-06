import os

TOK_EOF = 0
TOK_ID = 1
TOK_INT = 2
TOK_FLOAT = 3
TOK_LPAREN = 4
TOK_RPAREN = 5
TOK_LBRACE = 7
TOK_RBRACE = 8
TOK_COLON = 9
TOK_COMMA = 10
TOK_EQUAL = 11
TOK_SEMI = 12
TOK_STR = 13
TOK_LSQUARE = 14
TOK_RSQUARE = 15

def tok_type_to_str(type: int) -> str:
    if type == TOK_EOF:
        return "<EOF>"
    elif type == TOK_ID:
        return "Identifier"
    elif type == TOK_INT:
        return "Int"
    elif type == TOK_FLOAT:
        return "Float"
    elif type == TOK_LPAREN:
        return "Left paren"
    elif type == TOK_RPAREN:
        return "Right paren"
    elif type == TOK_LBRACE:
        return "Left brace"
    elif type == TOK_RBRACE:
        return "Right brace"
    elif type == TOK_COLON:
        return "Colon"
    elif type == TOK_COMMA:
        return "Comma"
    elif type == TOK_EQUAL:
        return "Equal"
    elif type == TOK_SEMI:
        return "Semicolon"
    elif type == TOK_STR:
        return "String"
    elif type == TOK_LSQUARE:
        return "Left square"
    elif type == TOK_RSQUARE:
        return "Right square"
    else:
        return "<Undefined>"

class Tok:
    def __init__(self, type: int, value: str, ln: int, col: int) -> None:
        self.type = type
        self.value = value
        self.ln = ln
        self.col = col

class Lex:
    def __init__(self, file: str) -> None:
        if not os.path.exists(file):
            print(f"{file}: Error: No such file exists.")
            exit()

        self.file = file
        
        with open(self.file, "r") as f:
            self.src = f.read() + '\0'

        self.ch = self.src[0]
        self.pos = 0
        self.ln = 1
        self.col = 1

    def step(self) -> None:
        if self.pos >= len(self.src):
            return
        
        if self.ch == '\n':
            self.ln += 1
            self.col = 1
        else:
            self.col += 1

        self.pos += 1
        self.ch = self.src[self.pos]

    def peek(self, offset: int) -> str:
        if self.pos + offset >= len(self.src):
            return self.src[-1]
        elif self.pos + offset <= 0:
            return self.src[0]
        return self.src[self.pos + offset]
    
    def step_with(self, type: int, value: str) -> Tok:
        tok = Tok(type, value, self.ln, self.col)
        for i in range(len(value)):
            self.step()
        return tok
    
    def next(self) -> Tok:
        while self.ch == ' ' or self.ch == '\t' or self.ch == '\n':
            self.step()

        if self.ch == '/' and self.peek(1) == '/':
            while self.ch != '\n' and self.ch != '\0':
                self.step()

            self.step()
            return self.next()

        if self.ch.isalpha() or self.ch == '_':
            value = ""

            while self.ch.isalpha() or self.ch == '_':
                value += self.ch
                self.step()

            return Tok(TOK_ID, value, self.ln, self.col - len(value))
        elif self.ch.isdigit() or (self.ch == '-' and self.peek(1).isdigit()):
            value = ""
            is_float = False

            while self.ch.isdigit() or (self.ch == '-' and len(value) < 1) or (self.ch == '.' and self.peek(1).isdigit() and not is_float):
                if self.ch == '.':
                    is_float = True
                
                value += self.ch
                self.step()

            if is_float:
                return Tok(TOK_FLOAT, value, self.ln, self.col - len(value))
            return Tok(TOK_INT, value, self.ln, self.col - len(value))
        elif self.ch == '\"':
            self.step()
            value = ""

            while (self.ch != '\"' or self.peek(-1) == '\\') and self.ch != '\n' and self.ch != '\0':
                if self.ch == '\\' and self.peek(1) == '"':
                    self.step()

                value += self.ch
                self.step()

            if self.ch != '\"':
                print(f"{self.file}:{self.ln}:{self.col - len(value) - 1}: Error: Unclosed string literal.")
                exit()

            self.step()
            return Tok(TOK_STR, value, self.ln, self.col - len(value) - 2)
        elif self.ch == '\'':
            col = self.col
            self.step()
            value = ""

            if self.ch == '\\':
                self.step()

                if self.ch == 'n':
                    value = "10"
                elif self.ch == 't':
                    value = "9"
                elif self.ch == "r":
                    value = "13"
                elif self.ch == "0":
                    value = "0"
                elif self.ch in ['\\', '\'', '\"']:
                    value = chr(self.ch[0])
                else:
                    print(f"{self.file}:{self.ln}:{col}: Error: Unsupported escape sequence '\\{self.ch}'.")
                    exit()
            else:
                value = chr(self.ch[0])

            self.step()

            if self.ch != '\'':
                print(f"{self.file}:{self.ln}:{col}: Error: Unclosed character constant.")
                exit()

            self.step()
            return Tok(TOK_INT, value, self.ln, col)
        
        if self.ch == '\0':
            return Tok(TOK_EOF, "<EOF>", self.ln, self.col)
        elif self.ch == '(':
            return self.step_with(TOK_LPAREN, "(")
        elif self.ch == ')':
            return self.step_with(TOK_RPAREN, ")")
        elif self.ch == '{':
            return self.step_with(TOK_LBRACE, "{")
        elif self.ch == '}':
            return self.step_with(TOK_RBRACE, "}")
        elif self.ch == ':':
            return self.step_with(TOK_COLON, ":")
        elif self.ch == ',':
            return self.step_with(TOK_COMMA, ",")
        elif self.ch == '=':
            return self.step_with(TOK_EQUAL, "=")
        elif self.ch == ';':
            return self.step_with(TOK_SEMI, ";")
        elif self.ch == '[':
            return self.step_with(TOK_LSQUARE, "[")
        elif self.ch == ']':
            return self.step_with(TOK_RSQUARE, "]")
        else:
            print(f"{self.file}:{self.ln}:{self.col}: Error: Unknown character '{self.ch}'.")
            exit()