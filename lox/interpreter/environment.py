import typing as t

from ..errors import RuntimeException
from ..lexer.token import Token


class Environment:
    def __init__(self, enclosing: t.Optional["Environment"] = None):
        self._enclosing = enclosing
        self._variables = {}

    def define(self, name: str, value: t.Any):
        self._variables[name] = value
    
    def get_at(self, distance: int, name: str):
        return self._ancestor(distance)._variables.get(name)
    
    def assign_at(self, distance: int, name: Token, value: t.Any):
        self._ancestor(distance)._variables[name.lexeme] = value

    def _ancestor(self, distance):
        environment = self
        for i in range(distance):
            environment = environment._enclosing
        return environment

    def assign(self, name: "Token", value: t.Any):
        print(value)
        print(name)
        print(self._variables)
        if name.lexeme in self._variables:
            self._variables[name.lexeme] = value
            return
        
        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return
        
        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")
    
    def get(self, name: "Token"):
        if name.lexeme in self._variables:
            return self._variables[name.lexeme]
        elif self._enclosing is not None:
            return self._enclosing.get(name)
        else:
            raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")