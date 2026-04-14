from environment import Environment
from interpreter import Interpreter
from loxcallable import LoxCallable
from loxinstance import LoxInstance
from return_ import Return
from stmt import FunctionStmt

type LF = LoxFunction

class LoxFunction(LoxCallable):

    def __init__(self, declaration: FunctionStmt, closure: Environment,
                 isInitializer: bool):
        self.declaration: FunctionStmt = declaration
        self.closure: Environment = closure
        self.isInitializer: bool = isInitializer
    
    def bind(self, instance: LoxInstance) -> LF:
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        cls = type(self)
        return cls(self.declaration, environment, self.isInitializer)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as returnValue:
            if self.isInitializer: return self.closure.getAt(0, "this")
            return returnValue.value
        
        if self.isInitializer: return self.closure.getAt(0, "this")

    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
    
