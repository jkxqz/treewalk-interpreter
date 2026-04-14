from typing import Optional

from expr import *
from lox import Lox
from stmt import *
from tokentype import TokenType
from token_ import Token

class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens : list[Token] = tokens
        self.current: int = 0
    
    class ParseError(RuntimeError):
        pass
        
    def parse(self) -> list[Optional[Stmt]]:
        statements: list[Optional[Stmt]] = []
        while not self.isAtEnd():
            statements.append(self.declaration())
        
        return statements
    
    def declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TokenType.CLASS): return self.classDeclaration()
            if self._match(TokenType.FUN): return self.function("function")
            if self._match(TokenType.VAR): return self.varDeclaration()
            return self.statement()
        except self.ParseError:
            self.synchronize()
            return None
    
    def classDeclaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: list[FunctionStmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            methods.append(self.function("method"))
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassStmt(name, methods)
    
    def function(self, kind: str) -> FunctionStmt:
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self._match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: list[Optional[Stmt]] = self.block()
        return FunctionStmt(name, parameters, body)
    

    def varDeclaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer: Optional[Expr] = None
        if self._match(TokenType.EQUAL): initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return VarStmt(name, initializer)


    def statement(self) -> Stmt:
        if self._match(TokenType.FOR): return self.forStatement()
        if self._match(TokenType.IF): return self.ifStatement() 
        if self._match(TokenType.PRINT): return self.printStatement()
        if self._match(TokenType.WHILE): return self.whileStatement()
        if self._match(TokenType.LEFT_BRACE): return BlockStmt(self.block())
        if self._match(TokenType.RETURN): return self.returnStatement()

        return self.expressionStatement()
    
    def forStatement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Optional[Stmt] = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()
        
        condition: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: Optional[Expr] = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: Stmt = self.statement()

        if increment:
            body = BlockStmt([body, ExpressionStmt(increment)])
        
        if condition == None: condition = Literal(True)
        body = WhileStmt(condition, body)

        if initializer:
            body = BlockStmt([initializer, body])

        return body
    
    def ifStatement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        thenBranch: Stmt = self.statement()
        elseBranch: Optional[Stmt] = None
        if self._match(TokenType.ELSE): elseBranch = self.statement()

        return IfStmt(condition, thenBranch, elseBranch)

    
    def printStatement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)
    
    def whileStatement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        body: Stmt = self.statement()

        return WhileStmt(condition, body)
    
    def block(self) -> list[Optional[Stmt]]:
        statements: list[Optional[Stmt]] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def returnStatement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmt(keyword, value)

    def expressionStatement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def expression(self) -> Expr:
        return self.assignment()
    
    def assignment(self) -> Expr:
        expr: Expr = self._or()

        if self._match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()
        
            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def _or(self) -> Expr:
        expr: Expr = self._and()

        while self._match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self._and()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def _and(self) -> Expr:
        expr: Expr = self.equality()

        while self._match(TokenType.AND):
            operator: Token = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr
    
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
        
        return self.call()
    
    def call(self) -> Expr:
        expr: Expr = self.primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self._match(TokenType.DOT):
                name: Token = self.consume(TokenType.IDENTIFIER, 
                                           "Expect property name after '.'.")
                expr = Get(expr, name)
            else: 
                break
        
        return expr
    
    def finishCall(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self._match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
        
        paren: Token = self.consume(TokenType.RIGHT_PAREN, 
                                    "Expect ')' after arguments.")
        
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        if self._match(TokenType.FALSE): return Literal(False)
        if self._match(TokenType.TRUE): return Literal(True)
        if self._match(TokenType.NIL): return Literal(None)
        if self._match(TokenType.NUMBER, TokenType.STRING): 
            return Literal(self.previous().literal)
        if self._match(TokenType.IDENTIFIER): return Variable(self.previous())
        if self._match(TokenType.THIS): return This(self.previous())
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


