from src.dfa import compile as dfa_compile, DFAState

def compile(pattern: str) -> DFAState:
    return dfa_compile(pattern)

def match(pattern: str, string: str) -> bool:
    return compile(pattern).match(string)

if __name__ == '__main__':
    print("Example usage:")
    print(f"{match('a(b|c)*d', 'abccbd')=}")
    print(f"{match('a(b|c)*d', 'abccbde')=}")
    print("It works!")
    print()
    print("It is recommended to use the 'compile' function to compile the pattern once and then use the resulting DFAState to match multiple strings.")
    print("This is much faster than compiling the pattern every time a string is matched.")
    print()
    print("Example usage:")
    print("compiled = compile('a(b|c)*d')")
    compiled = compile('a(b|c)*d')
    print(f"{compiled.match('abccbd')=}")
    print(f"{compiled.match('abccbde')=}")     
    