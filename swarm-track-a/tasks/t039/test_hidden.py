from solution import tokenize
import pytest

def test_1():
    assert tokenize("1 + 2") == ["1", "+", "2"]

def test_2():
    assert tokenize("(3.14*2)") == ["(", "3.14", "*", "2", ")"]

def test_3():
    assert tokenize("10-5") == ["10", "-", "5"]

def test_4():
    assert tokenize("  12.5  /  4  ") == ["12.5", "/", "4"]

def test_5():
    with pytest.raises(ValueError):
        tokenize("2 ^ 3")
    with pytest.raises(ValueError):
        tokenize("1..2")
    with pytest.raises(ValueError):
        tokenize("3 + .")
