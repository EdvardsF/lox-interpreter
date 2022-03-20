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
    def visit_call_expr(self, call_expr: "Call_expr"):
        pass

    @abstractmethod
    def visit_get_expr(self, get_expr: "Get_expr"):
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
    def visit_set_expr(self, set_expr: "Set_expr"):
        pass

    @abstractmethod
    def visit_super_expr(self, super_expr: "Super_expr"):
        pass

    @abstractmethod
    def visit_this_expr(self, this_expr: "This_expr"):
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

class Call_expr(Expr):
   def __init__(self, callee: "Expr", paren: "Token", arguments: t.List["Expr"]):
       self.callee = callee
       self.paren = paren
       self.arguments = arguments

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_call_expr(self)

class Get_expr(Expr):
   def __init__(self, object: "Expr", name: "Token"):
       self.object = object
       self.name = name

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_get_expr(self)

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

class Set_expr(Expr):
   def __init__(self, object: "Expr", name: "Token", value: "Expr"):
       self.object = object
       self.name = name
       self.value = value

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_set_expr(self)

class Super_expr(Expr):
   def __init__(self, keyword: "Token", method: "Token"):
       self.keyword = keyword
       self.method = method

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_super_expr(self)

class This_expr(Expr):
   def __init__(self, keyword: "Token"):
       self.keyword = keyword

   def accept(self, visitor: "BaseVisitor"):
       return visitor.visit_this_expr(self)

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

