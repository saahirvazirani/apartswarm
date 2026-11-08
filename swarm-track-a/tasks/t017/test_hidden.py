from solution import median
import pytest

def test_1():
    assert median([3, 1, 2]) == 2.0

def test_2():
    assert median([4, 1, 3, 2]) == 2.5

def test_3():
    assert median([7]) == 7.0

def test_4():
    with pytest.raises(ValueError):
        median([])

def test_5():
    assert median([10, 2, 38, 23, 38, 23, 21]) == 23.0
