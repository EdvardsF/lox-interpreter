import typing as t

from ..parser.expr import *
from ..parser.stmt import *
from ..handle_errors import report



class Reosolver(BaseVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self._interpreter = interpreter
        self._scopes = []
    
    def visit_var_stmt(self, stmt: "Var_stmt"):
        self._declare(stmt.name)
        if stmt.name is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)
        return None
    
    def _declare(self, name: "Token"):
        if not self._scopes: return

        scope = self._scopes[-1]
        scope[name.lexeme] = False
    
    def _define(self, name: "Token"):
        if not self._scopes: return
        scope = self._scopes[-1]
        scope[name.lexeme] = True
    
    def visit_block_stmt(self, stmt: Block_stmt):
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()
    
    def _begin_scope(self):
        self._scopes.append({})
    
    def _end_scope(self):
        self._scopes.pop()
    
    def _resolve(self, statements):
        for statement in statements:
            self._resolve_stmt(statement)
    
    def _resolve_stmt(self, stmt: Stmt):
        stmt.accept(self)
    
    def _resolve_expr(self, expr: Expr):
        expr.accept(self)
