from src.token import TokenType, Tokenizer


class ASTNode:
    pass

class LiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value
        
    def __repr__(self) -> str:
        return f"LiteralNode({repr(self.value)})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, LiteralNode) and self.value == other.value

class RangeNode(ASTNode):
    WILDCARD = 'WILDCARD'
    
    def __init__(self, start, end):
        self.start = start
        self.end = end
        
    def __repr__(self) -> str:
        return f"RangeNode({self.start}, {self.end})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, RangeNode) and self.start == other.start and self.end == other.end
    
    @property
    def is_wildcard(self):
        return self.start == self.WILDCARD and self.end == self.WILDCARD

class ClassNode(ASTNode):
    def __init__(self, ranges: list[RangeNode]):
        self.ranges = ranges
        
    def __repr__(self) -> str:
        return f"CharacterClassNode({self.ranges})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ClassNode) and self.ranges == other.ranges

class ZeroOrMoreNode(ASTNode):
    def __init__(self, node):
        self.node = node
        
    def __repr__(self) -> str:
        return f"ZeroOrMoreNode({self.node})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ZeroOrMoreNode) and self.node == other.node
    
class OneOrMoreNode(ASTNode):
    def __init__(self, node):
        self.node = node
        
    def __repr__(self) -> str:
        return f"OneOrMoreNode({self.node})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, OneOrMoreNode) and self.node == other.node
    
class ZeroOrOneNode(ASTNode):
    def __init__(self, node):
        self.node = node
        
    def __repr__(self) -> str:
        return f"ZeroOrOneNode({self.node})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ZeroOrOneNode) and self.node == other.node
    
class SpecificQuantifierNode(ASTNode):
    def __init__(self, node, min, max):
        self.node = node
        self.min = min
        self.max = max
        
    def __repr__(self) -> str:
        return f"SpecificQuantifierNode({self.node}, {self.min}, {self.max})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, SpecificQuantifierNode) and self.node == other.node and self.min == other.min and self.max == other.max
    
class ConcatenationNode(ASTNode):
    def __init__(self, nodes):
        self.nodes = nodes
        
    def __repr__(self) -> str:
        return f"ConcatenationNode({self.nodes})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ConcatenationNode) and self.nodes == other.nodes
    
class AlternationNode(ASTNode):
    def __init__(self, nodes):
        self.nodes = nodes
        
    def __repr__(self) -> str:
        return f"AlternationNode({self.nodes})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, AlternationNode) and self.nodes == other.nodes
    
class GroupNode(ASTNode):
    def __init__(self, node):
        self.node = node
        
    def __repr__(self) -> str:
        return f"GroupNode({self.node})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, GroupNode) and self.node == other.node
    
class EscapedCharacterNode(ASTNode):
    def __init__(self, value):
        self.value = value
        
    def __repr__(self) -> str:
        return f"EscapedCharacterNode({repr(self.value)})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, EscapedCharacterNode) and self.value == other.value
    
# class StartAnchorNode(ASTNode):
#     def __init__(self):
#         pass
#     
#     def __repr__(self) -> str:
#         return "StartAnchorNode()"
#     
# class EndAnchorNode(ASTNode):
#     def __init__(self):
#         pass
#     
#     def __repr__(self) -> str:
#         return "EndAnchorNode()"
    
    
"""
We will parse the regex into an abstract syntax tree (AST) using the following grammar:
```
Regex -> Concatenation RegexTail
RegexTail -> '|' Concatenation RegexTail | ε
Concatenation -> Unit ConcatenationTail
ConcatenationTail -> Unit ConcatenationTail | ε
Unit -> Character | Class | Group | QuantifiedUnit
Class -> '[' CharRange ']'
CharRange -> Char RangeTail
RangeTail -> '-' CharRange | ε
Group -> '(' Regex ')'
QuantifiedUnit -> Unit Quantifier
Quantifier -> '*' | '+' | '?' | '{' Number ',' Number '}'
Char -> any non-special character | '\' SpecialCharacter | '.'
```

In this structure, we've introduced `RegexTail`, `ConcatenationTail`, and `RangeTail` to maintain a left-linear form.

1. **Regex/RegexTail:** The identifying prefix is the first token of `Concatenation`, which is the first token of `Unit`.
2. **Concatenation/ConcatenationTail:** The identifying prefix is the first token of `Unit`.
3. **Unit:** The identifying prefix depends on the specific type of unit (`Character`, `CharacterClass`, `Group`, `QuantifiedUnit`).
4. **CharacterClass:** The identifying prefix is `[`.
5. **CharRange/RangeTail:** The identifying prefix is any character token.
6. **Group:** The identifying prefix is `(`.
7. **QuantifiedUnit:** The identifying prefix is the first token of `Unit`, followed by a quantifier token.
8. **Quantifier:** The identifying prefix is one of the quantifier symbols (`*`, `+`, `?`, `{`).
9. **Character:** The identifying prefix is any non-special character or `\\` followed by a special character.
"""

