from solution import two_sum_indices
import pytest

def test_1():
    assert two_sum_indices([2, 7, 11, 15], 9) == (0, 1)

def test_2():
    assert two_sum_indices([3, 2, 4], 6) == (1, 2)

def test_3():
    assert two_sum_indices([1, 2, 3], 10) is None

def test_4():
    assert two_sum_indices([3, 3, 4, 3], 6) == (0, 3)

def test_5():
    assert two_sum_indices([], 0) is None
