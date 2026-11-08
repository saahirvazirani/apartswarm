from solution import merge_intervals
import pytest

def test_1():
    assert merge_intervals([(1,3),(2,6),(8,10),(15,18)]) == [(1,6),(8,10),(15,18)]

def test_2():
    assert merge_intervals([(1,4),(4,5)]) == [(1,5)]

def test_3():
    assert merge_intervals([(5,6),(1,2)]) == [(1,2),(5,6)]

def test_4():
    assert merge_intervals([]) == []

def test_5():
    with pytest.raises(ValueError):
        merge_intervals([(3,1),(2,4)])
