from ast import parse
import typing as t
from functools import singledispatchmethod
from enum import Enum, auto

from ..parser.expr import *
from ..parser.stmt import *
from ..handle_errors import parse_error, error


class FunctionType(Enum):
    FUNCTION = auto()
    INITIALIZER = auto()
    NONE = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(BaseVisitor, StmtVisitor):
    def __init__(self, interpreter):
        self._interpreter = interpreter
        self._scopes = []
        self._current_function = FunctionType.NONE
        self._current_class = ClassType.NONE
    
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
            parse_error(expr.name, "Can't read local varialbe in its owm initializer.")
        
        self._resolve_local(expr, expr.name)
        return None
    
    def _declare(self, name: "Token"):
        if not self._scopes: return

        scope = self._scopes[-1]
        if name.lexeme in scope.keys():
            parse_error(name, "Already a variable with this name in this scope.")
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
    
    def visit_this_expr(self, expr: "This_expr"):
        if self._current_class == ClassType.NONE:
            error(expr.keyword.line, "Can't use 'this' outside of a class.")
            return None
        self._resolve_local(expr, expr.keyword)
        return None
    
    def visit_block_stmt(self, stmt: Block_stmt):
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()
    
    def visit_function_stmt(self, stmt: "Function_stmt"):
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt, FunctionType.FUNCTION)
        return None
    
    def _resolve_function(self, function: Function_stmt, type: FunctionType):
        enclosing_function = self._current_function
        self._current_function = type
        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._end_scope()
        self._current_function = enclosing_function
    
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
        if self._current_function == FunctionType.NONE:
            parse_error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self._current_function == FunctionType.INITIALIZER:
                parse_error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)
        return None
    
    def visit_class_stmt(self, stmt: "Class_stmt"):
        enclosing_class = self._current_class
        self._current_class = ClassType.CLASS
        self._declare(stmt.name)
        self._define(stmt.name)

        if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            error(stmt.superclass.name, "A class can't inherit from itself.")

        if stmt.superclass is not None:
            self._current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)
            self._begin_scope()
            self._scopes[-1]["super"] = True

        self._begin_scope()
        self._scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self._resolve_function(method, declaration)
        
        self._end_scope()
        if stmt.superclass is not None: self._end_scope()
        self._current_class = enclosing_class
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
    
    def visit_get_expr(self, expr: "Get_expr"):
        self.resolve(expr.object)
        return None
    
    def visit_set_expr(self, expr: "Set_expr"):
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None
    
    def visit_super_expr(self, expr: "Super_expr"):
        if self._current_class == ClassType.NONE:
            error(expr.keyword.line, "Can't use 'super' outside of a class.")
        elif self._current_class != ClassType.SUBCLASS:
            error(expr.keyword.line, "Can't use 'super' in a class with no superclass.")
        self._resolve_local(expr, expr.keyword)
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
