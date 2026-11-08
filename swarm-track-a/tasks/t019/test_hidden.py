from solution import anagram_groups

def test_1():
    assert anagram_groups(["eat","tea","tan","ate","nat","bat"]) == [["ate","eat","tea"],["bat"],["nat","tan"]]

def test_2():
    assert anagram_groups(["a"]) == [["a"]]

def test_3():
    assert anagram_groups(["ab","Ba"]) == [["Ba"],["ab"]]

def test_4():
    assert anagram_groups([]) == []

def test_5():
    assert anagram_groups(["Cat","act","tac","cat"]) == [["Cat"],["act","cat","tac"]]
