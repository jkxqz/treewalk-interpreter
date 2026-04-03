from expr import *
from tokentype import TokenType
from token_ import Token
from loxruntimeerror import LoxRuntimeError

class Interpreter:

    def interpret(self, expression: Expr) -> None:
        try:
            value: object = self.evaluate(expression)
            print(self.stringify(value))
        except LoxRuntimeError as error:
            from lox import Lox
            Lox.runtimeError(error)
    
    def stringify(self, obj: object) -> str:
        if obj == None: return "nil"

        if isinstance(obj, float):
            text: str = str(obj)
            if text.endswith(".0"):
                text = text[0:len(text)-2]
            return text

        return str(obj)

    def evaluate(self, expr: Expr) -> object:
        return expr.accept(self)

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


        
        