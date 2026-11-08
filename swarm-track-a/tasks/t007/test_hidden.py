from solution import is_balanced
import pytest

def test_1():
    assert is_balanced("([]){}") is True

def test_2():
    assert is_balanced("([)]") is False

def test_3():
    assert is_balanced("(((") is False

def test_4():
    assert is_balanced("a(b)c[d]e{f}g") is True
    assert is_balanced("") is True
    assert is_balanced("no brackets here") is True

def test_5():
    assert is_balanced("([)]") is False
    assert is_balanced("{[}]") is False
    assert is_balanced(")(") is False
    assert is_balanced("]") is False
