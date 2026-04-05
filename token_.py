from tokentype import TokenType

class Token:

    def __init__(self, type: TokenType, lexeme: str, 
                 literal: object, line: int):
        self.type   : TokenType = type
        self.lexeme : str = lexeme
        self.literal: object = literal
        self.line   : int = line
    
    def __str__(self):
        return str(self.type.name) + " " + repr(self.lexeme) + " " + str(self.literal)