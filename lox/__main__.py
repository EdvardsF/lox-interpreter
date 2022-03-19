import typing as t
import sys
from pathlib import Path

from .lexer.scanner import Scanner
from .parser.parser import Parser
from .interpreter.interpreter import Interpreter
from .interpreter.resolver import Resolver
from .handle_errors import has_any_error, update_error, has_error, has_runtime_error

interpreter = Interpreter()

def run(code):
    scanner = Scanner(code)
    tokens = scanner.scan_tokens()
    if has_error(): exit(65)

    # TODO remove code parameter
    parser = Parser(tokens, code)
    statements = parser.parse()
    if has_error(): exit(65)

    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    if has_error(): exit(65)

    interpreter.interpret(statements)
    if has_runtime_error(): exit(70)


def runFile(path: str):
    try:
        code = Path(path).read_text()
    except FileNotFoundError:
        print(f"File '{path}' doesn't exist.")
        exit(1)
    
    run(code)

def runPrompt():
    while True:
        try:
            line = input("> ")
            run(line)
            update_error(False, False)

        except EOFError:
            print("\nExiting")
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            break

def main(args: t.Optional[t.List[str]] = None):
    args = sys.argv
    if len(args) > 2:
        print("Usage: pylox [script]")
    elif len(args) == 2:
        runFile(args[1])
    else:
        runPrompt()

if __name__ == "__main__":
    main()
