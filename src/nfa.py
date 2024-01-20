from collections import defaultdict
from src.ast import ASTNode, ASTParser, AlternationNode, ConcatenationNode, LiteralNode, RangeNode, ClassNode, ZeroOrMoreNode, OneOrMoreNode, ZeroOrOneNode, SpecificQuantifierNode, GroupNode, EscapedCharacterNode
from src.test import REGEX_TEST_CASES, test_regex


class NFAState:
    def __init__(self) -> None:
        self.transitions: dict[str, set[NFAState]] = defaultdict(set)
        self.epsilon_transitions: set[NFAState] = set()
        self.is_final: bool = False

    def _add_transition(self, char: str, state: "NFAState") -> None:
        self.transitions[char].add(state)

    def _add_epsilon_transition(self, state: "NFAState") -> None:
        self.epsilon_transitions.add(state)
        
    def match(self, string: str) -> bool:
        def dfs(state: NFAState, position: int) -> bool:
            if position == len(string):
                return state.is_final or any(dfs(next_state, position) for next_state in state.epsilon_transitions)

            # Epsilon transitions
            if any(dfs(next_state, position) for next_state in state.epsilon_transitions):
                return True

            # Regular transitions
            if any(dfs(next_state, position + 1) for next_state in state.transitions[string[position]]):
                return True

            return False

        return dfs(self, 0)

    def to_dot(self) -> str:
        dot_graph = "digraph NFA {\n"
        dot_graph += "    rankdir=LR;\n"
        dot_graph += "    node [shape = circle];\n"

        # Traversal
        visited = set()
        def dfs(state: NFAState):
            nonlocal dot_graph
            
            if state in visited:
                return
            visited.add(state)

            if state.is_final:
                dot_graph += f"    {id(state)} [shape=doublecircle];\n"

            for char, states in state.transitions.items():
                for next_state in states:
                    dot_graph += f"    {id(state)} -> {id(next_state)} [label=\"{char}\"];\n"
                    dfs(next_state)

            for next_state in state.epsilon_transitions:
                dot_graph += f"    {id(state)} -> {id(next_state)} [label=\"ε\"];\n"
                dfs(next_state)

        dfs(self)
        
        dot_graph += "    start -> " + str(id(self)) + ";\n"
        dot_graph += "}"

        return dot_graph

    
def __convert_node(node: ASTNode, start_state: NFAState) -> NFAState:
    if isinstance(node, LiteralNode):
        return __convert_literal_node(node, start_state)
    elif isinstance(node, ConcatenationNode):
        return __convert_concatenation_node(node, start_state)
    elif isinstance(node, AlternationNode):
        return __convert_alternation_node(node, start_state)
    elif isinstance(node, RangeNode):
        return __convert_range_node(node, start_state)
    elif isinstance(node, ClassNode):
        return __convert_class_node(node, start_state)
    elif isinstance(node, ZeroOrMoreNode):
        return __convert_zero_or_more_node(node, start_state)
    elif isinstance(node, OneOrMoreNode):
        return __convert_one_or_more_node(node, start_state)
    elif isinstance(node, ZeroOrOneNode):
        return __convert_zero_or_one_node(node, start_state)
    elif isinstance(node, SpecificQuantifierNode):
        return __convert_specific_quantifier_node(node, start_state)
    elif isinstance(node, GroupNode):
        return __convert_group_node(node, start_state)
    elif isinstance(node, EscapedCharacterNode):
        return __convert_escaped_character_node(node, start_state)
    else:
        raise Exception(f"Unknown node type: {node}")

def __convert_literal_node(node: LiteralNode, start_state: NFAState) -> NFAState:
    end_state = NFAState()
    start_state._add_transition(node.value, end_state)
    return end_state

def __convert_concatenation_node(node: ConcatenationNode, start_state: NFAState) -> NFAState:
    current_state = start_state
    for subnode in node.nodes:
        current_state = __convert_node(subnode, current_state)
    return current_state

def __convert_alternation_node(node: AlternationNode, start_state: NFAState) -> NFAState:
    end_state = NFAState()
    for subnode in node.nodes:
        branch_state = __convert_node(subnode, start_state)
        branch_state._add_epsilon_transition(end_state)
    return end_state

