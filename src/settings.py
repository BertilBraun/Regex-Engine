"""
    Settings for the regex definition
"""


def get_alphabet() -> str:
    return '()[]|.*+?\\'


def is_star(char: chr) -> bool:
    return char == '*'


def is_question(char: chr) -> bool:
    return char == '?'


def is_plus(char: chr) -> bool:
    return char == '+'


def is_dot(char: chr) -> bool:
    return char == '.'


def is_start(char: chr) -> bool:
    return char == '^'


def is_end(char: chr) -> bool:
    return char == '$'


def is_operator(char: chr) -> bool:
    return is_plus(char) or is_question(char) or is_star(char)


def is_alternate_open(char: chr) -> bool:
    return char == '('


def is_alternate_close(char: chr) -> bool:
    return char == ')'


def is_set_open(char: chr) -> bool:
    return char == '['


def is_set_close(char: chr) -> bool:
    return char == ']'


def is_escape(char: chr) -> bool:
    return char == '\\'


def is_literal(char: chr) -> bool:
    return char not in get_alphabet()


def is_unit(term: str) -> bool:
    return is_literal(term[0]) or is_dot(term[0]) or is_set(term) or is_escape_sequence(term)


def is_set(term: str) -> bool:
    return is_set_open(term[0]) and is_set_close(term[-1])


def is_alternate(term: str) -> bool:
    return is_alternate_open(term[0]) and is_alternate_close(term[-1])


def is_escape_sequence(term: str) -> bool:
    return is_escape(term[0])

