from tokentype import TokenType
from token_ import Token
from expr import *
from typing import Optional
from lox import Lox

class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens : list[Token] = tokens
        self.current: int = 0
    

    class ParseError(RuntimeError):
        pass

        
    def parse(self) -> Optional[Expr]:
        try:
            return self.expression()
        except self.ParseError:
            return None



    def expression(self) -> Expr:
        return self.equality()
    

    def equality(self) -> Expr:
        expr: Expr = self.comparison()

        while (self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr: Expr = Binary(expr, operator, right)
        return expr
    

    def comparison(self) -> Expr:
        expr: Expr = self.term()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                           TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr: Expr = Binary(expr, operator, right)
        
        return expr
    

    def term(self) -> Expr:
        expr: Expr = self.factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr: Expr = Binary(expr, operator, right)

        return expr


    def factor(self) -> Expr:
        expr: Expr = self.unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr: Expr = Binary(expr, operator, right) 

        return expr
    

    def unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)
        
        return self.primary()
    

    def primary(self) -> Expr:
        if self._match(TokenType.FALSE): return Literal(False)
        if self._match(TokenType.TRUE): return Literal(True)
        if self._match(TokenType.NIL): return Literal(None)
        if self._match(TokenType.NUMBER, TokenType.STRING): 
            return Literal(self.previous().literal)
        if self._match(TokenType.LEFT_PAREN): 
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression.")
    

    def consume(self, _type: TokenType, message: str) -> Token:
        if self.check(_type): return self.advance()
        raise self.error(self.peek(), message)
        
    
    def error(self, token: Token, message: str) -> ParseError:
        Lox.error1(token, message)
        return Parser.ParseError("Parser Error")
    

    def synchronize(self) -> None:
        self.advance()

        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON: return

            match(self.peek().type):
                case (TokenType.CLASS | TokenType.FUN | 
                      TokenType.VAR | TokenType.FOR |
                    TokenType.IF | TokenType.WHILE | 
                    TokenType.PRINT | TokenType.RETURN):
                    return

            self.advance()


    def _match(self, *types: TokenType) -> bool:
        for _type in types:
            if (self.check(_type)):
                self.advance()
                return True
        
        return False
    

    def check(self, _type: TokenType) -> bool:
        if self.isAtEnd(): return False
        return self.peek().type == _type
    

    def advance(self) -> Token:
        if not self.isAtEnd(): self.current += 1
        return self.previous()
    

    def isAtEnd(self) -> bool:
        return self.peek().type == TokenType.EOF


    def peek(self) -> Token:
        return self.tokens[self.current]
    

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    


