import sys

from .errors import RuntimeException

errors = {"errors": False, "runtime_errors": False}

def report(line: int, line_str: str, position: int, message: str):
    global _errors
    errors["errors"] = True

    sys.stderr.write(f"\nError: {message}")
    sys.stderr.write(f"\n\n{line} | {line_str}\n")
    sys.stderr.write(" " * (len(str(line)) + 3) + " " * position + "^\n")

# TODO runtime_error should show whole line not single token
def runtime_error(runtime_exception: RuntimeException):
    global _errors
    errors["runtime_errors"] = True

    sys.stderr.write(f"\nRuntimeError: {runtime_exception.message}")
    sys.stderr.write(f"\n\n{runtime_exception.token.line} | {runtime_exception.token.lexeme}\n")
    sys.stderr.write(" " * (len(str(runtime_exception.token.lexeme)) + 3)  + "^\n")