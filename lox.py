import sys
from scanner import Scanner
from token_ import Token
from tokentype import TokenType
from expr import Expr
from astPrinter import AstPrinter
from typing import no_type_check
class Lox:

    @staticmethod
    @no_type_check
    def run(source: str):
        from parser import Parser
        scanner = Scanner(source)
        tokens = scanner.scanTokens()
        #for token in tokens:
        #    print(token, flush=True)
        parser: Parser = Parser(tokens)
        expression: Expr = parser.parse()
        if Lox.hadError: return
        print(AstPrinter().print(expression))

    @staticmethod
    def runFile(path: str):
        # read entire file as one string
        with open(path, 'r') as f:
            _bytes: str = f.read()
        Lox.run(_bytes)
        if Lox.hadError: sys.exit(65)


    @staticmethod
    def runPrompt():
        while True:
            try:
                line = input("> ")
            except EOFError:
                break
            if not line: break
            Lox.run(line)
            Lox.hadError = False

    @staticmethod
    def main(args: list[str]):
        if len(args) > 1:
            print("Usage: lox [script]", flush=True)
            exit(64) # exit code taken from book
        elif len(args) == 1:
            Lox.runFile(args[0])
        else:
            Lox.runPrompt()
    
    @staticmethod 
    def error(line: int, message: str):
        Lox.report(line, "", message)
    
    @staticmethod
    def report(line: int, where: str, message: str):
        print("[line " + str(line) + "] Error" + where + ": " + message, flush=True)
        Lox.hadError = True

    @staticmethod 
    def error1(token: Token, message: str):
        if token.type == TokenType.EOF:
            Lox.report(token.line, " at end", message)
        else:
            Lox.report(token.line, f" at '{token.lexeme}'", message)

    hadError: bool = False

if __name__ == "__main__":
    Lox.main(sys.argv[1:])
    #def error(self, line: int, message: str):
    #self.report(line, "", message)
    