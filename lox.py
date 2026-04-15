import sys
from typing import no_type_check

from astPrinter import AstPrinter
from expr import *
from interpreter import Interpreter
from loxruntimeerror import LoxRuntimeError
from resolver import Resolver
from scanner import Scanner
from stmt import *
from token_ import Token
from tokentype import TokenType

class Lox:

    def __init__(self):
        self.hadRuntimeError: bool = False
        self.hadError: bool = False
        self.interpreter: Interpreter = Interpreter(self)

    @no_type_check
    def run(self, source: str):
        from parser import Parser
        scanner: Scanner = Scanner(self, source)
        tokens: list[Token] = scanner.scanTokens()
        parser: Parser = Parser(self, tokens)
        statements: list[Stmt] = parser.parse()
        if self.hadError: return
        resolver: Resolver = Resolver(self, self.interpreter)
        resolver.resolveList(statements)
        if self.hadError: return
        self.interpreter.interpret(statements)

    def runFile(self, path: str):
        # read entire file as one string
        with open(path, 'r') as f:
            _bytes: str = f.read()
        self.run(_bytes)
        if self.hadError: sys.exit(65)
        if self.hadRuntimeError: sys.exit(70)

    def runPrompt(self):
        while True:
            try:
                line: str = input("> ")
            except EOFError:
                break
            if not line: break
            self.run(line)
            self.hadError = False

    def main(self, args: list[str]):
        if len(args) > 1:
            print("Usage: lox [script]", flush=True)
            exit(64) # exit code taken from book
        elif len(args) == 1:
            self.runFile(args[0])
        else:
            self.runPrompt()
    
    def error(self, line: int, message: str):
        self.report(line, "", message)
    
    def report(self, line: int, where: str, message: str):
        print("[line " + str(line) + "] Error" + where + ": " + message, flush=True)
        self.hadError = True

    def error1(self, token: Token, message: str):
        if token.type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)
    
    def runtimeError(self, error: LoxRuntimeError):
        print(f"{error.args[0]}\n[line {error.token.line} ]")
        self.hadRuntimeError = True


if __name__ == "__main__":
    Lox().main(sys.argv[1:])
    