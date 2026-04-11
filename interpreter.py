from time import time
from typing import cast

from environment import Environment
from expr import *
#from loxcallable import LoxCallable
#from loxfunction import LoxFunction
from loxruntimeerror import LoxRuntimeError
from return_ import Return
from stmt import *
from tokentype import TokenType
from token_ import Token

class Interpreter:

    _globals: Environment = Environment()
    _locals: dict[Expr, int] = {}

    environment: Environment = _globals

    def __init__(self):
        from loxcallable import LoxCallable
        self._globals.define("clock", 
            type("", (LoxCallable,), 
                { "arity"   : lambda self: 0,
                  "call"    : lambda self, interpreter, arguments: time(),
                  "__str__" : lambda self: "<native fn>"
                })()
            )

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            from lox import Lox
            Lox.runtimeError(error)
    
    def stringify(self, obj: object) -> str:
        if obj == None: return "nil"

        if isinstance(obj, bool):
            if obj:
                return "true"
            else:
                return "false"
    
        if isinstance(obj, float):
            text: str = str(obj)
            if text.endswith(".0"):
                text = text[0:len(text)-2]
            return text

        return str(obj)

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)
    
    def execute(self, stmt: Optional[Stmt]) -> None:
        if isinstance(stmt, Stmt): stmt.accept(self)
        # fallthrough and do nothing if parser returned None instead of legal statement
    
    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def visitLiteralExpr(self, expr: Literal) -> object:
        return expr.value
    
    def visitGroupingExpr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def visitUnaryExpr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.isTruthy(right)
            case TokenType.MINUS:
                operand = self.checkNumberOperand(expr.operator, right)
                return -float(operand)
        
    def visitBinaryExpr(self, expr: Binary) -> object:
        left: object = self.evaluate(expr.left)
        right: object = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left - right
            case TokenType.SLASH:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left * right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            case TokenType.GREATER:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                left, right = self.checkNumberOperands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
        return
    
    def visitAssignExpr(self, expr: Assign) -> object:
        value: object = self.evaluate(expr.value)

        distance: Optional[int] = self._locals.get(expr)
        if distance != None:
            self.environment.assignAt(distance, expr.name, value)
        else:
            self._globals.assign(expr.name, value)

        return value

    def isTruthy(self, obj: object) -> bool:
        if obj == None: return False
        if isinstance(obj, bool): return bool(obj)
        return True
    
    def checkNumberOperand(self, operator: Token, operand: object) -> float:
        if isinstance(operand, float):
            return operand
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def checkNumberOperands(self, operator: Token, left: object, right: object) -> list[float]:
        if isinstance(left, float) and isinstance(right, float):
            return [left, right]
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def visitExpressionStmt(self, stmt: ExpressionStmt) -> None:
        self.evaluate(stmt.expression)

    def visitPrintStmt(self, stmt: PrintStmt) -> None:
        value: object = self.evaluate(stmt.expression)
        print(self.stringify(value))
    
    def visitVarStmt(self, stmt: VarStmt) -> None:
        value: object = None
        if (stmt.initializer != None):
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)
    
    def visitBlockStmt(self, stmt: BlockStmt) -> None:
        self.executeBlock(stmt.statements, Environment(self.environment))
    
    def executeBlock(self, statements: list[Optional[Stmt]], environment: Environment) -> None:
        previous: Optional[Environment] = self.environment

        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
        
    def visitIfStmt(self, stmt: IfStmt) -> None:
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)
    
    def visitVariableExpr(self, expr: Variable) -> object:
        return self.lookUpVariable(expr.name, expr)
    
    def lookUpVariable(self, name: Token, expr: Expr) -> object:
        distance: Optional[int] = self._locals.get(expr)
        if distance != None:
            return self.environment.getAt(distance, name.lexeme)
        else:
            return self._globals.get(name)

    def visitLogicalExpr(self, expr: Logical) -> object:
        left: object = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left): return left
        else:
            if not self.isTruthy(left): return left
        
        return self.evaluate(expr.right)
    
    def visitWhileStmt(self, stmt: WhileStmt) -> None:
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        
    def visitCallExpr(self, expr) -> object:
        callee: object = self.evaluate(expr.callee)

        arguments: list[object] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        from loxcallable import LoxCallable
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = callee

        if len(arguments) != function.arity():
            raise LoxRuntimeError(expr.paren, 
                f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)
    
    def visitFunctionStmt(self, stmt: FunctionStmt) -> None:
        from loxfunction import LoxFunction
        function: LoxFunction = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
    
    def visitReturnStmt(self, stmt: ReturnStmt) -> None:
        value: object = None
        if (stmt.value != None): value = self.evaluate(stmt.value)

        raise Return(value)
        