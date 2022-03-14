import typing as t

from ..helpers import get_line_given_pos
from ..handle_errors import report
from ..errors import ParseError
from ..lexer.token import Token, TokenType
from .expr import *
from .stmt import *


class Parser:
    def __init__(self, tokens: t.List[Token], source: str):
        self._tokens = tokens
        self._source = source
        self._current = 0
    
    def parse(self):
        statements = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return statements
    
    def _declaration(self):
        try:
            if self._match(TokenType.VAR): return self._var_declaration()
            return self._statement()
        except ParseError as e:
            self._synchronize()
            return None
    
    def _var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after a vaariable decleration.")
        return Var_stmt(name, initializer)
    
    def _statement(self):
        if self._match(TokenType.IF):
            return self._if_statement()
        elif self._match(TokenType.PRINT):
            return self._print_statement()
        elif self._match(TokenType.WHILE):
            return self._while_statement()
        elif self._match(TokenType.LEFT_PAREN):
            return Block_stmt(self._block())
        else:
            return self._expression_statement()
    
    def _if_statement(self):
        self._consume(TokenType.LEFT_BRACE, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_BRACE, "Expect ')' after if condition.")

        then_branch = self._statement()
        else_branch = None

        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        
        return If_stmt(condition, then_branch, else_branch)
    
    def _print_statement(self):
        value = self._expression()
        # TODO in case of  if (a==2) print 2 else print nil; print the carret in the correct position
        self._consume(TokenType.SEMICOLON, "Expect ';' after a value.")
        return Print_stmt(value)
    
    def _while_statement(self):
        self._consume(TokenType.LEFT_BRACE, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_BRACE, "Expect ')' after condition.")
        body = self._statement()

        return While_stmt(condition, body)
    
    def _block(self):
        statements = []

        while not self._check(TokenType.RIGHT_PAREN) and not self._is_at_end():
            statements.append(self._declaration())
        
        self._consume(TokenType.RIGHT_PAREN, "Expect '}' after block.")
        return statements
    
    def _expression_statement(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression_stmt(expr)
    
    def _expression(self):
        return self._assignment()
    
    def _assignment(self):
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable_expr):
                name = expr.name
                return Assign_expr(name, value)
            
            self._error(equals, "Invalid assignment target.", 0)

        return expr
    
    def _or(self):
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = Logical_expr(expr, operator, right) 

        return expr

    def _and(self):
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = Logical_expr(expr, operator, right)

        return expr 

    def _equality(self):
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary_expr(expr, operator, right)
        
        return expr
    
    def _comparison(self):
        expr = self._term()

        while(self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL)):
            operator = self._previous()
            right = self._term()
            expr = Binary_expr(expr, operator, right)
        
        return expr
    
    def _term(self):
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary_expr(expr, operator, right)
        
        return expr
    
    def _factor(self):
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous()
            right = self._unary()
            expr = Binary_expr(expr, operator, right)
        
        return expr
    
    def _unary(self):
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary_expr(operator, right)
        
        return self._primary()
    
    def _primary(self):
        if self._match(TokenType.FALSE): return Literal_expr(False)
        if self._match(TokenType.TRUE): return Literal_expr(True)
        if self._match(TokenType.NIL): return Literal_expr(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal_expr(self._previous().literal)
        
        if self._match(TokenType.IDENTIFIER):
            return Variable_expr(self._previous())
        
        if self._match(TokenType.LEFT_BRACE):
            expr = self._expression()
            self._consume(TokenType.RIGHT_BRACE, "Expect ')' after expression.")
            return Grouping_expr(expr)
        
        raise self._error(self._peek(), "Expect expression.")
        
    def _consume(self, token_type: TokenType, message: str):
        if self._check(token_type): return self._advance()
        raise self._error(self._peek(), message)

    def _error(self, token: Token, message, error_pos: t.Optional[int] = -1):
        line_str = get_line_given_pos(self._source, token.offset)
        if error_pos == -1: error_pos = len(line_str)
        report(token.line, line_str, error_pos, message)
        return ParseError()
        
    def _match(self, *args: TokenType):
        for token_type in args:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType):
        if self._is_at_end(): return False
        return self._peek().type == token_type
    
    def _advance(self):
        if not self._is_at_end(): self._current += 1
        return self._previous()
    
    def _is_at_end(self):
        return self._peek().type == TokenType.EOF
    
    def _peek(self):
        return self._tokens[self._current]
    
    def _previous(self):
        return self._tokens[self._current - 1]
    
    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in (
                TokenType.CLASS,
                TokenType.FUNCTION,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN
            ):
                return
            
            self._advance()

    