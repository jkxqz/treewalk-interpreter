from token_ import Token
from tokentype import TokenType

class Scanner:

    keywords: dict[str, TokenType] = {
        "and":      TokenType.AND,
        "class":    TokenType.CLASS,
        "else":     TokenType.ELSE,
        "false":    TokenType.FALSE,
        "for":      TokenType.FOR,
        "fun":      TokenType.FUN,
        "if":       TokenType.IF,
        "nil":      TokenType.NIL,
        "or":       TokenType.OR,
        "print":    TokenType.PRINT,
        "return":   TokenType.RETURN,
        "super":    TokenType.SUPER,
        "this":     TokenType.THIS,
        "true":     TokenType.TRUE,
        "var":      TokenType.VAR,
        "while":    TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source : str = source
        self.tokens : list[Token] = []
        self.start  : int = 0
        self.current: int = 0
        self.line   : int = 1

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current-1]

    #def addToken(self, type: TokenType):
    #    self.addToken(type, None)
    
    def addToken(self, type: TokenType, literal: object = None):
        text: str = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)

    def _match(self, expected: str) -> bool:
        if (self.isAtEnd()): return False
        if (self.source[self.current]!=expected): return False
        self.current += 1
        return True
    
    def scanToken(self) -> None:
        c : str = self.advance()
        match c:
            case '(': self.addToken(TokenType.LEFT_PAREN)
            case ')': self.addToken(TokenType.RIGHT_PAREN)
            case '{': self.addToken(TokenType.LEFT_BRACE)
            case '}': self.addToken(TokenType.RIGHT_BRACE)
            case ',': self.addToken(TokenType.COMMA)
            case '.': self.addToken(TokenType.DOT)
            case '-': self.addToken(TokenType.MINUS)
            case '+': self.addToken(TokenType.PLUS)
            case ';': self.addToken(TokenType.SEMICOLON)
            case '*': self.addToken(TokenType.STAR)
            case '!': self.addToken(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
            case '=': self.addToken(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
            case '<': self.addToken(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
            case '>': self.addToken(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
            case '/': 
                if self._match('/'):
                     while (self.peek() not in ('\n', '\0')):
                        self.advance()
                else:
                    self.addToken(TokenType.SLASH)
            case ' ' | '\r' | '\t': # skip whitespace
                return
            case '\n':
                self.line += 1
            case '"': self.string()
            case _:
                if (self.isDigit(c)):
                    self.number()
                elif self.isAlpha(c):
                    self.identifier()
                else:
                    from lox import Lox
                    Lox.error(self.line, "Unexpected character.")
    
    def isAlpha(self, c: str) -> bool:
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c=='_')

    def identifier(self) -> None:
        while self.isAlphaNumeric(self.peek()): self.advance()
        text: str = self.source[self.start:self.current]
        type: TokenType = Scanner.keywords.get(text, TokenType.IDENTIFIER)
        self.addToken(type)
    
    def isAlphaNumeric(self, c: str) -> bool:
        return self.isAlpha(c) or self.isDigit(c)
    
    def isDigit(self, c: str) -> bool:
        return '0' <= c <= '9'

    def number(self) -> None:
        while (self.isDigit(self.peek())):
            self.advance()
        # look for fractional part
        if (self.peek() == '.' and self.isDigit(self.peekNext())):
            # consume the '.'
            self.advance()
            while(self.isDigit(self.peek())):
                self.advance()
        self.addToken(TokenType.NUMBER, 
                      float(self.source[self.start:self.current]))

    def peekNext(self):
        if (self.current+1) >= len(self.source): return '\0'
        return self.source[self.current + 1]
    

    def string(self) -> None:
        while self.peek() not in ('"', '\0'):
            if self.peek() == '\n': self.line += 1
            self.advance()
        if self.isAtEnd():
            from lox import Lox
            Lox.error(self.line, "Unterminated string.")
            return
        self.advance() # the closing "
        # trim surrounding quotes
        value: str = self.source[self.start+1:self.current-1]
        self.addToken(TokenType.STRING, value)

    def peek(self) -> str:
        if self.isAtEnd(): return '\0'
        return self.source[self.current]

    def scanTokens(self) -> list[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
