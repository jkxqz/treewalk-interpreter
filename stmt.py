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

class PrintStmt(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression
	def accept(self, visitor):
		return visitor.visitPrintStmt(self)

class VarStmt(Stmt):
	def __init__(self, name: Token, initializer: Optional[Expr] = None):
		self.name = name
		self.initializer = initializer
	def accept(self, visitor):
		return visitor.visitVarStmt(self)

