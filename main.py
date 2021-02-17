def match(regex: str, string: str) -> (bool, str):
    return True, string + regex


def main():
    regex = 'abc'
    string = 'abc'

    does_match, match_string = match(regex, string)

    print(match_string, does_match)


if __name__ == '__main__':
    main()
