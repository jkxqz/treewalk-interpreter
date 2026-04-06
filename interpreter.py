from typing import cast

from environment import Environment
from expr import *
from loxruntimeerror import LoxRuntimeError
from stmt import *
from tokentype import TokenType
from token_ import Token

class Interpreter:

    environment: Environment = Environment()

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
        self.environment.assign(expr.name, value)
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
        if (stmt.initializer):
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
        elif stmt.elseBranch:
            self.execute(stmt.elseBranch)
    
    def visitVariableExpr(self, expr: Variable) -> object:
        return self.environment.get(expr.name)

        
        