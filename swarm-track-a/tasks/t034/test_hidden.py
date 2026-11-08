from solution import group_by
import pytest

def test_1():
    records = [{"a": 1}, {"a": 2}, {"a": 1}]
    assert group_by(records, "a") == {1: [{"a": 1}, {"a": 1}], 2: [{"a": 2}]}

def test_2():
    records = [{"x": 1}, {"y": 2}]
    assert group_by(records, "x") == {1: [{"x": 1}], None: [{"y": 2}]}

def test_3():
    assert group_by([], "k") == {}

def test_4():
    records = [{"a": 1}, {"a": 2}, {"a": 1}]
    result = group_by(records, "a")
    assert list(result.keys()) == [1, 2]

def test_5():
    records = [{"a": 1}, {"b": 2}, {"a": 3}, {"b": 2}]
    result = group_by(records, "b")
    assert list(result.keys()) == [2, None]
    assert result[2] == [{"b": 2}, {"b": 2}]
    assert result[None] == [{"a": 1}, {"a": 3}]
