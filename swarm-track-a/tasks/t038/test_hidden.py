from solution import days_between
import pytest

def test_1():
    assert days_between('2021-01-01', '2021-01-02') == 1

def test_2():
    assert days_between('2021-12-31', '2021-01-01') == -364

def test_3():
    assert days_between('2020-02-29', '2021-02-28') == 365

def test_4():
    assert days_between('2021-05-10', '2021-05-10') == 0

def test_5():
    with pytest.raises(ValueError):
        days_between('2021-02-30', '2021-03-01')
