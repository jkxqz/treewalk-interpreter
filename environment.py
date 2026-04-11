from typing import Optional

from loxruntimeerror import LoxRuntimeError
from token_ import Token

type Env = Environment 

class Environment:

    def __init__(self, enclosing: Optional[Env] = None):
        self.values: dict[str, object] = {}
        self.enclosing: Optional[Env] = enclosing

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return 
        
        raise LoxRuntimeError(name,
                              f"Undefined variable {name.lexeme}.")

    def get(self, name: Token) -> object:
        if name.lexeme in self.values.keys(): 
            return self.values.get(name.lexeme)

        if self.enclosing: return self.enclosing.get(name) 

        raise LoxRuntimeError(name,
                              f"Undefined variable {name.lexeme}.")

    def define(self, name: str, value: object) -> None:
        self.values[name] = value
    
    def ancestor(self, distance: int) -> Env:
        environment: Env = self
        for i in range(distance):
            environment = environment.enclosing
        
        return environment
    
    def getAt(self, distance: int, name: str) -> object:
        return self.ancestor(distance).values.get(name)
    
    def assignAt(self, distance: int, name: Token, value: object) -> None:
        self.ancestor(distance).values[name.lexeme] = value
