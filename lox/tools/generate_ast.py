import typing as t
from pathlib import Path
import sys


if len(sys.argv) != 2:
    print("Usage: generate_ast <output directory>")
    exit(64)

output_dir = sys.argv[1]

def define_ast(output_dir: str, base_name: str, base_name_2: str, types: t.List[str]):
    path = Path(output_dir + "/" + base_name_2.lower() + ".py")
    path.touch(exist_ok=True)
    with path.open("w") as f:
        f.write("from abc import ABC, abstractmethod\n")
        f.write("import typing as t\n\n")
        f.write("from ..lexer.token import Token\n")
        if base_name == "StmtVisitor": f.write("from .expr import Expr\n\n")
        else: f.write("\n")
        f.write(f"class {base_name}(ABC):\n")

        # visitor
        _define_visitor(f, base_name, types)

        # base accept
        f.write(f"class {base_name_2}(ABC):\n")
        f.write("   @abstractmethod\n")
        f.write(f"   def accept(self, visitor: \"{base_name}\"):\n")
        f.write("        pass\n\n")

        for type in types:
            classname = type.split("|")[0].strip()
            fields = type.split("|")[1].strip()
            _define_type(f, base_name_2, classname, fields)
            #f.write("\n   @abstractmethod\n")
            f.write(f"\n   def accept(self, visitor: \"{base_name}\"):\n")
            f.write(f"       return visitor.visit_{classname.lower()}(self)\n\n")

def _define_type(file, base_name_2: str, classname: str, fields: str):
    file.write(f"class {classname}({base_name_2}):\n")

    # constructor
    file.write(f"   def __init__(self, {fields}):\n")
    # initialize fields
    fields = fields.split(",")
    for field in fields:
        name = field.split(":")[0].strip()
        file.write(f"       self.{name} = {name}\n")

def _define_visitor(file, base_name, types):
    for type in types:
        file.write("    @abstractmethod\n")
        typename = type.split("|")[0].strip().lower()
        file.write(f"    def visit_{typename}(self, {typename}: \"{typename.capitalize()}\"):\n")
        file.write("        pass\n\n")
    file.write("\n")

define_ast(output_dir, "BaseVisitor", "Expr",
    ["Assign_expr | name: \"Token\", value: \"Expr\"",
    "Binary_expr | left: \"Expr\", operator: \"Token\", right: \"Expr\"",
    "Grouping_expr | expression: \"Expr\"",
    "Literal_expr | value: t.Any",
    "Unary_expr | operator: \"Token\", right: \"Expr\"",
    "Variable_expr | name: \"Token\""])

define_ast(output_dir, "StmtVisitor", "Stmt",
    ["Block_stmt | statements: t.List[\"Stmt\"]",
    "Expression_stmt | expression: \"Expr\"",
    "If_stmt | condition: \"Expr\", then_branch: \"Stmt\", else_branch: \"Stmt\"",
    "Print_stmt | expression: \"Expr\"",
    "Var_stmt | name: \"Token\", initializer: \"Expr\""])