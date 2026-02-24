from expr import *

class AstPrinter:
    def print(self, expr: Expr):
        return expr.accept(self)
    
    def visitBinaryExpr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme,
                                 expr.left, expr.right)

    def visitGroupingExpr(self, expr: Grouping):
        return self.parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: Literal):
        if expr.value == None: return "nil"
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs):
        builder: list[str] = []
        builder.append("(")
        builder.append(name)
        for expr in exprs:
            builder.append(expr.accept(self))
        builder.append(")")
        return ' '.join(builder)

    
if __name__ == "__main__":
    from token_ import Token
    from tokentype import TokenType
    expression = Binary(Unary(Token(TokenType.MINUS, "-", None, 1),Literal(123)), 
           Token(TokenType.STAR, "*", None, 1), 
           Grouping(Literal(45.67)))
    
    print(AstPrinter().print(expression))
