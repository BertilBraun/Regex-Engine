import enum
from typing import Generator


class TokenType(enum.Enum):
    LITERAL = 1                 # a, b, c, 1, 2, 3, etc.
    GROUP_START = 2             # (
    GROUP_END = 3               # )
    CLASS_START = 4             # [
    CLASS_END = 5               # ]
    OR = 6                      # |
    WILDCARD = 7                # .
    ZERO_INF = 8                # *
    ONE_INF = 9                 # +
    ZERO_ONE = 10               # ?
    ESCAPED = 11                # \a, \b, \c, \1, \2, \3, etc.
    RANGE = 12                  # a-z, 1-9, etc.
    SPECIFIC_QUANTIFIER = 13    # {1, 3}, {2, 4}, etc.
    #START_ANCHOR = 14           # ^
    #END_ANCHOR = 15             # $


class Token:
    def __init__(self, type: TokenType, value: str) -> None:
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.value)})"
    
    def __eq__(self, other) -> bool:
        return self.type == other.type and self.value == other.value


class Tokenizer:
    def __init__(self, regex) -> None:
        self.__tokens = self.tokenize(regex)
        self.__previous = None
        self.__current = next(self.__tokens, None)
        
    @property
    def current(self) -> Token:
        if self.__current is None:
            raise Exception("Unexpected end of input")
        return self.__current
    
    @property
    def previous(self) -> Token:
        if self.__previous is None:
            raise Exception("No previous token")
        return self.__previous

    def next(self) -> None:
        self.__previous = self.__current
        self.__current = next(self.__tokens, None)
        
    def is_done(self) -> bool:
        return self.__current is None
        
    def match(self, token_type: TokenType) -> bool:
        if not self.is_done() and self.current.type == token_type:
            self.next()
            return True
        else:
            return False

    def expect(self, token_type: TokenType) -> bool:
        if self.match(token_type):
            return True
        else:
            raise Exception(f"Expected {token_type} but got {self.current}")

    def tokenize(self, regex: str) -> Generator[Token, None, None]:
        def get(error_message: str = "Unexpected end of input") -> str:
            nonlocal i
            if i >= len(regex):
                raise Exception(error_message)
            return regex[i]

        i = 0
        while i < len(regex):
            char = get()
            
            if char == '(':
                yield Token(TokenType.GROUP_START, char)
            elif char == ')':
                yield Token(TokenType.GROUP_END, char)
            elif char == '[':
                yield Token(TokenType.CLASS_START, char)
            elif char == ']':
                yield Token(TokenType.CLASS_END, char)
            elif char == '|':
                yield Token(TokenType.OR, char)
            elif char == '*':
                yield Token(TokenType.ZERO_INF, char)
            elif char == '+':
                yield Token(TokenType.ONE_INF, char)
            elif char == '?':
                yield Token(TokenType.ZERO_ONE, char)
            elif char == '.':
                yield Token(TokenType.WILDCARD, char)
            # elif char == '^':
            #     yield Token(TokenType.START_ANCHOR, char)
            # elif char == '$':
            #     yield Token(TokenType.END_ANCHOR, char)
            elif char == '\\':
                i += 1
                char = get("Unfinished escape sequence")
                yield Token(TokenType.ESCAPED, char)
            elif char == '{':
                j = i + 1
                while get("Unfinished quantifier") != '}':
                    i += 1
                cleaned = regex[j:i].replace(' ', '').replace('\t', '')
                yield Token(TokenType.SPECIFIC_QUANTIFIER, cleaned)
            elif char == '-':
                yield Token(TokenType.RANGE, char)            
            else:
                yield Token(TokenType.LITERAL, char)
            
            i += 1
            
            
if __name__ == '__main__':
    test_cases = [
        {
            "pattern": "(ab)*",
            "expected_tokens": [
                Token(TokenType.GROUP_START, '('),
                Token(TokenType.LITERAL, 'a'),
                Token(TokenType.LITERAL, 'b'),
                Token(TokenType.GROUP_END, ')'),
                Token(TokenType.ZERO_INF, '*')
            ]
        },
        {
            "pattern": "[a-z]+",
            "expected_tokens": [
                Token(TokenType.CLASS_START, '['),
                Token(TokenType.LITERAL, 'a'),
                Token(TokenType.RANGE, '-'),
                Token(TokenType.LITERAL, 'z'),
                Token(TokenType.CLASS_END, ']'),
                Token(TokenType.ONE_INF, '+')
            ]
        },
        {
            "pattern": "a|b|c",
            "expected_tokens": [
                Token(TokenType.LITERAL, 'a'),
                Token(TokenType.OR, '|'),
                Token(TokenType.LITERAL, 'b'),
                Token(TokenType.OR, '|'),
                Token(TokenType.LITERAL, 'c')
            ]
        },
        {
            "pattern": "a{1,3}?",
            "expected_tokens": [
                Token(TokenType.LITERAL, 'a'),
                Token(TokenType.SPECIFIC_QUANTIFIER, '1,3'),
                Token(TokenType.ZERO_ONE, '?')
            ]
        },
        {
            # complex pattern
            "pattern": "a(b|c)*d",
            "expected_tokens": [
                Token(TokenType.LITERAL, 'a'),
                Token(TokenType.GROUP_START, '('),
                Token(TokenType.LITERAL, 'b'),
                Token(TokenType.OR, '|'),
                Token(TokenType.LITERAL, 'c'),
                Token(TokenType.GROUP_END, ')'),
                Token(TokenType.ZERO_INF, '*'),
                Token(TokenType.LITERAL, 'd')
            ]
        },
        {
            # with escaped characters, range, wildcard, and quantifiers
            "pattern": "\\d{1,2}-\\d{1,2}-\\d{4}",
            "expected_tokens": [
                Token(TokenType.ESCAPED, 'd'),
                Token(TokenType.SPECIFIC_QUANTIFIER, '1,2'),
                Token(TokenType.RANGE, '-'),
                Token(TokenType.ESCAPED, 'd'),
                Token(TokenType.SPECIFIC_QUANTIFIER, '1,2'),
                Token(TokenType.RANGE, '-'),
                Token(TokenType.ESCAPED, 'd'),
                Token(TokenType.SPECIFIC_QUANTIFIER, '4')
            ]
        }
    ]

    for test_case in test_cases:
        pattern = test_case["pattern"]
        expected_tokens = test_case["expected_tokens"]
        tokenizer = Tokenizer(pattern)
        actual_tokens = []
        while not tokenizer.is_done():
            actual_tokens.append(tokenizer.current)
            tokenizer.next()

        assert actual_tokens == expected_tokens, f"Test failed for pattern '{pattern}'. Expected {expected_tokens}, but got {actual_tokens}"
        
        print(f"Test passed for pattern '{pattern}'.")
