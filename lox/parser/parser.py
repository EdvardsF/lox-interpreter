import typing as t

from ..handle_errors import parse_error
from ..errors import ParseError
from ..lexer.token import Token, TokenType
from .expr import *
from .stmt import *


class Parser:
    def __init__(self, tokens: t.List[Token]):
        self._tokens = tokens
        self._current = 0
    
    def parse(self):
        statements = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return statements
    
    def _declaration(self):
        try:
            if self._match(TokenType.CLASS): return self._class_declaration()
            elif self._match(TokenType.FUNCTION): return self._function("function")
            elif self._match(TokenType.VAR): return self._var_declaration()
            return self._statement()
        except ParseError as e:
            self._synchronize()
            return None
        
    def _class_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        superclass = None
        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable_expr(self._previous())

        self._consume(TokenType.LEFT_PAREN, "Expect '{' before class body.")

        methods = []
        while not self._check(TokenType.RIGHT_PAREN) and not self._is_at_end():
            methods.append(self._function("method"))
        
        self._consume(TokenType.RIGHT_PAREN, "Expect '}' after class body.")
        return Class_stmt(name, superclass, methods)
        
    def _function(self, kind: str):
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        parameters = []
        self._consume(TokenType.LEFT_BRACE, f"Expect '(' after {kind} name.")
        if not self._check(TokenType.RIGHT_BRACE):
            parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self._match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))
        self._consume(TokenType.RIGHT_BRACE, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '{{' before {kind} body.")
        # self._block assumes '{' is already consumed
        statements = self._block()
        return Function_stmt(name, parameters, statements)
    
    def _var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after a variable decleration.")
        return Var_stmt(name, initializer)
    
    def _statement(self):
        if self._match(TokenType.FOR):
            return self._for_statement()
        elif self._match(TokenType.IF):
            return self._if_statement()
        elif self._match(TokenType.PRINT):
            return self._print_statement()
        elif self._match(TokenType.RETURN):
            return self._return_statement()
        elif self._match(TokenType.WHILE):
            return self._while_statement()
        elif self._match(TokenType.LEFT_PAREN):
            return Block_stmt(self._block())
        else:
            return self._expression_statement()
    
    def _for_statement(self):
        self._consume(TokenType.LEFT_BRACE, "Expect '(' after 'for'.")

        initializer = None
        if self._match(TokenType.SEMICOLON):
            pass
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()
        
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self._check(TokenType.RIGHT_BRACE):
            increment = self._expression()
        self._consume(TokenType.RIGHT_BRACE, "Expect ')' after for clauses.")

        body = self._statement()

        if increment is not None:
            body = Block_stmt([
                body,
                Expression_stmt(increment)
            ])
        
        if condition is None:
            condition = Literal_expr(True)
        
        body = While_stmt(condition, body)

        if initializer is not None:
            body = Block_stmt([initializer, body])
        
        return body
    
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
        self._consume(TokenType.SEMICOLON, "Expect ';' after a value.")
        return Print_stmt(value)
    
    def _return_statement(self):
        keyword = self._previous()
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return_stmt(keyword, value)
    
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
            
            elif isinstance(expr, Get_expr):
                return Set_expr(expr.object, expr.name, value)
            
            self._error(equals, "Invalid assignment target.")

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
        
        return self._call()
    
    def _call(self):
        expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_BRACE):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Expect propert name after '.'.")
                expr = Get_expr(expr, name)
            else:
                break
        
        return expr
    
    def _finish_call(self, callee: "Expr"):
        arguments = []
        if not self._check(TokenType.RIGHT_BRACE):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self._expression())
        paren = self._consume(TokenType.RIGHT_BRACE, "Expected ')' after arguments.")

        return Call_expr(callee, paren, arguments)
    
    def _primary(self):
        if self._match(TokenType.FALSE): return Literal_expr(False)
        if self._match(TokenType.TRUE): return Literal_expr(True)
        if self._match(TokenType.NIL): return Literal_expr(None)

        if self._match(TokenType.SUPER):
            keyword = self._previous()
            self._consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self._consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super_expr(keyword, method)

        if self._match(TokenType.THIS): return This_expr(self._previous())

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

    def _error(self, token: Token, message):
        parse_error(token, message)
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

    