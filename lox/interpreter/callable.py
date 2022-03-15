import typing as t
from abc import ABC, abstractmethod

from .environment import Environment
from ..parser.stmt import *

class Callable(ABC):
    @abstractmethod
    def call(interpreter, arguments: t.List[t.Any]):
        pass
    
    @abstractmethod
    def arity():
        pass

class Function(Callable):
    def __init__(self, declaration: Function_stmt):
        self.declaration = declaration
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        environment = Environment(interpreter.globals)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        interpreter._execute_block(self.declaration.body, environment)
        return None
    
    def arity(self):
        return len(self.declaration.params)
    
    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"
    
    def __str__(self):
        return self.__repr__()

