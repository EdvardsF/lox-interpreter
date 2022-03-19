import typing as t
from functools import singledispatchmethod

from ..parser.expr import *
from ..parser.stmt import *
from ..handle_errors import report



class Resolver(BaseVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self._interpreter = interpreter
        self._scopes = []
    
    def visit_var_stmt(self, stmt: "Var_stmt"):
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self._define(stmt.name)
        return None
    
    def visit_assign_expr(self, expr: "Assign_expr"):
        self.resolve(expr.value)
        self._resolve_local(expr, expr.name)
        return None
    
    def visit_variable_expr(self, expr: Variable_expr):
        if self._scopes and self._scopes[-1].get(expr.name.lexeme) is False:
            report(expr.name.line, expr.name.lexeme, 0, "Can't read local varialbe in its owm initializer.")
        
        self._resolve_local(expr, expr.name)
        return None
    
    def _declare(self, name: "Token"):
        if not self._scopes: return

        scope = self._scopes[-1]
        scope[name.lexeme] = False
    
    def _define(self, name: "Token"):
        if not self._scopes: return
        scope = self._scopes[-1]
        scope[name.lexeme] = True
    
    def _resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope.keys():
                self._interpreter.resolve(expr, i)
                return
    
    def visit_block_stmt(self, stmt: Block_stmt):
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()
    
    def visit_function_stmt(self, stmt: "Function_stmt"):
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt)
        return None
    
    def _resolve_function(self, function: Function_stmt):
        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._end_scope()
    
    def visit_expression_stmt(self, stmt: "Expression_stmt"):
        self.resolve(stmt.expression)
        return None

    def visit_if_stmt(self, stmt: "If_stmt"):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: "Print_stmt"):
        self.resolve(stmt.expression)
        return None
    
    def visit_return_stmt(self, stmt: "Return_stmt"):
        if stmt.value is not None:
            self.resolve(stmt.value)
        return None
    
    def visit_while_stmt(self, stmt: "While_stmt"):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None
    
    def visit_binary_expr(self, expr: "Binary_expr"):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visit_call_expr(self, expr: "Call_expr"):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)
        return None
    
    def visit_grouping_expr(self, expr: "Grouping_expr"):
        self.resolve(expr.expression)
        return None

    def visit_literal_expr(self, expr: "Literal_expr"):
        return None
    
    def visit_logical_expr(self, expr: "Logical_expr"):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None
    
    def visit_unary_expr(self, expr: "Unary_expr"):
        self.resolve(expr.right)
        return None

    def _begin_scope(self):
        self._scopes.append({})
    
    def _end_scope(self):
        self._scopes.pop()
    
    @singledispatchmethod
    def resolve(self, arg):
        raise NotImplementedError(f"Unexpected type provided.")
    
    @resolve.register(list)
    def _(self, arg: t.List[Stmt]):
        for statement in arg:
            self.resolve(statement)

    @resolve.register(Stmt)
    def _(self, arg: Stmt):
        arg.accept(self)

    @resolve.register(Expr)
    def _(self, arg: Expr):
        arg.accept(self)
