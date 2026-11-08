from solution import normalize

def test_1():
    assert normalize([1.0, 2.0, 3.0]) == [0.0, 0.5, 1.0]

def test_2():
    assert normalize([5.0, 5.0]) == [0.0, 0.0]

def test_3():
    assert normalize([]) == []

def test_4():
    original = [10.0, 20.0, 30.0]
    result = normalize(original)
    assert result == [0.0, 0.5, 1.0]
    assert original == [10.0, 20.0, 30.0]

def test_5():
    assert normalize([-2.0, 0.0, 2.0]) == [0.0, 0.5, 1.0]