def __convert_range_node(node: RangeNode, start_state: NFAState) -> NFAState:	
    end_state = NFAState()
    start, end = node.start, node.end
    if start == RangeNode.WILDCARD and end == RangeNode.WILDCARD:
        for char in range(256):
            start_state._add_transition(chr(char), end_state)
    else:
        for char in range(ord(start), ord(end) + 1):
            start_state._add_transition(chr(char), end_state)
    return end_state

def __convert_class_node(node: ClassNode, start_state: NFAState) -> NFAState:
    end_state = NFAState()
    for range_node in node.ranges:
        __convert_range_node(range_node, start_state)._add_epsilon_transition(end_state)
    return end_state

def __convert_zero_or_more_node(node: ZeroOrMoreNode, start_state: NFAState) -> NFAState:
    loop_state = NFAState()
    end_state = NFAState()
    start_state._add_epsilon_transition(loop_state)
    loop_state._add_epsilon_transition(end_state)
    __convert_node(node.node, loop_state)._add_epsilon_transition(loop_state)
    return end_state

def __convert_one_or_more_node(node: OneOrMoreNode, start_state: NFAState) -> NFAState:
    repeat_state = NFAState()
    start_state._add_epsilon_transition(repeat_state)
    end_state = __convert_node(node.node, repeat_state)

    # Ensure loop back for one or more occurrences
    end_state._add_epsilon_transition(repeat_state)

    # Final state to mark the acceptance of the input
    final_state = NFAState()
    end_state._add_epsilon_transition(final_state)
    return final_state

def __convert_specific_quantifier_node(node: SpecificQuantifierNode, start_state: NFAState) -> NFAState:
    if node.max != None and node.min > node.max:
        raise Exception("SpecificQuantifierNode min must be less than or equal to max")
    
    # Create the required 'min' repetitions
    current_state = start_state
    for _ in range(node.min):
        current_state = __convert_node(node.node, current_state)

    end_state = NFAState()

    if node.max == None:
        optional_state = current_state
        optional_state._add_epsilon_transition(end_state)  # Optional jump to the end
        optional_state = __convert_node(node.node, optional_state)
        optional_state._add_epsilon_transition(end_state)
    else:
        # For the remaining up to 'max - min', create optional states
        optional_state = current_state
        for _ in range(node.max - node.min):
            optional_state._add_epsilon_transition(end_state)  # Optional jump to the end
            optional_state = __convert_node(node.node, optional_state)  # Next repetition

        optional_state._add_epsilon_transition(end_state)  # Connect the last optional state to the end

    return end_state

def __convert_group_node(node: GroupNode, start_state: NFAState) -> NFAState:
    return __convert_node(node.node, start_state)

def __convert_zero_or_one_node(node: ZeroOrOneNode, start_state: NFAState) -> NFAState:
    end_state = NFAState()
    start_state._add_epsilon_transition(end_state)
    __convert_node(node.node, start_state)._add_epsilon_transition(end_state)
    return end_state

def __convert_escaped_character_node(node: EscapedCharacterNode, start_state: NFAState) -> NFAState:
    end_state = NFAState()

    if node.value == 'd':  # Digit shorthand
        for char in '0123456789':
            start_state._add_transition(char, end_state)
    elif node.value == 'w':  # Word character shorthand
        for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_':
            start_state._add_transition(char, end_state)
    elif node.value == 's':  # Whitespace shorthand
        for char in ' \t\n\r\f\v':
            start_state._add_transition(char, end_state)
    else:
        start_state._add_transition(node.value, end_state)

    return end_state

def ast_to_nfa(ast: ASTNode) -> NFAState:
    start_state = NFAState()
    end_state = __convert_node(ast, start_state)
    end_state.is_final = True
    return start_state

if __name__ == '__main__':
    def parse(pattern: str) -> NFAState:
        return ast_to_nfa(ASTParser(pattern).parse())
    
    def match(compiled: NFAState, string: str) -> bool:
        return compiled.match(string)
    
    def log(pattern: str, compiled: NFAState) -> None:
        print(f"Pattern '{pattern}' compiled to NFA:\n{compiled.to_dot()}")

    test_regex(parse, match, log)
        