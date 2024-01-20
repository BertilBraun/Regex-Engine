"""
    A regex Test and the main file
"""

from regex import match


def main():
    regex = '([a-zABC]| )+'
    string = 'abz ABC'

    does_match, match_string = match(regex, string)

    print(match_string, '->', does_match)


if __name__ == '__main__':
    main()
