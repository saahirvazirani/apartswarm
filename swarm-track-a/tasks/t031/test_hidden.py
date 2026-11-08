from solution import levenshtein

def test_1():
    assert levenshtein("kitten", "sitting") == 3

def test_2():
    assert levenshtein("flaw", "lawn") == 2

def test_3():
    assert levenshtein("", "abc") == 3
    assert levenshtein("abc", "") == 3
    assert levenshtein("", "") == 0

def test_4():
    assert levenshtein("abc", "abc") == 0
    assert levenshtein("ABC", "abc") == 3

def test_5():
    assert levenshtein("a", "b") == 1
    assert levenshtein("ab", "ba") == 2
    assert levenshtein("sunday", "saturday") == 3
