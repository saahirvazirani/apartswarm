from solution import dedupe

def test_1():
    assert dedupe([1, 2, 1, 3, 2]) == [1, 2, 3]

def test_2():
    assert dedupe(["a", "b", "a"]) == ["a", "b"]

def test_3():
    assert dedupe([]) == []

def test_4():
    original = [1, 2, 3]
    dedupe(original)
    assert original == [1, 2, 3]

def test_5():
    assert dedupe([1, 1, 1, 1]) == [1]
