from tokentype import TokenType

class Token:
    def __init__(self, type: TokenType, lexeme: str, 
                 literal: object, line: int):
        self.type       = type
        self.lexeme     = lexeme
        self.literal    = literal
        self.line       = line
    
    def __str__(self):
        return str(self.type.name) + " " + repr(self.lexeme) + " " + str(self.literal)