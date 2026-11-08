from solution import top_k_words

def test_1():
    assert top_k_words("apple apple Banana, banana apple", 1) == [("apple", 3)]

def test_2():
    assert top_k_words("a b a b c", 2) == [("a", 2), ("b", 2)]

def test_3():
    assert top_k_words("Hello! hello world.", 5) == [("hello", 2), ("world", 1)]

def test_4():
    assert top_k_words("... !!! ??? ...", 3) == []

def test_5():
    assert top_k_words("zebra apple mango apple zebra banana", 3) == [
        ("apple", 2),
        ("zebra", 2),
        ("banana", 1),
    ]
