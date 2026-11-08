from solution import caesar_shift

def test_1():
    assert caesar_shift("Abc Xyz!", 3) == "Def Abc!"

def test_2():
    assert caesar_shift("Hello", -1) == "Gdkkn"

def test_3():
    assert caesar_shift("Zz", 52) == "Zz"

def test_4():
    assert caesar_shift("a", -1) == "z"
    assert caesar_shift("A", -1) == "Z"

def test_5():
    assert caesar_shift("123 !@#", 7) == "123 !@#"
    assert caesar_shift("", 10) == ""
