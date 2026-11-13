
import sys

KEYWORDS = {"if", "else", "while", "return", "for", "def"}
OPERATORS = {"+", "-", "*", "/", "=", "<", ">", "==", "<=", ">="}
SEPARATORS = {"(", ")", "{", "}", ",", ";"}
WHITESPACE = (" \t\r\n\f\v")

TWO_CHAR_OPERATORS = {"==", "<=", ">="}


class LexicalError(ValueError):
    
    def __init__(self, filename, line, column, message):
        self.filename = filename
        self.line = line
        self.column = column
        self.message = message
        super().__init__(
            f"{filename}:{line}:{column}: lexical: {message}"
        )


def is_digit(char):
    return char.isascii() and char.isdigit()


def is_identifier_start(char):
    return char == "_" or (char.isascii() and char.isalpha())


def is_identifier_part(char):
    return char == "_" or (char.isascii() and char.isalnum())


def skip_whitespace(source, i, line, column):
    
    while i < len(source) and source[i] in WHITESPACE:
        if source[i] == "\n":
            line += 1
            column = 1
        else:
            column += 1
        i += 1
    return i, line, column


def skip_comment(source, i, column):
    
    while i < len(source) and source[i] != "\n":
        i += 1
        column += 1
    return i, column


def read_identifier(source, i):
    
    start = i
    while i < len(source) and is_identifier_part(source[i]):
        i += 1

    value = source[start:i]
    token_type = "KEYWORD" if value in KEYWORDS else "IDENT"
    return (token_type, value), i


def read_number(source, i, filename, line, column):
    
    start = i
    while i < len(source) and is_digit(source[i]):
        i += 1

    token_type = "INT"
    if i + 1 < len(source) and source[i] == "." and is_digit(source[i + 1]):
        token_type = "FLOAT"
        i += 1
        while i < len(source) and is_digit(source[i]):
            i += 1

    if i < len(source) and is_identifier_part(source[i]):
        end = i
        while end < len(source) and is_identifier_part(source[end]):
            end += 1
        raise LexicalError(
            filename, line, column,
            f"invalid number literal {source[start:end]!r}",
        )

    return (token_type, source[start:i]), i


def read_string(source, i, filename, line, column):
    
    start = i + 1
    i += 1
    while i < len(source) and source[i] != '"' and source[i] != "\n":
        i += 1

    if i >= len(source) or source[i] != '"':
        raise LexicalError(
            filename, line, column, "unterminated string literal"
        )

    return ("STRING", source[start:i]), i + 1


def read_operator_or_separator(source, i):
    
    pair = source[i:i + 2]
    if pair in TWO_CHAR_OPERATORS:
        return ("OP", pair), i + 2

    char = source[i]
    if char in OPERATORS:
        return ("OP", char), i + 1
    return ("SEP", char), i + 1


def tokenize(source, filename):
   
    tokens = []
    i = 0
    line = 1
    column = 1

    while i < len(source):
        char = source[i]

        if char in WHITESPACE:
            i, line, column = skip_whitespace(source, i, line, column)
            continue

        if char == "#":
            i, column = skip_comment(source, i, column)
            continue

        start = i
        token_line = line
        token_column = column

        if char == '"':
            (token_type, value), i = read_string(
                source, i, filename, token_line, token_column
            )
        elif is_digit(char):
            (token_type, value), i = read_number(
                source, i, filename, token_line, token_column
            )
        elif is_identifier_start(char):
            (token_type, value), i = read_identifier(source, i)
        elif char in OPERATORS or char in SEPARATORS:
            (token_type, value), i = read_operator_or_separator(source, i)
        else:
            raise LexicalError(
                filename, token_line, token_column,
                f"unexpected character {char!r}",
            )

        column += i - start
        tokens.append((token_type, value, token_line, token_column))

    return tokens


def main(argv):
    if len(argv) != 2:
        print("usage: python3 main.py <file>", file=sys.stderr)
        return 2

    filename = argv[1]

    
    with open(filename, encoding="utf-8") as file:
            source = file.read()
    

    try:
        tokens = tokenize(source, filename)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    for token_type, value, token_line, token_column in tokens:
        print(f"({token_type}, {value}, {token_line}:{token_column})")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
