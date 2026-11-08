from solution import transpose
import pytest

def test_1():
    assert transpose([[1, 2], [3, 4], [5, 6]]) == [[1, 3, 5], [2, 4, 6]]

def test_2():
    assert transpose([[1, 2, 3]]) == [[1], [2], [3]]

def test_3():
    assert transpose([]) == []

def test_4():
    assert transpose([[], []]) == []

def test_5():
    with pytest.raises(ValueError):
        transpose([[1, 2], [3, 4, 5]])
