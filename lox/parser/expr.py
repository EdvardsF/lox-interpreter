from abc import ABC, abstractmethod
import typing as t

from ..lexer.token import Token

class BaseVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, assign_expr: "Assign_expr"):
        pass

    @abstractmethod
    def visit_binary_expr(self, binary_expr: "Binary_expr"):
        pass

    @abstractmethod
    def visit_grouping_expr(self, grouping_expr: "Grouping_expr"):
        pass

    @abstractmethod
    def visit_literal_expr(self, literal_expr: "Literal_expr"):
        pass

    @abstractmethod
    def visit_logical_expr(self, logical_expr: "Logical_expr"):
        pass

    @abstractmethod
    def visit_unary_expr(self, unary_expr: "Unary_expr"):
        pass

    @abstractmethod
    def visit_variable_expr(self, variable_expr: "Variable_expr"):
        pass


class Expr(ABC):
   @abstractmethod
   def accept(self, visitor: "BaseVisitor"):
        pass

class Assign_expr(Expr):
   def __init__(self, name: "Token", value: "Expr"):
       self.name = name
       self.value = value

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_assign_expr(self)

class Binary_expr(Expr):
   def __init__(self, left: "Expr", operator: "Token", right: "Expr"):
       self.left = left
       self.operator = operator
       self.right = right

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_binary_expr(self)

class Grouping_expr(Expr):
   def __init__(self, expression: "Expr"):
       self.expression = expression

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_grouping_expr(self)

class Literal_expr(Expr):
   def __init__(self, value: t.Any):
       self.value = value

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_literal_expr(self)

class Logical_expr(Expr):
   def __init__(self, left: "Expr", operator: "Token", right: "Expr"):
       self.left = left
       self.operator = operator
       self.right = right

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_logical_expr(self)

class Unary_expr(Expr):
   def __init__(self, operator: "Token", right: "Expr"):
       self.operator = operator
       self.right = right

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_unary_expr(self)

class Variable_expr(Expr):
   def __init__(self, name: "Token"):
       self.name = name

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_variable_expr(self)

