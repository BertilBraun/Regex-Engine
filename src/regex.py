"""
    The regex Implementation
"""

from settings import *


def split_set(head: str) -> list:
    tokens = list(head[1:-1])
    out_tokens = []

    i = 0
    while i <= len(tokens) - 2:
        if tokens[i + 1] == '-':
            for j in range(ord(tokens[i]), ord(tokens[i + 2]) + 1):
                out_tokens.append(chr(j))
            i += 3
        else:
            out_tokens.append(tokens[i])
            i += 1

    out_tokens.append(tokens[-1])
    return out_tokens


def split_alternate(head: str) -> list:
    return head[1:-1].split('|')


def split_expr(expr: str) -> (str, chr, str):
    operator = None

    if is_set_open(expr[0]):
        last_expr_pos = expr.find(']') + 1
        if last_expr_pos == 0:
            raise Exception("Invalid Class block! couldn't find ']'!")
        head = expr[:last_expr_pos]
    elif is_alternate_open(expr[0]):
        last_expr_pos = expr.find(')') + 1
        if last_expr_pos == 0:
            raise Exception("Invalid Set block! couldn't find ')'!")
        head = expr[:last_expr_pos]
    elif is_escape(expr[0]):
        last_expr_pos = 2
        head = expr[:2]
    else:
        last_expr_pos = 1
        head = expr[0]

    if last_expr_pos < len(expr) and is_operator(expr[last_expr_pos]):
        operator = expr[last_expr_pos]
        last_expr_pos += 1

    rest = expr[last_expr_pos:]

    return head, operator, rest


def does_unit_match(expr: str, string: str) -> bool:
    head, operator, rest = split_expr(expr)

    if is_literal(head[0]):
        return expr[0] == string[0]
    elif is_dot(head[0]):
        return True
    elif is_escape_sequence(head):
        if head == '\\a':
            return string[0].isalpha()
        elif head == '\\d':
            return string[0].isdigit()
        else:
            raise Exception(f"Invalid Escape Sequence! couldn't process '{head}'!")
    elif is_set(head):
        tokens = split_set(head)
        return string[0] in tokens

    return False


def match_multiple(expr: str, string: str, match_length: int, min_match_length: int, max_match_length) -> (bool, int):
    head, operator, rest = split_expr(expr)
    submatch_length = -1

    while not max_match_length or submatch_length < max_match_length:
        submatch_matched, _ = match_expr((head * (submatch_length + 1)), string, match_length)
        if submatch_matched:
            submatch_length += 1
        else:
            break

    while submatch_length >= min_match_length:
        matched, length = match_expr((head * submatch_length) + rest, string, match_length)
        if matched:
            return True, length
        submatch_length -= 1

    return False, 0


def match_star(expr: str, string: str, match_length: int) -> (bool, int):
    return match_multiple(expr, string, match_length, 0, None)


def match_question(expr: str, string: str, match_length: int) -> (bool, int):
    return match_multiple(expr, string, match_length, 0, 1)


def match_plus(expr: str, string: str, match_length: int) -> (bool, int):
    return match_multiple(expr, string, match_length, 1, None)


def match_alternate(expr: str, string: str, match_length: int) -> (bool, int):
    head, operator, rest = split_expr(expr)

    options = split_alternate(head)

    for option in options:
        matched, length = match_expr(option + rest, string, match_length)
        if matched:
            return True, length

    return False, 0


def match_expr(expr: str, string: str, match_length: int = 0) -> (bool, int):
    if len(expr) == 0:
        return True, match_length
    elif is_end(expr[0]):
        return not len(string), match_length if not len(string) else 0
    if len(string) == 0:
        return False, 0

    head, operator, rest = split_expr(expr)

    if is_star(operator):
        return match_star(expr, string, match_length)
    elif is_question(operator):
        return match_question(expr, string, match_length)
    elif is_plus(operator):
        return match_plus(expr, string, match_length)
    elif is_alternate(head):
        return match_alternate(expr, string, match_length)
    elif is_unit(head):
        if does_unit_match(head, string):
            return match_expr(rest, string[1:], match_length + 1)
    else:
        raise Exception(f"Unknown token '{head}'!")

    return False, 0


def match(regex: str, string: str) -> (bool, str):
    match_pos = -1

    if is_start(regex[0]):
        max_match_pos = 0
        regex = regex[1:]
    else:
        max_match_pos = len(string)

    try:
        while match_pos < max_match_pos:
            match_pos += 1
            matched, match_length = match_expr(regex, string[match_pos:])
            if matched:
                return matched, string[match_pos:match_pos + match_length]

    except Exception as e:
        print('Invalid Regex:', str(e))
        return False, ''

    return False, ''
