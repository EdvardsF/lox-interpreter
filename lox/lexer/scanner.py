import typing as t

from .token import Token
from .token_type import TokenType
from ..handle_errors import report

class Scanner:
    def __init__(self, source: str):
        self._tokens = []
        self._source = source
        self._start = 0 # points to the start of the lexeme currently being scanned
        self._current = 0 # points to the character currently being cnsidered
        self._line = 1
    
    def scan_tokens(self):
        while not self._is_at_end():
            self._start = self._current # skips over any comments and whitespaces
            self._scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line, self._current, 0))
        return self._tokens
    
    def _scan_token(self):
        char = self._advance()
        add = self._add_token
        single_char_tokens = [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.LEFT_BRACE,
            TokenType.RIGHT_BRACE,
            TokenType.COMMA,
            TokenType.DOT,
            TokenType.MINUS,
            TokenType.PLUS,
            TokenType.SEMICOLON,
            TokenType.STAR,
        ]

        if char.isspace():
            if char == "\n":
                self._line += 1
        elif self._safe_to_token_type(char) in single_char_tokens:
            add(TokenType(char))
        elif char == "!":
            add(TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG_EQUAL)
        elif char == "=":
            add(TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL)
        elif char == ">":
            add(TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER)
        elif char == "<":
            add(TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS)
        elif char == "/":
            if self._match("/"):
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            else:
                add(TokenType.SLASH)
        elif char in ("\"", "'"):
            self._handle_string(char)
        elif char.isdigit():
            self._handle_number()
        elif char.isalnum() or char == "_":
            self._handle_identifier()
        else:
            line_str = self._source.splitlines()[self._line - 1]
            lines_len = len("".join(self._source.splitlines()[:self._line - 1]))
            position = self._current - (lines_len + self._line)
            report(self._line, line_str, position, f"Illegal character {char}.")
        
    def _handle_string(self, start_delimiter: str):
        while self._peek() != start_delimiter:
            if self._peek() == "\n":
                self._line += 1
            self._advance()
        
        # skip over " or '
        self._advance()

        # don't include the delimiters
        string = self._source[self._start + 1 : self._current - 1]
        self._add_token(TokenType.STRING, string)
    
    def _handle_number(self):
        while self._peek().isdigit():
            self._advance()
        # look for . and check if the next char is number
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        
        self._add_token(TokenType.NUMBER, float(self._source[self._start : self._current]))

    def _handle_identifier(self):
        keywords = [
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.IF,
            TokenType.ELSE,
            TokenType.FOR,
            TokenType.FUNCTION,
            TokenType.PRINT,
            TokenType.SUPER,
            TokenType.RETURN,
            TokenType.VAR,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.CLASS,
            TokenType.AND,
            TokenType.OR,
            TokenType.NIL,
            TokenType.THIS,
        ]

        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        
        value = self._source[self._start : self._current]
        type_ = TokenType.IDENTIFIER
        if self._safe_to_token_type(value) in keywords:
            type_ = TokenType(value)
        
        self._add_token(type_)

    def _add_token(self, t_type: TokenType, t_literal: t.Optional[t.Any] = None):
        lexeme = self._source[self._start : self._current]
        self._tokens.append(Token(t_type, lexeme, t_literal, self._line, self._start, len(lexeme)))

    @staticmethod
    def _safe_to_token_type(type: str):  # Doesn't raise ValueError returns `None` instead
        try:
            token = TokenType(type)
        except ValueError:
            return None
        return token
    
    def _match(self, expected: str):
        if self._is_at_end(): return False
        if self._source[self._current] != expected: return False

        self._current += 1
        return True

    def _advance(self):
        cur_char = self._source[self._current]
        self._current += 1
        return cur_char
    
    def _peek(self):
        if self._is_at_end(): return "\0"
        else: return self._source[self._current]
    
    def _peek_next(self):
        if self._current + 1 >= self._source: return "\0"
        else: return self._source[self._current + 1]
    
    def _is_at_end(self):
        return self._current >= len(self._source)
