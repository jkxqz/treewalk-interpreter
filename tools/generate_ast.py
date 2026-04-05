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
            "Binary     : self, left: Expr, operator: Token, right: Expr",
            "Grouping   : self, expression: Expr",
            "Literal    : self, value: object",
            "Unary      : self, operator: Token, right: Expr"
        ])

        GenerateAst.defineAst(outputDir, "Stmt",[
            "ExpressionStmt     : self, expression: Expr",
            "PrintStmt          : self, expression: Expr"
        ])

    @staticmethod
    def defineAst(outputDir: str, baseName:str, types: list[str]):
        import os
        path: str = os.path.join(outputDir, baseName.lower() + '.py')
        with open(path, 'w') as f:
            f.write(f"from abc import ABC, abstractmethod\n\n")
            if baseName != "Expr":
                f.write(f"from expr import Expr\n")
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
