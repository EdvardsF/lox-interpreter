from enum import Enum


class TokenType(Enum):
    # Single character
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"

    # One or two characters
    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    # Literals
    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = "number"

    # Keywords
    ELSE = "else"
    CLASS = "class"
    IF = "if"
    PRINT = "print"
    FOR = "for"
    RETURN = "return"
    SUPER = "super"
    FUNCTION = "fun"
    AND = "and"
    VAR = "var"
    WHILE = "while"
    OR = "or"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"
    THIS = "this"
    
    EOF = None
    