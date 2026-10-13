import runpy
import subprocess
import sys
from unittest.mock import patch
import pytest
from main import (
    solution, apply_binary, apply_tilde,
    add, sub, mul, div, operators,
)


@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (2.5, 0.5, 3.0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (5, 3, 2),
    (3, 5, -2),
    (0, 0, 0),
    (-1, -1, 0),
])
def test_sub(a, b, expected):
    assert sub(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (4, 3, 12),
    (-2, 3, -6),
    (0, 5, 0),
    (1.5, 2, 3.0),
])
def test_mul(a, b, expected):
    assert mul(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5),
    (1, 4, 0.25),
    (-6, 3, -2),
    (5, 2, 2.5),
])
def test_div(a, b, expected):
    assert div(a, b) == expected


def test_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        div(1, 0)


@pytest.mark.parametrize("op, stack_in, expected", [
    (add, [2, 3], [5]),
    (sub, [10, 3], [7]),
    (mul, [3, 4], [12]),
    (div, [10, 2], [5]),
    (div, [1, 4], [0.25]),
])
def test_apply_binary(op, stack_in, expected):
    s = list(stack_in)
    apply_binary(s, op)
    assert s == expected


def test_apply_binary_div_by_zero():
    s = [1, 0]
    with pytest.raises(ZeroDivisionError):
        apply_binary(s, div)



@pytest.mark.parametrize("stack_in, expected", [
    ([0, 5], [25]),
    ([5, 0], [25]),
    ([0, 0], [0]),
    ([3, 5], [2]),
    ([5, 3], [2]),
    ([-3, -5], [2]),
    ([2.5, 0.5], [2.0]),
    ([1, 0, 0], [1]),
    ([0, 1, 0], [1]),
])
def test_apply_tilde(stack_in, expected):
    s = list(stack_in)
    apply_tilde(s)
    assert s == expected


def test_apply_tilde_insufficient_stack():
    with pytest.raises(ValueError, match="at least 2"):
        apply_tilde([5])


def test_apply_tilde_empty_stack():
    with pytest.raises(ValueError, match="at least 2"):
        apply_tilde([])


@pytest.mark.parametrize("tokens, expected", [
    (["2", "3", "+"], 5.0),
    (["5", "3", "-"], 2.0),
    (["4", "3", "*"], 12.0),
    (["10", "2", "/"], 5.0),
    (["2", "3", "+", "4", "*"], 20.0),
    (["5"], 5.0),
    (["2", "3", "~"], 1.0),
    (["3", "5", "~", "2", "*"], 4.0),
    (["2.5", "0.5", "+"], 3.0),
    (["-1", "1", "+"], 0.0),
    (["10", "5", "0", "~"], 225.0),
    (["1", "2", "3", "+", "*"], 5.0),
])
def test_solution(tokens, expected):
    result = solution(tokens)
    assert result == expected


def test_solution_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        solution(["1", "0", "/"])


@pytest.mark.parametrize("args, expected_output", [
    (["2", "3", "+"], "2 3 + = 5.0"),
    (["10", "2", "/"], "10 2 / = 5.0"),
    (["4", "3", "*"], "4 3 * = 12.0"),
    (["2", "~"], None),
])
def test_cli(args, expected_output):
    proc = subprocess.run(
        [sys.executable, "main.py"] + args,
        capture_output=True, text=True
    )
    if expected_output is not None:
        assert expected_output in proc.stdout


def test_cli_combined_expression():
    proc = subprocess.run(
        [sys.executable, "main.py", "2", "3", "+", "4", "*"],
        capture_output=True, text=True
    )
    assert "2 3 + 4 * = 20.0" in proc.stdout


def test_cli_invalid_number():
    proc = subprocess.run(
        [sys.executable, "main.py", "abc"],
        capture_output=True, text=True
    )
    assert proc.returncode != 0


def test_cli_args_coverage():
    with patch.object(sys, "argv", ["main.py", "2", "3", "+"]):
        runpy.run_path("main.py", run_name="__main__")


def test_div_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError, match="You cannot divide by zero."):
        div(1, 0)


def test_solution_empty_expression():
    with pytest.raises(ValueError, match="Empty expression"):
        solution([])


def test_solution_invalid_token():
    with pytest.raises(ValueError, match="Invalid token: 'abc'"):
        solution(["abc"])


def test_solution_too_many_values_on_stack():
    with pytest.raises(ValueError, match="3 values left on stack"):
        solution(["1", "2", "3"])


def test_cli_no_args_exits_with_error():
    proc = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "expression was not written" in proc.stdout


def test_cli_error_catches_value_error():
    with patch.object(sys, "argv", ["main.py", "abc"]):
        with pytest.raises(SystemExit):
            runpy.run_path("main.py", run_name="__main__")


def test_apply_binary_index_error_coverage():
    with pytest.raises(IndexError, match="Not enough operands"):
        apply_binary([1], add)


def test_no_args_coverage():
    with patch.object(sys, "argv", ["main.py"]):
        with pytest.raises(SystemExit):
            runpy.run_path("main.py", run_name="__main__")
