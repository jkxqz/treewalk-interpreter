from typing import Optional

from loxclass import LoxClass
from loxruntimeerror import LoxRuntimeError
from token_ import Token


class LoxInstance:
    
    def __init__(self, klass: LoxClass):
        self.klass: LoxClass            = klass
        self.fields:dict[str, object]   = {}
    
    def get(self, name: Token) -> object:
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]
        
        from loxfunction import LoxFunction
        method: Optional[LoxFunction] = self.klass.findMethod(name.lexeme)
        if method != None: return method.bind(self)
        
        raise LoxRuntimeError(name, 
                              f"Undefined property {name.lexeme}.")
    
    def set(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value
    
    def __str__(self):
        return self.klass.name + " instance"
