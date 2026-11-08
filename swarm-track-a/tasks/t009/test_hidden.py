from solution import caesar_shift

def test_1():
    assert caesar_shift("abc", 1) == "bcd"

def test_2():
    assert caesar_shift("XYZ", 3) == "ABC"

def test_3():
    assert caesar_shift("Hello, World!", 5) == "Mjqqt, Btwqi!"

def test_4():
    assert caesar_shift("abc", -1) == "zab"
    assert caesar_shift("ABC", -3) == "XYZ"
    assert caesar_shift("Test", 26) == "Test"
    assert caesar_shift("Test", 52) == "Test"

def test_5():
    assert caesar_shift("123 !?@", 10) == "123 !?@"
    assert caesar_shift("MixCase XYZ", 30) == "QmbGewi BCD"
    assert caesar_shift("", 5) == ""
