
REGEX_TEST_CASES = [
    {
        "pattern": "a",
        "matching": ["a"],
        "not_matching": ["", "b", "aa"]
    },
    {
        "pattern": "(ab)*",
        "matching": ["", "ab", "abab", "ababab"],
        "not_matching": ["a", "b", "aba", "abb"]
    },
    {
        "pattern": "[a-z]+",
        "matching": ["a", "abc", "xyz"],
        "not_matching": ["", "1", "A", "9", "!"]
    },
    {
        "pattern": "a?b+c*",
        "matching": ["b", "ab", "bc", "abc", "abcc", "bcc"],
        "not_matching": ["", "a", "c", "ac", "ba"]
    },
    {
        "pattern": "(a|b)c",
        "matching": ["ac", "bc"],
        "not_matching": ["", "a", "b", "ab", "cc", "acb"]
    },
    {
        "pattern": "\\d{2,4}",
        "matching": ["12", "123", "1234"],
        "not_matching": ["", "1", "12345", "abc", "12a"]
    },
    {
        "pattern": "(foo)+|bar",
        "matching": ["foo", "foofoo", "bar"],
        "not_matching": ["", "f", "fo", "foobar", "foo bar"]
    },
    {
        "pattern": "\\w\\d?",
        "matching": ["a", "a1", "b2", "c"],
        "not_matching": ["", "ab", "123", "!"]
    },
    {
        "pattern": "(a[bc]*d)+",
        "matching": ["abd", "abcd", "abbd", "abcbd", "adabd"],
        "not_matching": ["", "abc", "abdab", "abdcd"]
    },
    {
        "pattern": "a(b(c|d))*",
        "matching": ["a", "abc", "abcbd", "abdbd"],
        "not_matching": ["", "ab", "acd", "abce"]
    },
        {
        "pattern": "a(bc|de)f",
        "matching": ["abcf", "adef"],
        "not_matching": ["abf", "aef", "abcdef", "abdef"]
    },
    {
        "pattern": "a[0-9]*b",
        "matching": ["ab", "a123b", "a0b", "a56789b"],
        "not_matching": ["a", "b", "abc", "a123"]
    },
    # {
    #     "pattern": "^[a-zA-Z]+\\d?$",
    #     "matching": ["abc", "Z4", "xyz3", "A"],
    #     "not_matching": ["1a", "abc10", "XYZ "]
    # },
    {
        "pattern": "foo(bar|baz)*qux",
        "matching": ["fooqux", "foobarqux", "foobazqux", "foobarbazbarqux"],
        "not_matching": ["foo", "foobar", "qux", "foobarbaz"]
    },
    {
        "pattern": ".+@.+\\..+",
        "matching": ["test@example.com", "name@domain.co", "user123@host.org"],
        "not_matching": ["@example.com", "test@.com", "example.com"]
    },
    {
        "pattern": "(\\d{4}-\\d{2}-\\d{2})",
        "matching": ["2023-01-01", "1999-12-31"],
        "not_matching": ["01-01-2023", "2023/01/01", "2023-1-1", "2023-01-1", "2023-1-01"]
    },
    {
        "pattern": "[a-zA-Z0-9]+",
        "matching": ["abc", "ABC", "123", "abc123", "ABC123", "abcABC123"],
        "not_matching": ["", "abc ", "abc!"]
    },
    # {
    #     "pattern": "^\\s*#.*",
    #     "matching": ["# Comment", "   # Another comment"],
    #     "not_matching": ["No comment", " #Not a comment"]
    # },
    {
        "pattern": "a(b|c)?d+e{2,3}",
        "matching": ["adee", "abdddee", "acddee", "addddeee"],
        "not_matching": ["ade", "adde", "abde", "abdddeeee"]
    },
    # Add more test cases as needed
]

def test_regex(parse, match, log) -> None:
    for case in REGEX_TEST_CASES[:9]:
        pattern = case["pattern"]
        print(f"Testing pattern '{pattern}'")

        compiled = parse(pattern)
        log(pattern, compiled)

        for string in case["matching"]:
            assert match(compiled, string), f"String '{string}' should match pattern '{pattern}' but doesn't."

        for string in case["not_matching"]:
            assert not match(compiled, string), f"String '{string}' should not match pattern '{pattern}' but does."

        print(f"All tests passed for pattern '{pattern}'.")
        