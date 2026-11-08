from solution import chunk
import pytest

def test_1():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

def test_2():
    assert chunk([], 3) == []

def test_3():
    assert chunk([1, 2], 1) == [[1], [2]]

def test_4():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

def test_5():
    with pytest.raises(ValueError):
        chunk([1, 2, 3], 0)
