import subprocess
import sys
from pathlib import Path

import pytest

from main import (
    KEYWORDS, tokenize, main, LexicalError, is_digit,  is_identifier_start, 
    is_identifier_part, skip_whitespace, skip_comment, read_identifier,
    read_number,  read_string, read_operator_or_separator
)



@pytest.mark.parametrize(
    "source, expected_values",
    [
        ("5",True),
        ("1.0", False)
    ],
)
def test_is_digit(source, expected_values):
    
    assert is_digit(source) == expected_values
    

@pytest.mark.parametrize(
    "source, expected_values",
    [
        ("a",True),
        ("_", True),
        ("1", False)
    ],
)
def test_is_identifier_start(source, expected_values):
    
    assert is_identifier_start(source) == expected_values


@pytest.mark.parametrize(
    "source, expected_values",
    [
        ("a",True),
        ("_", True),
        ("1", True),
        ("@", False),
        ("1.0", False)
    ],
)
def test_is_identifier_part(source, expected_values):
    assert is_identifier_part(source) == expected_values


@pytest.mark.parametrize(
    "source, expected_values",
    [
        (("\n abc", 0, 1, 1),(2,2,2)),
        (("abc", 0, 1, 1,), (0, 1, 1))
        
    ],
)
def test_skip_whitespace(source, expected_values):
    assert skip_whitespace(*source) == expected_values



def test_unexpected_character():
    with pytest.raises(LexicalError) as excinfo:
        tokenize("a @ b", "input.txt")

    assert str(excinfo.value) == "input.txt:1:3: lexical: unexpected character '@'"



@pytest.mark.parametrize(
    "source, expected_values",
    [
        (("# comment\nrest", 0, 1), (9, 10)),
        (("#abc", 0, 5), (4, 9)),
        (("#", 0, 1), (1, 2)),
    ],
)
def test_skip_comment(source, expected_values):
    assert skip_comment(*source) == expected_values


@pytest.mark.parametrize(
    "source, expected_values",
    [
        ("abc", (("IDENT", "abc"), 3)),
        ("if", (("KEYWORD", "if"), 2)),
        ("_x1 ", (("IDENT", "_x1"), 3)),
        ("x1 + y", (("IDENT", "x1"), 2)),
    ],
)
def test_read_identifier(source, expected_values):
    assert read_identifier(source, 0) == expected_values


@pytest.mark.parametrize(
    "source, expected_values",
    [
        (("123", 0, "input.txt", 1, 1), (("INT", "123"), 3)),
        (("0", 0, "input.txt", 1, 1), (("INT", "0"), 1)),
        (("12.5", 0, "input.txt", 1, 1), (("FLOAT", "12.5"), 4)),
        (("12.", 0, "input.txt", 1, 1), (("INT", "12"), 2))
    ],
)
def test_read_number(source, expected_values):
    assert read_number(*source) == expected_values


@pytest.mark.parametrize(
    "source, expected_message",
    [
        (
            ("12abc", 0, "input.txt", 1, 1),
            "input.txt:1:1: lexical: invalid number literal '12abc'",
        ),
        (
            ("1.2x", 0, "input.txt", 2, 4),
            "input.txt:2:4: lexical: invalid number literal '1.2x'",
        ),
    ],
)
def test_read_number_invalid_literal(source, expected_message):
    with pytest.raises(LexicalError) as excinfo:
        read_number(*source)

    assert str(excinfo.value) == expected_message


@pytest.mark.parametrize(
    "source, expected_values",
    [
        (('"hello"', 0, "input.txt", 1, 1), (("STRING", "hello"), 7)),
        (('""', 0, "input.txt", 1, 1), (("STRING", ""), 2)),
        (('"hi" + x', 0, "input.txt", 1, 1), (("STRING", "hi"), 4)),
    ],
)
def test_read_string(source, expected_values):
    assert read_string(*source) == expected_values


@pytest.mark.parametrize(
    "source",
    [
        ('"abc', 0, "input.txt", 1, 1),
        ('"abc\nnext', 0, "input.txt", 1, 1),
    ],
)
def test_read_string_unterminated(source):
    with pytest.raises(LexicalError) as excinfo:
        read_string(*source)

    assert str(excinfo.value) == "input.txt:1:1: lexical: unterminated string literal"


@pytest.mark.parametrize(
    "source, expected_values",
    [
        ("==", (("OP", "=="), 2)),
        ("<=", (("OP", "<="), 2)),
        (">=", (("OP", ">="), 2)),
        ("=", (("OP", "="), 1)),
        ("<", (("OP", "<"), 1)),
        ("(", (("SEP", "("), 1)),
        (",", (("SEP", ","), 1)),
    ],
)
def test_read_operator_or_separator(source, expected_values):
    assert read_operator_or_separator(source, 0) == expected_values


@pytest.mark.parametrize(
    "source, expected_tokens",
    [
        (
            "if x == 1",
            [
                ("KEYWORD", "if", 1, 1),
                ("IDENT", "x", 1, 4),
                ("OP", "==", 1, 6),
                ("INT", "1", 1, 9),
            ],
        ),
        (
            "x = 3.14;",
            [
                ("IDENT", "x", 1, 1),
                ("OP", "=", 1, 3),
                ("FLOAT", "3.14", 1, 5),
                ("SEP", ";", 1, 9),
            ],
        ),
        (
            'print("hi")',
            [
                ("IDENT", "print", 1, 1),
                ("SEP", "(", 1, 6),
                ("STRING", "hi", 1, 7),
                ("SEP", ")", 1, 11),
            ],
        ),
        (
            "a # comment\nb",
            [
                ("IDENT", "a", 1, 1),
                ("IDENT", "b", 2, 1),
            ],
        ),
        (
            "a\nb\n  c",
            [
                ("IDENT", "a", 1, 1),
                ("IDENT", "b", 2, 1),
                ("IDENT", "c", 3, 3),
            ],
        ),
        ("", []),
    ],
)
def test_tokenize_sources(source, expected_tokens):
    assert tokenize(source, "input.txt") == expected_tokens




