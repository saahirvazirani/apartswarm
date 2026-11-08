from solution import lcm_list
import pytest


def test_1():
    assert lcm_list([4, 6]) == 12


def test_2():
    assert lcm_list([7, 5]) == 35


def test_3():
    assert lcm_list([2, 3, 4]) == 12


def test_4():
    with pytest.raises(ValueError):
        lcm_list([])
    with pytest.raises(ValueError):
        lcm_list([1, 0, 3])
    with pytest.raises(ValueError):
        lcm_list([2, -5])


def test_5():
    assert lcm_list([1]) == 1
    assert lcm_list([6, 8, 10]) == 120
    assert lcm_list([21, 6]) == 42
    assert lcm_list([11, 13, 17]) == 11 * 13 * 17
