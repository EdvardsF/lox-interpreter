import typing as t

from ..lexer.token_type import TokenType
from ..lexer.token import Token
from ..parser.expr import *
from ..parser.stmt import *
from ..errors import RuntimeException, Return
from ..handle_errors import runtime_error
from .environment import Environment
from .callable import Callable, Function
import lox.interpreter.natives as natives
from lox.interpreter.natives import *
from .lox_class import Class, Instance


def classesinmodule(module):
    md = module.__dict__
    return [
        md[c] for c in md if (
            isinstance(md[c], type) and md[c].__module__ == module.__name__
        )
    ]


class Interpreter(BaseVisitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self._locals = {}
        self._environment = self.globals
        native_function_classes = classesinmodule(natives)
        for cls in native_function_classes:
            self.globals.define(cls.__name__.lower(), cls())

    def interpret(self, statements: t.List["Stmt"]):
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeException as e:
            runtime_error(e)
    
    def resolve(self, expr: Expr, depth: int):
        self._locals[expr] = depth
        
    def visit_block_stmt(self, stmt: "Block_stmt"):
        self._execute_block(stmt.statements, Environment(self._environment))
        return None
    
    def visit_class_stmt(self, stmt: "Class_stmt"):
        superclass = None
        if stmt.superclass is not None:
            superclass = self._evaluate(stmt.superclass)
            if not isinstance(superclass, Class):
                raise RuntimeException(stmt.superclass.name, "Superclass must be a class.")

        self._environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            environment = Environment(self._environment)
            self._environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = Function(method, self._environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        lox_class = Class(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self._environment = environment._enclosing

        self._environment.assign(stmt.name, lox_class)
        return None
    
    def visit_this_expr(self, expr: "This_expr"):
        return self._look_up_variable(expr.keyword, expr)
    
    def _execute_block(self, statements: t.List["Stmt"], environment: "Environment"):
        previous = self._environment

        try:
            self._environment = environment

            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous
    
    def visit_assign_var_expr(self, expr: "Assign_var_expr"):
        value = self._evaluate(expr.value)
        if expr in self._locals.keys():
            self._environment.assign_at(self._locals[expr], expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value
        
    def visit_var_stmt(self, statement: "Stmt"):
        value = None
        if statement.initializer is not None:
            value = self._evaluate(statement.initializer)
        
        self._environment.define(statement.name.lexeme, value)
    
    def visit_while_stmt(self, stmt: "While_stmt"):
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)
        return None
    
    def visit_variable_expr(self, expr: "Expr"):
        return self._look_up_variable(expr.name, expr)
    
    def visit_list_expr(self, expr: "List_expr"):
         return self._look_up_variable(expr.name, expr)
    
    def _look_up_variable(self, name: Token, expr: Expr):
        if expr in self._locals.keys():
            return self._environment.get_at(self._locals[expr], name.lexeme)
        else:
            return self.globals.get(name)
    
    def _execute(self, statement: "Stmt"):
        return statement.accept(self)
    
    def visit_expression_stmt(self, stmt: "Expression_stmt"):
        value = self._evaluate(stmt.expression)
    
    def visit_function_stmt(self, stmt: "Function_stmt"):
        function = Function(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)
    
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
    
    def visit_return_stmt(self, stmt: "Return_stmt"):
        value = None
        if stmt.value: value = self._evaluate(stmt.value)

        raise Return(value)

    def visit_literal_expr(self, expr: "Literal_expr"):
        return expr.value
    
    def visit_logical_expr(self, expr: "Logical_expr"):
        left = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self._is_truthy(left): return left
        else:
            if not self._is_truthy(left): return left
        
        return self._evaluate(expr.right)
    
    def visit_set_expr(self, expr: "Set_expr"):
        object_ = self._evaluate(expr.object)

        if not isinstance(object_, Instance):
            raise RuntimeException(expr.name, "Only instances have fields.")
        
        value = self._evaluate(expr.value)
        object_.set(expr.name, value)
        return value
    
    def visit_super_expr(self, expr: "Super_expr"):
        distance = self._locals.get(expr)
        superclass = self._environment.get_at(distance, "super")
        obj = self._environment.get_at(distance - 1, "this")
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeException(expr.method, f"Undefined property '{expr.method.lexeme}'.")
        return method.bind(obj)
    
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
                return float(left) + float(right)
            elif isinstance(right, str) and isinstance(left, str):
                return str(left) + str(right)
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
    
    def visit_call_expr(self, expr: "Call_expr"):
        callee = self._evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))
        
        if not isinstance(callee, Callable):
            raise RuntimeException(expr.paren, "Object is not callable.")
        
        func = callee
        if len(arguments) != func.arity:
            raise RuntimeException(expr.paren, f"Expected {func.arity} arguments, but got {len(arguments)}.")

        return func.call(self, arguments)

    def visit_get_expr(self, expr: "Get_expr"):
        object_ = self._evaluate(expr.object)
        if isinstance(object_, Instance):
            return object_.get(expr.name)
        raise RuntimeException(expr.name, "Only instances can have properties.")
    
    def visit_list_get_expr(self, expr: "List_get_expr"):
        index = self._evaluate(expr.index)
        list_obj = self._evaluate(expr.name)

        if int(index) != index:
            raise RuntimeException(expr.paren, "List index must be an integer.")

        index = int(index)

        if not 0 <= index < len(list_obj):
            raise RuntimeException(expr.paren, "List index out of range.")
        
        return list_obj[index]
    
    def visit_assign_list_expr(self, expr: "Assign_list_expr"):
        values = []
        for val in expr.values:
            values.append(self._evaluate(val))
        if expr in self._locals.keys():
            self._environment.assign_at(self._locals[expr], expr.name, values)
        else:
            self.globals.assign(expr.name, values)
        return values

    def visit_list_stmt(self, stmt: "List_stmt"):
        values = []
        for val in stmt.values:
            values.append(self._evaluate(val))
        
        self._environment.define(stmt.name.lexeme, values)
    
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
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, float):
            return str(value).replace(".0", "")
        elif isinstance(value, list):
            return str(value).replace(".0", "")
        else:
            return str(value)

