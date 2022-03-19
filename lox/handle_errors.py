import sys

from .errors import RuntimeException
from .lexer.token import Token
from .lexer.token_type import TokenType

_errors = {"errors": False, "runtime_errors": False}

def error(line: int, error_message: str):
    report(line, "", error_message)

def report(line: int, where: str, message: str):
    sys.stderr.write(f"[line {line}] Error{where}: {message}\n")
    _errors["errors"] = True

def runtime_error(runtime_exception: RuntimeException):
    sys.stderr.write(
        str(runtime_exception) + f"\n[line {runtime_exception.token.line}]\n"
    )
    _errors["runtime_errors"] = True

def parse_error(token: Token, message: str):
    _errors["errors"] = True
    if token.type == TokenType.EOF:
        report(token.line, "  at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)

def has_error():
    return _errors["errors"]

def has_runtime_error():
    return _errors["runtime_errors"]

def has_any_error():
    return any(_errors.values())

def update_error(runtime: bool, other_error: bool):
    _errors["errors"] = other_error
    _errors["runtime_errors"] = runtime