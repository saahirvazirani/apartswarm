from solution import longest_common_prefix

def test_1():
    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"

def test_2():
    assert longest_common_prefix(["dog", "racecar", "car"]) == ""

def test_3():
    assert longest_common_prefix(["interspecies", "interstellar", "interstate"]) == "inters"

def test_4():
    assert longest_common_prefix([]) == ""

def test_5():
    assert longest_common_prefix(["abc", "abc", "abc"]) == "abc"
