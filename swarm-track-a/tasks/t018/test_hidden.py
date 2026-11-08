from solution import moving_average
import pytest

def test_1():
    assert moving_average([1.0, 2.0, 3.0, 4.0], 2) == [1.5, 2.5, 3.5]

def test_2():
    assert moving_average([5.0], 1) == [5.0]

def test_3():
    assert moving_average([1.0, 2.0, 3.0], 3) == [2.0]

def test_4():
    assert moving_average([2.0, 4.0, 6.0, 8.0, 10.0], 3) == [4.0, 6.0, 8.0]

def test_5():
    with pytest.raises(ValueError):
        moving_average([1.0, 2.0], 3)
    with pytest.raises(ValueError):
        moving_average([1.0, 2.0, 3.0], 0)
