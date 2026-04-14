from typing import Optional, TYPE_CHECKING

from interpreter import Interpreter
from loxcallable import LoxCallable

# Make type checker aware of class while avoiding circular imports
if TYPE_CHECKING:
    from loxfunction import LoxFunction

class LoxClass(LoxCallable):
    
    def __init__(self, name: str, methods: dict[str, "LoxFunction"]):
        self.name       = name
        self.methods    = methods
    
    def findMethod(self, name: str) -> Optional["LoxFunction"]:
        if name in self.methods.keys():
            return self.methods[name]

        return None
    
    def __str__(self):
        return self.name
    
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        from loxinstance import LoxInstance
        instance: LoxInstance = LoxInstance(self)
        initializer: Optional[LoxFunction] = self.findMethod("init")
        if initializer != None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer: Optional[LoxFunction] = self.findMethod("init")
        if initializer == None: return 0
        return initializer.arity()

