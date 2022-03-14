from abc import ABC, abstractmethod
import typing as t

from ..lexer.token import Token
from .expr import Expr

class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, block_stmt: "Block_stmt"):
        pass

    @abstractmethod
    def visit_expression_stmt(self, expression_stmt: "Expression_stmt"):
        pass

    @abstractmethod
    def visit_if_stmt(self, if_stmt: "If_stmt"):
        pass

    @abstractmethod
    def visit_print_stmt(self, print_stmt: "Print_stmt"):
        pass

    @abstractmethod
    def visit_var_stmt(self, var_stmt: "Var_stmt"):
        pass


class Stmt(ABC):
   @abstractmethod
   def accept(self, visitor: "StmtVisitor"):
        pass

class Block_stmt(Stmt):
   def __init__(self, statements: t.List["Stmt"]):
       self.statements = statements

   def accept(self, visitor: "StmtVisitor"):
       return visitor.visit_block_stmt(self)

class Expression_stmt(Stmt):
   def __init__(self, expression: "Expr"):
       self.expression = expression

   def accept(self, visitor: "StmtVisitor"):
       return visitor.visit_expression_stmt(self)

class If_stmt(Stmt):
   def __init__(self, condition: "Expr", then_branch: "Stmt", else_branch: "Stmt"):
       self.condition = condition
       self.then_branch = then_branch
       self.else_branch = else_branch

   def accept(self, visitor: "StmtVisitor"):
       return visitor.visit_if_stmt(self)

class Print_stmt(Stmt):
   def __init__(self, expression: "Expr"):
       self.expression = expression

   def accept(self, visitor: "StmtVisitor"):
       return visitor.visit_print_stmt(self)

class Var_stmt(Stmt):
   def __init__(self, name: "Token", initializer: "Expr"):
       self.name = name
       self.initializer = initializer

   def accept(self, visitor: "StmtVisitor"):
       return visitor.visit_var_stmt(self)

