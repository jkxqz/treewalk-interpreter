from sys import argv
from typing import IO

class GenerateAst:
    @staticmethod
    def main(args: list[str]):
        if len(args) != 1:
            print("Usage: python generate_ast <output directory>", flush=True)
            exit(64)
        outputDir: str = args[0]
        GenerateAst.defineAst(outputDir, "Expr",[
            "Assign     : self, name: Token, value: Expr",
            "Binary     : self, left: Expr, operator: Token, right: Expr",
            "Grouping   : self, expression: Expr",
            "Literal    : self, value: object",
            "Unary      : self, operator: Token, right: Expr",
            "Variable   : self, name: Token",
        ])

        GenerateAst.defineAst(outputDir, "Stmt",[
            "BlockStmt          : self, statements: list[Optional[Stmt]]",
            "ExpressionStmt     : self, expression: Expr",
            "IfStmt             : self, condition: Expr, thenBranch: Stmt, elseBranch: Optional[Stmt] = None",
            "PrintStmt          : self, expression: Expr",
            "VarStmt            : self, name: Token, initializer: Optional[Expr] = None",
        ])

    @staticmethod
    def defineAst(outputDir: str, baseName:str, types: list[str]):
        import os
        path: str = os.path.join(outputDir, baseName.lower() + '.py')
        with open(path, 'w') as f:
            f.write(f"from abc import ABC, abstractmethod\n")
            if baseName == "Stmt":
                f.write(f"from typing import Optional\n\n")
                f.write(f"from expr import Expr\n")
            else:
                f.write(f"\n")
            f.write(f"from token_ import Token\n\n")
            f.write(f"class {baseName}(ABC):\n")
            f.write("\t@abstractmethod\n")
            f.write("\tdef accept(self, visitor):\n")
            f.write("\t\tpass\n\n")
            for t in types:
                fields: str = t[t.find(':')+1:].strip()
                className: str = t[:t.find(':')].strip()
                GenerateAst.defineType(f, baseName, className, fields)
                f.write('\n')
    
    @staticmethod
    def defineType(f: IO, baseName: str, className: str, fieldList: str):
        f.write(f"class {className}({baseName}):\n")
        f.write(f"\tdef __init__({fieldList}):\n")
        fields: list[str] = fieldList.split(', ')[1:] # ignoring lone 'self'
        for field in fields:
            name: str = field.split(':')[0]
            f.write(f"\t\tself.{name} = {name}\n")
        f.write(f"\tdef accept(self, visitor):\n")
        if baseName != "Stmt":
            f.write(f"\t\treturn visitor.visit{className}{baseName}(self)\n")
        else:
            f.write(f"\t\treturn visitor.visit{className}(self)\n")


if __name__ == "__main__":
    GenerateAst.main(argv[1:])
