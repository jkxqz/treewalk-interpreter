import sys
from scanner import Scanner

class Lox:

    @staticmethod
    def run(source: str):
        scanner = Scanner(source)
        tokens = scanner.scanTokens()
        for token in tokens:
            print(token, flush=True)

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

    hadError: bool = False

if __name__ == "__main__":
    Lox.main(sys.argv[1:])
    #def error(self, line: int, message: str):
    #self.report(line, "", message)
    