import typing as t
import time

from .callable import Callable


class Clock(Callable):
    @property
    def arity(self):
        return 0
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        return time.time()
    
    def __repr__(self):
        return "<native function>"


class Input(Callable):
    @property
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        return input(arguments[0])

    def __repr__(self):
        return "<native function>"


class String(Callable):
    @property
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        return str(arguments[0])

    def __repr__(self):
        return "<native function>"
    

class Number(Callable):
    @property
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        return float(arguments[0])

    def __repr__(self):
        return "<native function>"


class Type(Callable):
    @property
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        obj = arguments[0]
        if isinstance(obj, float) or isinstance(obj, int):
            return "number"
        elif isinstance(obj, bool):
            return "boolean"
        elif isinstance(obj, str):
            return "string"
        else:
            return "nil"

    def __repr__(self):
        return "<native function>" 


class Len(Callable):
    @property
    def arity(self):
        return 1
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        return len(arguments[0])

    def __repr__(self):
        return "<native function>"