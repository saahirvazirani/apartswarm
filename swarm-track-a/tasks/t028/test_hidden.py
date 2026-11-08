from solution import dedupe

def test_1():
    assert dedupe([1, 2, 3, 2, 1]) == [1, 2, 3]

def test_2():
    assert dedupe(["a", "b", "a", "c"]) == ["a", "b", "c"]

def test_3():
    assert dedupe([]) == []

def test_4():
    original = [1, 2, 3, 2, 1]
    snapshot = list(original)
    result = dedupe(original)
    assert result == [1, 2, 3]
    assert original == snapshot

def test_5():
    assert dedupe([5, 5, 5, 5]) == [5]
    assert dedupe([1, 2, 3]) == [1, 2, 3]
    assert dedupe([(1, 2), (3, 4), (1, 2)]) == [(1, 2), (3, 4)]
