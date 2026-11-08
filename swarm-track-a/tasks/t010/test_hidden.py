from solution import flatten
import pytest

def test_1():
    assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]

def test_2():
    assert flatten([[[]]]) == []

def test_3():
    assert flatten([1, (2, 3), "ab"]) == [1, (2, 3), "ab"]

def test_4():
    assert flatten([]) == []
    assert flatten([[], [[]], [[], [1]]]) == [1]

def test_5():
    with pytest.raises(TypeError):
        flatten("not a list")
