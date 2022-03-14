import typing as t

from .token_type import TokenType

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: t.Any, line: int, offset: int, length: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.offset = offset
        self.length = length

    def __str__(self):
        return f"Token(type={self.type}, lexeme={self.lexeme} literal={self.literal}, line={self.line}, offset={self.offset}, length={self.length})"