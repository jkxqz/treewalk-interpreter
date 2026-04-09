from abc import ABC, abstractmethod
from typing import Optional

from expr import Expr
from token_ import Token

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor):
		pass

class BlockStmt(Stmt):
	def __init__(self, statements: list[Optional[Stmt]]):
		self.statements = statements
	def accept(self, visitor):
		return visitor.visitBlockStmt(self)

class ExpressionStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression
	def accept(self, visitor):
		return visitor.visitExpressionStmt(self)

class FunctionStmt(Stmt):
	def __init__(self, name: Token, params: list[Token], body: list[Optional[Stmt]]):
		self.name = name
		self.params = params
		self.body = body
	def accept(self, visitor):
		return visitor.visitFunctionStmt(self)

class IfStmt(Stmt):
	def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Optional[Stmt] = None):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch
	def accept(self, visitor):
		return visitor.visitIfStmt(self)

class PrintStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression
	def accept(self, visitor):
		return visitor.visitPrintStmt(self)

class ReturnStmt(Stmt):
	def __init__(self, keyword: Token, value: Optional[Expr]):
		self.keyword = keyword
		self.value = value
	def accept(self, visitor):
		return visitor.visitReturnStmt(self)

class VarStmt(Stmt):
	def __init__(self, name: Token, initializer: Optional[Expr] = None):
		self.name = name
		self.initializer = initializer
	def accept(self, visitor):
		return visitor.visitVarStmt(self)

class WhileStmt(Stmt):
	def __init__(self, condition: Expr, body: Stmt):
		self.condition = condition
		self.body = body
	def accept(self, visitor):
		return visitor.visitWhileStmt(self)

