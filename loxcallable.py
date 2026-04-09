from abc import ABC, abstractmethod

from interpreter import Interpreter

class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        pass 
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        pass