from abc import ABC, abstractmethod

from expr import Expr
from token_ import Token

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor):
		pass

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

