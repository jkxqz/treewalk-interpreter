from environment import Environment
from interpreter import Interpreter
from loxcallable import LoxCallable
from return_ import Return
from stmt import FunctionStmt

class LoxFunction(LoxCallable):

    def __init__(self, declaration: FunctionStmt, closure: Environment):
        self.declaration: FunctionStmt = declaration
        self.closure: Environment = closure
    
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as returnValue:
            return returnValue.value

    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
    
