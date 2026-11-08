from solution import group_by

def test_1():
    records = [{"a": 1}, {"a": 2}, {"a": 1}]
    assert group_by(records, "a") == {1: [{"a": 1}, {"a": 1}], 2: [{"a": 2}]}

def test_2():
    records = [{"x": 1}, {"x": 2, "y": 3}]
    assert group_by(records, "x") == {1: [{"x": 1}], 2: [{"x": 2, "y": 3}]}

def test_3():
    records = [{"a": 1}, {"b": 2}]
    assert group_by(records, "a") == {1: [{"a": 1}], None: [{"b": 2}]}

def test_4():
    records = []
    assert group_by(records, "a") == {}

def test_5():
    records = [{"a": 1}, {"a": None}, {"b": 2}, {"a": 1}]
    assert group_by(records, "a") == {1: [{"a": 1}, {"a": 1}], None: [{"a": None}, {"b": 2}]}
