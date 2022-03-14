import typing as t

from loxscript.errors import RuntimeException
from ..lexer.token import Token


class Environment:
    def __init__(self, enclosing: t.Optional["Environment"] = None):
        self._enclosing = enclosing
        self._variables = {}

    def define(self, name: str, value: t.Any):
        self._variables[name] = value
    
    def assign(self, name: "Token", value: t.Any):
        if name.lexeme in self._variables:
            self._variables[name] = value
            return
        
        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return
        
        raise RuntimeException(name, f"Undefined variable'{name.lexeme}'.")
    
    def get(self, name: "Token"):
        if name.lexeme in self._variables:
            return self._variables[name.lexeme]
        elif self._enclosing is not None:
            return self._enclosing.get(name)
        else:
            raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")