import typing as t

from ..errors import RuntimeException
from ..lexer.token import Token
from .callable import Callable, Function


class Instance:
    def __init__(self, lox_class):
        self.lox_class = lox_class
        self._fields = {}
    
    def get(self, name: Token):
        if name.lexeme in self._fields.keys():
            return self._fields[name.lexeme]
        
        method = self.lox_class.find_method(name.lexeme)
        if method: return method.bind(self)
        raise RuntimeException(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: t.Any):
        self._fields[name.lexeme] = value
    
    def __str__(self):
        return f"<instance of {self.lox_class.name}>"


class Class(Callable):
    def __init__(self, name: str, superclass: "Class", methods: t.Dict[str, Function]):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def find_method(self, name: str):
        if name in self.methods.keys():
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None
    
    def call(self, interpreter, arguments: t.List[t.Any]):
        instance = Instance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    @property
    def arity(self):
        initializer = self.find_method("init")
        if initializer is None: return 0
        return initializer.arity
    
    def __str__(self):
        return self.name