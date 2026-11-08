from solution import anagram_groups

def test_1():
    assert anagram_groups(["eat","tea","tan","ate","nat","bat"]) == [["ate","eat","tea"],["bat"],["nat","tan"]]

def test_2():
    assert anagram_groups(["Cat","cat"]) == [["Cat"],["cat"]]

def test_3():
    assert anagram_groups([]) == []

def test_4():
    assert anagram_groups(["listen","silent","enlist","google","gogole"]) == [["enlist","listen","silent"],["google","gogole"]]

def test_5():
    assert anagram_groups(["a","b","a"]) == [["a","a"],["b"]]
