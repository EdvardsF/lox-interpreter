from ..parser.expr import *
from ..lexer.token import Token, TokenType


class AstPrinter():
    def print(self, expr: Expr):
        return expr.accept(self)
    
    def visit_binary_expr(self, expr: Binary_expr):
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_unary_expr(self, expr: Unary_expr):
        return self._parenthesize(expr.operator.lexeme, expr.right)
    
    def visit_literal_expr(self, expr: Literal_expr):
        return str(expr.value)
    
    def visit_grouping_expr(self, expr: Grouping_expr):
        return self._parenthesize("group", expr.expression)
    
    def _parenthesize(self, name: str, *args: "Expr"):
        parenthesized = "("
        parenthesized += name
        for expr in args:
            parenthesized += " " + expr.accept(self)
        parenthesized += ")"
        return parenthesized