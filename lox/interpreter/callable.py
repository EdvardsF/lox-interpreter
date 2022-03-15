import typing as t
from abc import ABC, abstractmethod

from .environment import Environment
from ..parser.stmt import *
from ..errors import Return

class Callable(ABC):
    @abstractmethod
    def call(interpreter, arguments: t.List[t.Any]):
        pass
    
    @abstractmethod
    def arity():
        pass

class Function(Callable):
    def __init__(self, declaration: Function_stmt, closure: "Environment"):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        try:
            interpreter._execute_block(self.declaration.body, environment)
        except Return as e:
            return e.value
        return None
    
    @property
    def arity(self):
        return len(self.declaration.params)
    
    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"
    
    def __str__(self):
        return self.__repr__()

