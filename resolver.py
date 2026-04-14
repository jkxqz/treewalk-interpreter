from enum import Enum, auto

from expr import *
from interpreter import Interpreter
from stmt import *
from token_ import Token

class FunctionType(Enum):
    NONE        = auto()
    FUNCTION    = auto()
    INITIALIZER = auto()
    METHOD      = auto()

class ClassType(Enum):
    NONE        = auto()
    CLASS       = auto()

class Resolver:

    def __init__(self, interpreter: Interpreter):
        self.interpreter: Interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.currentFunction: FunctionType = FunctionType.NONE
        self.currentClass: ClassType = ClassType.NONE
    
    def visitBlockStmt(self, stmt: BlockStmt) -> None:
        self.beginScope()
        self.resolveList(stmt.statements)
        self.endScope()
    
    def visitClassStmt(self, stmt: ClassStmt) -> None:
        enclosingClass: ClassType = self.currentClass
        self.currentClass = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        self.beginScope()
        self.scopes[-1]["this"] = True
        
        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolveFunction(method, declaration)
        
        self.endScope()

        self.currentClass = enclosingClass
    
    def visitExpressionStmt(self, stmt: ExpressionStmt) -> None:
        self.resolveExpr(stmt.expression)
    
    def visitFunctionStmt(self, stmt: FunctionStmt) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, FunctionType.FUNCTION)
    
    def visitIfStmt(self, stmt: IfStmt) -> None:
        self.resolveExpr(stmt.condition)
        self.resolveStmt(stmt.thenBranch)
        if stmt.elseBranch != None: self.resolveStmt(stmt.elseBranch)

    def visitPrintStmt(self, stmt: PrintStmt) -> None:
        self.resolveExpr(stmt.expression)
    
    def visitReturnStmt(self, stmt: ReturnStmt) -> None:
        if self.currentFunction == FunctionType.NONE:
            from lox import Lox
            Lox.error1(stmt.keyword, "Can't return from top-level code.")
        if stmt.value != None:
            if self.currentFunction == FunctionType.INITIALIZER:
                Lox.error1(stmt.keyword, "Can't return a value from an initializer.")
            self.resolveExpr(stmt.value)
    
    def visitVarStmt(self, stmt: VarStmt) -> None:
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolveExpr(stmt.initializer)
        
        self.define(stmt.name)
    
    def visitWhileStmt(self, stmt: WhileStmt) -> None:
        self.resolveExpr(stmt.condition)
        self.resolveStmt(stmt.body)
    
    def visitAssignExpr(self, expr: Assign) -> None:
        self.resolveExpr(expr.value)
        self.resolveLocal(expr, expr.name)
    
    def visitBinaryExpr(self, expr: Binary) -> None:
        self.resolveExpr(expr.left)
        self.resolveExpr(expr.right)
    
    def visitCallExpr(self, expr: Call) -> None:
        self.resolveExpr(expr.callee)

        for argument in expr.arguments:
            self.resolveExpr(argument)
    
    def visitGetExpr(self, expr: Get)-> None:
        self.resolveExpr(expr.obj)
    
    def visitGroupingExpr(self, expr: Grouping) -> None:
        self.resolveExpr(expr.expression)
    
    def visitLiteralExpr(self, expr: Literal) -> None:
        return None
    
    def visitLogicalExpr(self, expr: Logical) -> None:
        self.resolveExpr(expr.left)
        self.resolveExpr(expr.right)
    
    def visitSetExpr(self, expr: Set) -> None:
        self.resolveExpr(expr.value)
        self.resolveExpr(expr.obj)
    
    def visitThisExpr(self, expr: This) -> None:
        from lox import Lox
        if self.currentClass == ClassType.NONE:
            Lox.error1(expr.keyword, "Can't use 'this' outside of a class.")
            return None
        self.resolveLocal(expr, expr.keyword)

    def visitUnaryExpr(self, expr: Unary) -> None:
        self.resolveExpr(expr.right)
    
    def visitVariableExpr(self, expr: Variable) -> None:
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) == False:
            from lox import Lox
            Lox.error1(expr.name, "Can't read local variable in its own initializer.")

        self.resolveLocal(expr, expr.name)
    
    def resolveList(self, statements: list[Optional[Stmt]]) -> None:
        for statement in statements:
            self.resolveStmt(statement)
    
    def resolveStmt(self, stmt: Optional[Stmt]) -> None:
        if isinstance(stmt, Stmt): stmt.accept(self)

    
    def resolveExpr(self, expr: Expr) -> None:
        expr.accept(self)
    
    def resolveFunction(self, function: FunctionStmt, _type: FunctionType) -> None:
        enclosingFunction: FunctionType = self.currentFunction
        self.currentFunction = _type

        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolveList(function.body)
        self.endScope()
        self.currentFunction = enclosingFunction
    
    def beginScope(self) -> None:
        self.scopes.append({})
    
    def endScope(self) -> None:
        self.scopes.pop()
    
    def declare(self, name: Token) -> None:
        if not self.scopes: return

        scope: dict[str, bool] = self.scopes[-1]
        if name.lexeme in scope.keys():
            from lox import Lox
            Lox.error1(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False
    
    def define(self, name: Token) -> None:
        if not self.scopes: return
        self.scopes[-1][name.lexeme] = True

    def resolveLocal(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.scopes)-1, -1, -1):
            if name.lexeme in self.scopes[i].keys():
                self.interpreter.resolve(expr, len(self.scopes)-1-i)
                return

