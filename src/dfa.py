from src.nfa import NFAState, ast_to_nfa
from src.ast import ASTParser
from src.test import test_regex


class DFAState:
    def __init__(self, nfa_states: set[NFAState] | frozenset[NFAState]) -> None:
        self.nfa_states = frozenset(nfa_states)  # Immutable set for hashing
        self.transitions: dict[str, DFAState] = {}
        self.is_final: bool = any(state.is_final for state in nfa_states)

    def _add_transition(self, char: str, state: "DFAState") -> None:
        self.transitions[char] = state

    def match(self, string: str) -> bool:
        current_state = self

        for char in string:
            if char in current_state.transitions:
                current_state = current_state.transitions[char]
            else:
                # If there is no transition for this character, the string does not match
                return False

        # After processing all characters, check if we are in a final state
        return current_state.is_final
    
    def get_all_states(self) -> set["DFAState"]:
        visited = set()

        def visit(state: DFAState) -> None:
            if state not in visited:
                visited.add(state)
                for next_state in state.transitions.values():
                    visit(next_state)

        visit(self)
        return visited
        
    def to_dot(self) -> str:
        all_states = self.get_all_states()
        
        final_states = [state for state in all_states if state.is_final]
        final_states_str = ' '.join(f'S{hash(state)}' for state in final_states)
        
        dot_str = 'digraph DFA {\n'
        dot_str += f'    rankdir=LR;\n'
        dot_str += f'    size="8,5"\n'
        dot_str += f'    node [shape = doublecircle]; {final_states_str};\n'
        dot_str += f'    node [shape = circle];\n'
        dot_str += f'    start -> S{hash(self)};\n'
        
        for state in all_states:
            for char, next_state in state.transitions.items():
                dot_str += f'    S{hash(state)} -> S{hash(next_state)} [ label="{char}" ];\n'
        
        dot_str += '}\n'
        
        return dot_str

    def __hash__(self) -> int:
        h = hash(tuple(sorted(id(state) for state in self.nfa_states)))
        return h if h >= 0 else -h

    def __eq__(self, other: "DFAState") -> bool:
        return self.nfa_states == other.nfa_states


def __epsilon_closure(nfa_state: NFAState, visited: set[NFAState] | None = None) -> set[NFAState]:
    if visited is None:
        visited = set()

    closure = {nfa_state}

    if nfa_state in visited:
        return closure

    visited.add(nfa_state)
    closure.update(__epsilon_closure_set(nfa_state.epsilon_transitions, visited))

    return closure

def __epsilon_closure_set(nfa_states: set[NFAState], visited: set[NFAState]) -> set[NFAState]:
    closure = set()
    for nfa_state in nfa_states:
        closure.update(__epsilon_closure(nfa_state, visited))
    return closure

def nfa_to_dfa(start_nfa_state: NFAState) -> DFAState:
    start_dfa_state = DFAState(__epsilon_closure(start_nfa_state))
    unmarked_states = [start_dfa_state]

    dfa_state_mapping = {frozenset(__epsilon_closure(start_nfa_state)): start_dfa_state}

    while unmarked_states:
        current_dfa_state = unmarked_states.pop()

        for char in set().union(*(state.transitions for state in current_dfa_state.nfa_states)):
            if char:
                next_nfa_states: set[NFAState] = set()
                for nfa_state in current_dfa_state.nfa_states:
                    next_nfa_states.update(nfa_state.transitions[char])

                next_nfa_states_closure = __epsilon_closure_set(next_nfa_states, set())
                frozen_next_nfa_states_closure = frozenset(next_nfa_states_closure)

                if frozen_next_nfa_states_closure in dfa_state_mapping:
                    # Reuse existing DFA state
                    next_dfa_state = dfa_state_mapping[frozen_next_nfa_states_closure]
                else:
                    # Create new DFA state
                    next_dfa_state = DFAState(next_nfa_states_closure)
                    unmarked_states.append(next_dfa_state)
                    dfa_state_mapping[frozen_next_nfa_states_closure] = next_dfa_state

                current_dfa_state._add_transition(char, next_dfa_state)

    return start_dfa_state

def compile(pattern: str) -> DFAState:
    return nfa_to_dfa(ast_to_nfa(ASTParser(pattern).parse()))

if __name__ == '__main__':
    def parse(pattern: str) -> DFAState:
        return compile(pattern)
    
    def match(compiled: DFAState, string: str) -> bool:
        return compiled.match(string)
        
    def log(pattern: str, compiled: DFAState) -> None:
        # print(f"Pattern '{pattern}' compiled to NFA:\n{compiled}")
        print(compiled.to_dot())
        pass
    
    test_regex(parse, match, log)
        