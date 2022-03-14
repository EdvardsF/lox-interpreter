from turtle import st
import typing as t

from ..lexer.token_type import TokenType
from ..lexer.token import Token
from ..parser.expr import *
from ..parser.stmt import *
from ..errors import RuntimeException
from ..handle_errors import runtime_error
from .environment import Environment


class Interpreter(BaseVisitor, StmtVisitor):
    def __init__(self):
        self._environment = Environment()

    def interpret(self, statements: t.List["Stmt"]):
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeException as e:
            runtime_error(e)
        
    def visit_block_stmt(self, stmt: "Block_stmt"):
        self._execute_block(stmt.statements, Environment(self._environment))
        return None
    
    def _execute_block(self, statements: t.List["Stmt"], environment: "Environment"):
        previous = self._environment

        try:
            self._environment = environment

            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous
    
    def visit_assign_expr(self, expr: "Assign_expr"):
        value = self._evaluate(expr.value)
        self._environment.assign(expr.name, value)
        return value
        
    def visit_var_stmt(self, statement: "Stmt"):
        value = None
        if statement.initializer is not None:
            value = self._evaluate(statement.initializer)
        
        self._environment.define(statement.name.lexeme, value)
    
    def visit_variable_expr(self, expr: "Expr"):
        return self._environment.get(expr.name)
    
    def _execute(self, statement: "Stmt"):
        return statement.accept(self)
    
    def visit_expression_stmt(self, stmt: "Expression_stmt"):
        value = self._evaluate(stmt.expression)
        # TODO here
        print(value)
    
    def visit_if_stmt(self, stmt: "If_stmt"):
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)
        return None
    
    def visit_print_stmt(self, stmt: "Print_stmt"):
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))
        return None

    def visit_literal_expr(self, expr: "Literal_expr"):
        return expr.value
    
    def visit_grouping_expr(self, expr: "Grouping_expr"):
        return self._evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: "Unary_expr"):
        right = self._evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -float(right)
        
        elif expr.operator.type == TokenType.BANG:
            return not self._is_truthy(right)
        
        return None
    
    def visit_binary_expr(self, expr: "Binary_expr"):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        if expr.operator.type == TokenType.PLUS:
            if isinstance(right, float) and isinstance(left, float):
                return float(right) + float(left)
            elif isinstance(right, str) and isinstance(left, str):
                return str(right) + str(left)
            else:
                raise RuntimeException(expr.operator, "Operands must be two numbers or two strings")
        
        elif expr.operator.type == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        
        elif expr.operator.type == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        
        elif expr.operator.type == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)

        elif expr.operator.type == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        
        elif expr.operator.type == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
        
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        
        return None
    
    def _evaluate(self, expr: "Expr"):
        return expr.accept(self)
    
    def _is_truthy(self, val: t.Any):
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        return True
    
    def _is_equal(self, a: t.Any, b: t.Any):
        return a == b
    
    def _check_number_operand(self, operator: Token, operand: t.Any):
        if isinstance(operand, float): return
        raise RuntimeException(operator, "Operand must be a number.")
    
    def _check_number_operands(self, operator: Token, left: t.Any, right: t.Any):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeException(operator, "Operands must be numbers.")
    
    def _stringify(self, value: t.Any):
        if value is None: return "nil"
        elif isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        else:
            return str(value)

