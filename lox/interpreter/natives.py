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
    