class ASTParser:
    def __init__(self, regex: str) -> None:
        self.tokenizer = Tokenizer(regex)
        
    def parse(self) -> ASTNode:
        return self.__parse_regex()

    def __parse_regex(self) -> ASTNode:
        concatenations = [self.__parse_concatenation()]
        
        while not self.tokenizer.is_done() and self.tokenizer.match(TokenType.OR):
            concatenations.append(self.__parse_concatenation())
            
        return AlternationNode(concatenations) if len(concatenations) > 1 else concatenations[0]
        
    def __parse_concatenation(self) -> ASTNode:
        units = [self.__parse_unit()]
        
        while not self.tokenizer.is_done() and self.tokenizer.current.type not in [TokenType.OR, TokenType.GROUP_END]:
            units.append(self.__parse_unit())
            
        return ConcatenationNode(units) if len(units) > 1 else units[0]
        
    def __parse_unit(self) -> ASTNode:
        unit = self.__parse_basic_unit()
        
        if self.tokenizer.is_done():
            return unit
        # Apply quantifiers if present
        return self.__parse_quantifier(unit)
        
    def __parse_basic_unit(self) -> ASTNode:
        if self.tokenizer.match(TokenType.LITERAL):
            return LiteralNode(self.tokenizer.previous.value)
        elif self.tokenizer.match(TokenType.CLASS_START):
            char_range = self.__parse_char_range()
            return ClassNode(char_range)
        elif self.tokenizer.match(TokenType.GROUP_START):
            regex = self.__parse_regex()
            self.tokenizer.expect(TokenType.GROUP_END)
            return GroupNode(regex)
        elif self.tokenizer.match(TokenType.ESCAPED):
            return EscapedCharacterNode(self.tokenizer.previous.value)
        elif self.tokenizer.match(TokenType.WILDCARD):
            return RangeNode(RangeNode.WILDCARD, RangeNode.WILDCARD)
        elif self.tokenizer.match(TokenType.RANGE):
            return LiteralNode(self.tokenizer.previous.value)
        else:
            raise Exception(f"Unexpected token {self.tokenizer.current}")

    def __parse_quantifier(self, unit: ASTNode) -> ASTNode:
        if self.tokenizer.match(TokenType.ZERO_INF):
            return ZeroOrMoreNode(unit)
        elif self.tokenizer.match(TokenType.ONE_INF):
            return OneOrMoreNode(unit)
        elif self.tokenizer.match(TokenType.ZERO_ONE):
            return ZeroOrOneNode(unit)
        elif self.tokenizer.match(TokenType.SPECIFIC_QUANTIFIER):
            quantifier_parts = self.tokenizer.previous.value.split(',')
            min = int(quantifier_parts[0]) if quantifier_parts[0] else 0
            max = int(quantifier_parts[1]) if len(quantifier_parts) > 1 and quantifier_parts[1] else None
            return SpecificQuantifierNode(unit, min, max)
        else:
            return unit  # Return the unit itself if no quantifier is present

    def __parse_char_range(self) -> list[RangeNode]:
        char_range = []
        while not self.tokenizer.match(TokenType.CLASS_END):
            start = self.__parse_char()
            if self.tokenizer.match(TokenType.RANGE):
                end = self.__parse_char()
                char_range.append(RangeNode(start, end))
            else:
                char_range.append(RangeNode(start, start))
        return char_range

    def __parse_char(self) -> str:
        if self.tokenizer.match(TokenType.ESCAPED):
            return self.tokenizer.previous.value
        elif self.tokenizer.match(TokenType.LITERAL):
            return self.tokenizer.previous.value
        elif self.tokenizer.match(TokenType.WILDCARD):
            return RangeNode.WILDCARD
        else:
            raise Exception(f"Unexpected token {self.tokenizer.current}")
        
if __name__ == '__main__':
    test_cases = [
        {
            "pattern": "(ab)*",
            "expected_ast": ZeroOrMoreNode(
                GroupNode(
                    ConcatenationNode([
                        LiteralNode('a'),
                        LiteralNode('b')
                    ])
                )
            )
        },
        {
            "pattern": "[a-z]+",
            "expected_ast": OneOrMoreNode(
                ClassNode([
                    RangeNode('a', 'z')
                ])
            )
        },
        {
            "pattern": "a?b+c*",
            "expected_ast": ConcatenationNode([
                ZeroOrOneNode(LiteralNode('a')),
                OneOrMoreNode(LiteralNode('b')),
                ZeroOrMoreNode(LiteralNode('c'))
            ])
        },
        {
            "pattern": "(a|b)c",
            "expected_ast": ConcatenationNode([
                GroupNode(
                    AlternationNode([
                        LiteralNode('a'),
                        LiteralNode('b')
                    ])
                ),
                LiteralNode('c')
            ])
        },
        {
            "pattern": "\\d{2,4}",
            "expected_ast": SpecificQuantifierNode(
                EscapedCharacterNode('d'), 2, 4
            )
        },
        # Add more test cases as needed
    ]

    for test_case in test_cases:
        pattern = test_case["pattern"]
        expected_ast = test_case["expected_ast"]
        actual_ast = ASTParser(pattern).parse()

        assert str(actual_ast) == str(expected_ast), f"Test failed for pattern '{pattern}'. Expected {expected_ast}, but got {actual_ast}"
        
        print(f"Test passed for pattern '{pattern}'.")
