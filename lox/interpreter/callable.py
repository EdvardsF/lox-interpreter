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
    def __init__(self, declaration: Function_stmt, closure: "Environment", is_initializer: bool):
        self.declaration = declaration
        self.closure = closure
        self._is_initializer = is_initializer
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return Function(self.declaration, environment, self._is_initializer)
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        try:
            interpreter._execute_block(self.declaration.body, environment)
        except Return as e:
            if self._is_initializer:
                return self.closure.get(0, "this")
            return e.value
        if self._is_initializer:
            return self.closure.get_at(0, "this")
        return None
    
    @property
    def arity(self):
        return len(self.declaration.params)
    
    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"
    
    def __str__(self):
        return self.__repr__()

